from langchain_core.documents import Document

import app.splitter as splitter
from app.splitter import clean_text, detect_doc_type, extract_metadata

INVOICE = """TAX INVOICE
Invoice No: 42  GSTIN: 27AABCU9603R1ZM
HSN 9983  CGST 9%  SGST 9%  Place of supply: Maharashtra"""

FORM16 = """FORM NO. 16  Certificate under section 203 of the Income-tax Act
TAN of the Deductor: PNEA12345B   Assessment Year: 2025-26
Part A  Part B  TDS Section 192"""

STATEMENT = """Consolidated Balance Sheet
Total assets  Total liabilities  Equity and liabilities
Statement of Profit and Loss"""


def test_detects_gst_invoice():
    assert detect_doc_type(INVOICE) == "gst_invoice"


def test_detects_form16():
    assert detect_doc_type(FORM16) == "form16"


def test_detects_financial_statement():
    assert detect_doc_type(STATEMENT) == "financial_statement"


def test_plain_text_is_general():
    assert detect_doc_type("Meeting notes about the office picnic.") == "general"


def test_extracts_gstin_tan_and_year():
    meta = extract_metadata(INVOICE + "\n" + FORM16)
    assert meta["gstins"] == "27AABCU9603R1ZM"
    assert meta["tans"] == "PNEA12345B"
    assert meta["fiscal_years"] == "2025-26"


def test_no_metadata_when_nothing_matches():
    assert extract_metadata("hello world") == {}


def test_clean_text_keeps_rows_but_removes_extra_blank_lines():
    cleaned = clean_text("a    b\n\n\n\n\nrow2")
    assert cleaned == "a b\n\nrow2"


def test_invoice_chunks_carry_type_and_metadata(monkeypatch):
    # An invoice uses the plain splitter, so the embedding model must not be needed.
    monkeypatch.setattr(splitter, "get_embedding_model", lambda: None)
    monkeypatch.setattr(splitter, "SemanticChunker", lambda **kw: None)

    pages = [Document(page_content=INVOICE, metadata={"source": "inv.pdf", "page": 0})]
    chunks = splitter.split_documents(pages)

    assert chunks, "expected at least one chunk"
    assert all(c.metadata["doc_type"] == "gst_invoice" for c in chunks)
    assert all(c.metadata["gstins"] == "27AABCU9603R1ZM" for c in chunks)
    assert chunks[0].metadata["chunk_id"] == "inv.pdf_0"
