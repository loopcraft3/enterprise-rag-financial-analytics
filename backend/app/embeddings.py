# from dotenv import load_dotenv
# from langchain_openai import OpenAIEmbeddings

# load_dotenv()


# def get_embedding_model():
#     """
#     Returns the OpenAI embedding model.
#     """

#     embedding_model = OpenAIEmbeddings(
#         model="text-embedding-3-small"
#     )

#     return embedding_model 



from langchain_huggingface import HuggingFaceEmbeddings
from app.config import EMBEDDING_MODEL

_embedding_model = None


def get_embedding_model():
    """
    Returns the Hugging Face embedding model.
    Loads weights only once and reuses the cached instance.
    """
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL, 
            model_kwargs={
                "device": "cpu"
            },
            encode_kwargs={
                "normalize_embeddings": True
            }
        )

    return _embedding_model