from pathlib import Path

from pypdf import PdfReader


def extract_pages_from_pdf(file_path: Path) -> list[dict]:
    reader = PdfReader(str(file_path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append(
                {
                    "file": file_path.name,
                    "page": page_number,
                    "text": text.strip(),
                }
            )

    return pages


def extract_pages_from_folder(folder_path: str) -> list[dict]:
    documents_folder = Path(folder_path)

    if not documents_folder.exists():
        raise FileNotFoundError(
            f"Documents folder was not found: {folder_path}"
        )

    pdf_files = sorted(documents_folder.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files were found inside: {folder_path}"
        )

    all_pages = []

    for pdf_file in pdf_files:
        print(f"Reading {pdf_file.name}...")

        try:
            pages = extract_pages_from_pdf(pdf_file)
            all_pages.extend(pages)

            print(
                f"Extracted {len(pages)} readable pages "
                f"from {pdf_file.name}."
            )

        except Exception as error:
            print(
                f"Could not read {pdf_file.name}: {error}"
            )

    return all_pages