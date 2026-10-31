import time
from app.cache import AnswerCache, normalize_question, make_key, is_cacheable


def test_normalization_matches_variants():
    assert normalize_question("  What was Net Income?? ") == normalize_question("what was net income")


def test_key_changes_with_corpus_and_prompt():
    a = make_key("net income", "3-10", "prompt v1")
    assert a != make_key("net income", "4-11", "prompt v1")
    assert a != make_key("net income", "3-10", "prompt v2")


def test_ttl_expiry():
    c = AnswerCache(ttl_seconds=0.05)
    c.set("k", "v")
    assert c.get("k") == "v"
    time.sleep(0.1)
    assert c.get("k") is None


def test_lru_eviction():
    c = AnswerCache(max_entries=2)
    c.set("a", 1); c.set("b", 2); c.get("a"); c.set("c", 3)
    assert c.get("b") is None and c.get("a") == 1


def test_followups_not_cached():
    convo = [{"role": "user"}, {"role": "assistant"}, {"role": "user"}]
    assert not is_cacheable("what about the previous year", convo)
    assert is_cacheable("what was the gross margin percentage this quarter", convo)