from docling.document_converter import DocumentConverter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from utils.utils import config

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever, BM25Retriever
from typing import List, Any
import logging
import os
from dotenv import load_dotenv
import rank_bm25

load_dotenv()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Handles document conversion and splitting.
    """
    def __init__(self, headers_to_split_on_param: List[tuple[str, str]]):
        self.headers_to_split_on = headers_to_split_on_param

    def process(self, source: Any) -> List[str]:
        """
        Converts a document to markdown and splits it into chunks.

        Args:
            source (Any): The source document to process.

        Returns:
            List[str]: List of document sections split by headers.
        """
        try:
            logger.info("Starting document processing.")
            converter = DocumentConverter()
            markdown_document = converter.convert(source).document.export_to_markdown()
            markdown_splitter = MarkdownHeaderTextSplitter(self.headers_to_split_on)
            documents = markdown_splitter.split_text(markdown_document)
            logger.info("Document processed successfully.")
            return documents
        except Exception as exception:
            logger.error(f"Error processing document: {exception}")
            raise RuntimeError(f"Error processing document: {exception}")


class IndexBuilder:
    """
    Builds vector-based and BM25-based retrievers.
    """
    def __init__(self, docs_list: List[str], collection_name: str, persist_directory: str, load_documents: bool):
        self.docs_list = docs_list
        self.collection_name = collection_name
        self.vectorstore = None
        self.persist_directory = persist_directory
        self.load_documents = load_documents

    def build_vectorstore(self):
        """
        Initializes the Chroma vectorstore with the provided documents and embeddings.
        """
        embeddings = OpenAIEmbeddings()
        try:
            logger.info("Building vectorstore.")
            self.vectorstore = Chroma.from_documents(
                persist_directory=self.persist_directory,
                documents=self.docs_list,
                collection_name=self.collection_name,
                embedding=embeddings,
            )
            logger.info("Vectorstore built successfully.")
        except Exception as e:
            logger.error(f"Error building vectorstore: {e}")
            raise RuntimeError(f"Error building vectorstore: {e}")

    def build_retrievers(self):
        """
        Builds BM25 and vector-based retrievers and combines them into an ensemble retriever.

        Returns:
            EnsembleRetriever: Combined retriever using BM25 and vector-based methods.
        """
        try:
            logger.info("Building BM25 retriever.")
            bm25_retriever = BM25Retriever.from_documents(self.docs_list, search_kwargs={"k": 4})

            logger.info("Building vector-based retrievers.")
            retriever_vanilla = self.vectorstore.as_retriever(
                search_type="similarity", search_kwargs={"k": 4}
            )
            retriever_mmr = self.vectorstore.as_retriever(
                search_type="mmr", search_kwargs={"k": 4}
            )

            logger.info("Combining retrievers into an ensemble retriever.")
            ensemble_retriever = EnsembleRetriever(
                retrievers=[retriever_vanilla, retriever_mmr, bm25_retriever],
                weights=[0.3, 0.3, 0.4],
            )
            logger.info("Retrievers built successfully.")
            return ensemble_retriever
        except Exception as e:
            logger.error(f"Error building retrievers: {e}")
            raise RuntimeError(f"Error building retrievers: {e}")


if __name__ == "__main__":
    # Configuration
    headers_to_split_on = config["retriever"]["headers_to_split_on"]
    filepath = config["retriever"]["file"]
    collection_name = config["retriever"]["collection_name"]
    load_documents = config["retriever"]["load_documents"]

    print("Retriever entry")
    if load_documents:
        # Document Processing
        logger.info("Initializing document processor.")
        processor = DocumentProcessor(headers_to_split_on)  # Replace with actual source
        try:
            docs_list = processor.process(filepath)
            logger.info(f"{len(docs_list)} chunks generated.")
        except RuntimeError as e:
            logger.info(f"Failed to process document: {e}")
            exit(1)

    # Index Building
    logger.info("Initializing index builder.")
    index_builder = IndexBuilder(docs_list, collection_name, persist_directory="vector_db", load_documents=load_documents)
    index_builder.build_vectorstore()

    try:
        ensemble_retriever = index_builder.build_retrievers()
        logger.info("Index and retrievers built successfully. Ready for use.")
    except RuntimeError as e:
        logger.critical(f"Failed to build index or retrievers: {e}")
        exit(1)