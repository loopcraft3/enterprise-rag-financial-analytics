from langchain_community.document_loaders import PyPDFDirectoryLoader


def load_documents(folder_path: str):


    loader = PyPDFDirectoryLoader(folder_path)

    documents = loader.load()
      
    return documents
  

from langchain_community.document_loaders import PyPDFLoader


def load_document(file_path):
    """
    Load a single PDF document.
    """

    loader = PyPDFLoader(file_path)

    documents = loader.load()

    return documents 