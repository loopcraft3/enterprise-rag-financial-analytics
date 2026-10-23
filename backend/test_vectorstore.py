from app.embeddings import get_embedding_model
from app.vectorstore import add_documents, vector_search
from langchain_core.documents import Document


# Create a small test document
test_document = Document(
    page_content="India is a country in South Asia.",
    metadata={
        "source": "test_document.pdf",
        "page": 1,
        "chunk_index": 0,
    },
)

# Load embedding model
embedding_model = get_embedding_model()

# Insert into PostgreSQL
add_documents(
    chunks=[test_document],
    embedding_model=embedding_model,
)

# Search PostgreSQL using pgvector
results = vector_search(
    question="Which country is in South Asia?",
    embedding_model=embedding_model,
    k=1,
)

print("\n🔎 Search result:")

for document, score in results:
    print(f"Score: {score:.4f}")
    print(f"Content: {document.page_content}")