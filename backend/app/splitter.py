from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP
from langchain_experimental.text_splitter import SemanticChunker
from app.embeddings import get_embedding_model

def split_documents(documents):
    """
    Split documents into smaller chunks while preserving context.
    """

    embeddings = get_embedding_model()

    splitter = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=80,
    )

    chunks = splitter.split_documents(documents)  
 
    print(f"Total chunks: {len(chunks)}") 

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n----- Chunk {i+1} -----")  
        print(chunk.page_content[:500])

    total_chunks = len(chunks) 

    for index, chunk in enumerate(chunks):


        chunk.metadata["chunk_index"] = index

        chunk.metadata["total_chunks"] = total_chunks

        chunk.metadata["chunk_id"] = (
            f"{chunk.metadata.get('source')}_{index}"
        )

        chunk.metadata["token_estimate"] = (
            len(chunk.page_content) // 4
        )

    return chunks    

