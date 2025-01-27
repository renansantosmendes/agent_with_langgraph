from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class WebContentVectorRetriever:
    def __init__(self, url: str) -> None:
        self.url = url
        self.loader = WebBaseLoader(url)
        self._load_documents()
        self._start_retriever()

    def _load_documents(self):
        self._loaded_documents = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        ).split_documents(self.loader.load())
        return self._loaded_documents

    def _start_retriever(self):
        self._vector_retriever = FAISS.from_documents(self._loaded_documents,
                                                      OpenAIEmbeddings()).as_retriever()

    def get_retriever(self):
        return self._vector_retriever

    def invoke(self, query: str):
        return self._vector_retriever.invoke(query)

    def __call__(self, query: str):
        return self.invoke(query)
