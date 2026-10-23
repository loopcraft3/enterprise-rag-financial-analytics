from fastapi import FastAPI
# from app.loader import load_documents
# from app.splitter import split_documents

from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.documents import router as documents_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Custom RAG API",
    version="5.2.3",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(upload_router)
app.include_router(documents_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to Custom RAG API"
    }


# @app.get("/chunks")
# def get_chunks():

#     documents = load_documents("data/default")

#     chunks = split_documents(documents)  

#     result = []

#     for index, chunk in enumerate(chunks): 
                          
#         result.append(
#             {
#                 "chunk_number": index + 1,
#                 "source": chunk.metadata.get("source"),
#                 "page": chunk.metadata.get("page"),
#                 "characters": len(chunk.page_content),
#                 "preview": chunk.page_content[:200]
#             }   
#         )

#     return {                                
#         "total_documents": len(documents),
#         "total_chunks": len(chunks),
#         "chunks": result
#     }
