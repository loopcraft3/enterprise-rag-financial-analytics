from fastembed import TextEmbedding
from langchain_core.embeddings import Embeddings

from app.config import EMBEDDING_MODEL

_embedding_model = None


class FastEmbedEmbeddings(Embeddings):
    """Same BGE model as before, run with ONNX instead of PyTorch (far less RAM)."""

    def __init__(self, model_name: str):
        self._model = TextEmbedding(model_name=model_name, threads=1)

    def embed_documents(self, texts):
        return [v.tolist() for v in self._model.embed(list(texts), batch_size=32)]

    def embed_query(self, text):
        return next(iter(self._model.embed([text]))).tolist()


def get_embedding_model():
    """Loads the model once and reuses it."""
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = FastEmbedEmbeddings(EMBEDDING_MODEL)

    return _embedding_model