"""Run Hisaab's evaluation against a running backend and print a report.

What it does
  1. Starts a fresh private session (a random UUID, like the website does).
  2. Uploads the PDF named in questions.json.
  3. Asks every question and checks:
       - Answer     : the answer contains one of the expected values
       - Citation   : the sources include the expected file and page (pages are 1-based)
       - Refusal    : questions NOT in the document get the "couldn't find" reply
  4. Prints a table and the average response time. Use --json to save details.
  5. Deletes the session's files when it finishes.

Usage
  python eval/run_eval.py --pdf path/to/apple_10q.pdf
  python eval/run_eval.py --pdf apple.pdf --api https://your-backend.onrender.com --json eval/last_run.json

The backend limits chats to 6 per minute, so the script waits between questions.
Run it against your own local backend, not the public demo, if you can.
"""
import argparse
import json
import re
import sys
import time
import uuid
from pathlib import Path

import httpx

HERE = Path(__file__).parent
REFUSAL = "couldn't find the answer"


def norm(text: str) -> str:
    """Lower-case and drop commas, spaces and currency marks so '1,23,456' matches '123456'."""
    return re.sub(r"[,\s$₹]", "", text.lower())


def answer_ok(answer: str, expected: list[str]) -> bool:
    a = norm(answer)
    return any(norm(e) in a for e in expected)


def citation_ok(sources: list[dict], file: str | None, page: int | None) -> bool:
    for s in sources:
        file_match = file is None or Path(s.get("source", "")).name.lower() == file.lower()
        page_match = page is None or s.get("page") == page
        if file_match and page_match:
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", required=True, help="PDF the questions are about")
    ap.add_argument("--questions", default=str(HERE / "questions.json"))
    ap.add_argument("--api", default="http://127.0.0.1:8000")
    ap.add_argument("--json", help="save per-question results to this file")
    ap.add_argument("--pause", type=float, default=11.0, help="seconds between questions (rate limit)")
    args = ap.parse_args()

    items = json.loads(Path(args.questions).read_text(encoding="utf-8"))
    if any(i.get("TODO") for i in items):
        print("questions.json still has TODO entries. Replace them with real questions first.")
        return 2

    pdf = Path(args.pdf)
    headers = {"X-Session-Id": str(uuid.uuid4())}
    results = []

    with httpx.Client(base_url=args.api, headers=headers, timeout=300) as client:
        print(f"Uploading {pdf.name} ...")
        r = client.post("/upload", files={"file": (pdf.name, pdf.read_bytes(), "application/pdf")})
        r.raise_for_status()

        try:
            for n, item in enumerate(items, 1):
                start = time.time()
                resp = client.post("/chat", json={"question": item["question"]})
                took = time.time() - start
                resp.raise_for_status()
                data = resp.json()
                answer, sources = data["answer"], data["sources"]

                if item.get("answerable", True):
                    a = answer_ok(answer, item["expect"])
                    c = citation_ok(sources, item.get("file", pdf.name), item.get("page"))
                    results.append({"id": item["id"], "kind": "answerable", "answer_ok": a, "citation_ok": c, "seconds": took, "answer": answer})
                    print(f"[{n:>2}/{len(items)}] {'PASS' if a else 'FAIL'} answer, {'PASS' if c else 'FAIL'} citation, {took:4.1f}s  {item['question'][:60]}")
                else:
                    ok = REFUSAL in answer.lower()
                    results.append({"id": item["id"], "kind": "refusal", "refused_ok": ok, "seconds": took, "answer": answer})
                    print(f"[{n:>2}/{len(items)}] {'PASS' if ok else 'FAIL'} refusal, {took:4.1f}s  {item['question'][:60]}")

                if n < len(items):
                    time.sleep(args.pause)
        finally:
            client.delete("/session")  # leave nothing behind

    ans = [r for r in results if r["kind"] == "answerable"]
    ref = [r for r in results if r["kind"] == "refusal"]
    pct = lambda k, rows: f"{sum(r[k] for r in rows)}/{len(rows)}" if rows else "n/a"
    avg = sum(r["seconds"] for r in results) / len(results)

    print("\n| Check | Result |\n|---|---|")
    print(f"| Answers correct | {pct('answer_ok', ans)} |")
    print(f"| Citations correct (file + page) | {pct('citation_ok', ans)} |")
    print(f"| Out-of-document questions refused | {pct('refused_ok', ref)} |")
    print(f"| Average response time | {avg:.1f} s |")

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
