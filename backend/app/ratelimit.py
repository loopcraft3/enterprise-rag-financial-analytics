"""Simple in-memory rate limits so strangers cannot burn the free Groq quota.

Limits are per visitor (IP address), plus one daily cap for the whole site.
All numbers can be changed with environment variables on Render.
The counters live in memory, so they reset when the server restarts.
"""

import os
import time
from collections import defaultdict, deque
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# path -> (max requests, window in seconds), per visitor
RATE_LIMITS = {
    "/chat": (int(os.getenv("CHAT_LIMIT_PER_MIN", "6")), 60),
    "/upload": (int(os.getenv("UPLOAD_LIMIT_PER_HOUR", "5")), 3600),
}

# Total chat requests per day, all visitors together. 0 = no daily cap.
DAILY_CHAT_CAP = int(os.getenv("DAILY_CHAT_CAP", "300"))

_hits = defaultdict(deque)          # (ip, path) -> timestamps of recent requests
_daily = {"day": None, "count": 0}  # shared daily counter


def client_ip(request: Request) -> str:
    # Render puts the real visitor address in X-Forwarded-For.
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _too_many(message: str, retry_after: int) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": message},
        headers={"Retry-After": str(max(1, retry_after))},
    )


def _cleanup(now: float) -> None:
    """Drop visitors that have gone quiet, so memory does not grow forever."""
    longest = max(window for _, window in RATE_LIMITS.values())
    for key in [k for k, dq in _hits.items() if not dq or now - dq[-1] > longest]:
        del _hits[key]


def reset_state() -> None:
    """Used by tests."""
    _hits.clear()
    _daily.update({"day": None, "count": 0})


def install_rate_limit(app: FastAPI) -> None:
    """Call this BEFORE app.add_middleware(CORSMiddleware, ...).

    The last middleware added is the outermost one. CORS must be outermost,
    otherwise the 429 reply has no CORS headers and the browser shows a
    confusing CORS error instead of our message.
    """

    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        rule = RATE_LIMITS.get(request.url.path)

        if request.method != "POST" or rule is None:
            return await call_next(request)

        now = time.time()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if _daily["day"] != today:
            _daily.update({"day": today, "count": 0})

        if request.url.path == "/chat" and DAILY_CHAT_CAP > 0 and _daily["count"] >= DAILY_CHAT_CAP:
            return _too_many(
                "This free demo has reached its daily question limit. Please try again tomorrow.",
                3600,
            )

        limit, window = rule
        dq = _hits[(client_ip(request), request.url.path)]

        while dq and now - dq[0] > window:
            dq.popleft()

        if len(dq) >= limit:
            wait = int(window - (now - dq[0])) + 1
            what = "questions" if request.url.path == "/chat" else "uploads"
            return _too_many(
                f"Too many {what}. Please wait {wait} seconds and try again.",
                wait,
            )

        dq.append(now)

        if request.url.path == "/chat":
            _daily["count"] += 1

        if len(_hits) > 5000:
            _cleanup(now)

        return await call_next(request)