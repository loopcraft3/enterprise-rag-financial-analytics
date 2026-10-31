import re

from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.embeddings import get_embedding_model

GSTIN_RE = re.compile(r"\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b")
TAN_RE = re.compile(r"\b[A-Z]{4}\d{5}[A-Z]\b")
YEAR_RE = re.compile(
    r"(?:A\.?Y\.?|F\.?Y\.?|Assessment Year|Financial Year)\s*[:\-]?\s*(20\d{2}\s*-\s*\d{2,4})",
    re.I,
)

DOC_SIGNATURES = {
    "gst_invoice": ["tax invoice", "gstin", "hsn", "cgst", "sgst", "igst",
                    "place of supply", "invoice no"],
    "form16": ["form no. 16", "form 16", "certificate under section 203", "tds",
               "tan of the deductor", "assessment year", "part a", "part b", "section 192"],
    "financial_statement": ["balance sheet", "statement of profit and loss", "total assets",
                            "equity and liabilities", "shareholders' funds",
                            "cash flow", "schedule iii", "statements of operations",
                            "statements of cash flows", "total liabilities", "consolidated"],
}
STRUCTURED_TYPES = {"gst_invoice", "form16"}

_structured_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1800, chunk_overlap=250, separators=["\n\n", "\n", " ", ""]
)
_cap_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
)


def clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)  # keep newlines: they preserve table rows
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def detect_doc_type(text: str) -> str:
    t = text.lower().replace("\u2019", "'")
    scores = {
        name: sum(1 for k in kws if re.search(r"\b" + re.escape(k) + r"\b", t))
        for name, kws in DOC_SIGNATURES.items()
    }
    best, score = max(scores.items(), key=lambda kv: kv[1])
    return best if score >= 3 else "general"


def extract_metadata(text: str) -> dict:
    meta = {}
    gstins = sorted(set(GSTIN_RE.findall(text)))
    tans = sorted(set(TAN_RE.findall(text)))
    years = sorted({re.sub(r"\s+", "", y) for y in YEAR_RE.findall(text)})
    if gstins:
        meta["gstins"] = ",".join(gstins[:5])
    if tans:
        meta["tans"] = ",".join(tans[:5])
    if years:
        meta["fiscal_years"] = ",".join(years[:3])
    return meta


def _cap_large(chunks, max_chars=2000):
    out = []
    for c in chunks:
        if len(c.page_content) > max_chars:
            out.extend(_cap_splitter.split_documents([c]))
        else:
            out.append(c)
    return out


def _merge_small(chunks, min_chars=200):
    merged = []
    for c in chunks:
        same_page = merged and merged[-1].metadata.get("page") == c.metadata.get("page")
        if same_page and len(c.page_content) < min_chars:
            merged[-1].page_content += "\n" + c.page_content
        else:
            merged.append(c)
    return merged


def split_documents(documents):
    """
    Split PDF pages into chunks. Chunking strategy depends on document type.
    """
    by_source = {}
    for doc in documents:
        by_source.setdefault(doc.metadata.get("source", "unknown"), []).append(doc)

    embeddings = get_embedding_model()
    semantic = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=80,
    )

    all_chunks = []
    for source, pages in by_source.items():
        for p in pages:
            p.page_content = clean_text(p.page_content)
        pages = [p for p in pages if p.page_content]
        if not pages:
            continue
        pages.sort(key=lambda p: p.metadata.get("page", 0))

        doc_type = detect_doc_type("\n".join(p.page_content for p in pages[:5]))
        extra = extract_metadata("\n".join(p.page_content for p in pages))

        if doc_type in STRUCTURED_TYPES:
            chunks = _structured_splitter.split_documents(pages)
        else:
            chunks = _merge_small(_cap_large(semantic.split_documents(pages)))

        total = len(chunks)
        for i, chunk in enumerate(chunks):
            chunk.metadata.update(extra)
            chunk.metadata["doc_type"] = doc_type
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = total
            chunk.metadata["chunk_id"] = f"{source}_{i}"
            chunk.metadata["token_estimate"] = len(chunk.page_content) // 4

        print(f"{source}: type={doc_type}, chunks={total}")
        all_chunks.extend(chunks)

    return all_chunks