import hashlib
import re
import threading
import time
from collections import OrderedDict

FOLLOW_UP_WORDS = {
    "it", "its", "that", "this", "those", "these", "they", "them",
    "previous", "above", "earlier", "same", "next", "continue",
    "done", "again", "more",
}


class AnswerCache:
    """Thread-safe in-memory cache with LRU eviction and a time-to-live."""

    def __init__(self, max_entries: int = 500, ttl_seconds: float = 24 * 60 * 60):
        self._data = OrderedDict()
        self._lock = threading.Lock()
        self.max_entries = max_entries
        self.ttl = ttl_seconds
        self.hits = 0
        self.misses = 0

    def get(self, key):
        now = time.time()
        with self._lock:
            item = self._data.get(key)
            if item is None:
                self.misses += 1
                return None
            value, expires_at = item
            if expires_at < now:
                del self._data[key]
                self.misses += 1
                return None
            self._data.move_to_end(key)
            self.hits += 1
            return value

    def set(self, key, value):
        with self._lock:
            self._data[key] = (value, time.time() + self.ttl)
            self._data.move_to_end(key)
            while len(self._data) > self.max_entries:
                self._data.popitem(last=False)

    def clear(self):
        with self._lock:
            self._data.clear()

    def stats(self):
        with self._lock:
            return {"entries": len(self._data), "hits": self.hits, "misses": self.misses}


def normalize_question(question: str) -> str:
    q = re.sub(r"\s+", " ", question.lower().strip())
    return q.rstrip("?.! ")


def make_key(question: str, corpus_fingerprint: str, prompt_text: str) -> str:
    prompt_hash = hashlib.sha256(prompt_text.encode()).hexdigest()[:8]
    raw = f"{normalize_question(question)}|{corpus_fingerprint}|{prompt_hash}"
    return hashlib.sha256(raw.encode()).hexdigest()


EMPTY_CORPUS = "empty"


def corpus_fingerprint(session_id: str):
    """
    A hash of everything this session has uploaded (file names and chunk text).

    - Changes when a document is added or removed, so old answers are never reused.
    - Two sessions that uploaded the same file get the same fingerprint, so the
      second one can reuse the first one's cached answers (the answer only
      depends on the document, not on who asked).
    - EMPTY_CORPUS when the session has no documents; None if the database
      could not be reached.
    """
    try:
        from app.vectorstore import get_connection

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select md5(string_agg(
                        d.filename || ':' || c.chunk_index::text || ':' || c.content,
                        E'\\n' order by d.filename, c.chunk_index
                    ))
                    from public.chunks c
                    join public.documents d on d.id = c.document_id
                    where d.session_id = %s
                    """,
                    (session_id,),
                )
                (digest,) = cur.fetchone()
        return digest or EMPTY_CORPUS
    except Exception as e:
        print("Cache fingerprint failed, skipping cache:", repr(e))
        return None


def is_cacheable(question: str, conversation) -> bool:
    user_turns = sum(1 for m in conversation if m["role"] == "user")
    if user_turns <= 1:
        return True
    words = re.findall(r"[a-z']+", question.lower())
    return len(words) >= 5 and not (set(words) & FOLLOW_UP_WORDS)


answer_cache = AnswerCache()