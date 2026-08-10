from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

    def load_pdf(
        self,
        file_path: Path,
    ) -> list[Document]:
        loader = PyPDFLoader(str(file_path))

        documents = loader.load()

        return documents

    def split_documents(
        self,
        documents: list[Document],
    ) -> list[Document]:
        chunks = self.text_splitter.split_documents(
            documents,
        )

        return chunks


document_service = DocumentService()