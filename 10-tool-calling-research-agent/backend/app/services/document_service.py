from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

    async def load_and_split(self, file_path: Path):
        loader = PyPDFLoader(str(file_path))

        documents = await loader.aload()

        return self.text_splitter.split_documents(documents)


document_service = DocumentService()