from pathlib import Path

from pypdf import PdfReader


class TextExtractionService:
    def extract_text(self, file_path: Path) -> str:
        extension = file_path.suffix.lower()

        if extension == ".pdf":
            return self._extract_pdf(file_path)

        if extension == ".txt":
            return file_path.read_text(encoding="utf-8")

        raise ValueError("Unsupported file type")

    def _extract_pdf(self, file_path: Path) -> str:
        reader = PdfReader(file_path)

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n\n".join(pages)