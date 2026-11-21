from langchain_core.documents import Document

from app.rrf import reciprocal_rank_fusion


def doc(text):
    return Document(page_content=text)


def test_document_found_by_both_rankings_comes_first():
    vector = [(doc("a"), 0.9), (doc("b"), 0.8), (doc("c"), 0.7)]
    keyword = [(doc("b"), 5.0), (doc("d"), 4.0)]

    result = reciprocal_rank_fusion(vector, keyword)

    assert result[0].page_content == "b"


def test_no_duplicates_and_all_documents_kept():
    vector = [(doc("a"), 1), (doc("b"), 1)]
    keyword = [(doc("b"), 1), (doc("c"), 1)]

    result = [d.page_content for d in reciprocal_rank_fusion(vector, keyword)]

    assert sorted(result) == ["a", "b", "c"]


def test_empty_rankings_give_empty_result():
    assert reciprocal_rank_fusion([], []) == []
