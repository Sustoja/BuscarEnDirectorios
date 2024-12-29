import os
from docx import Document
from pypdf import PdfReader

from src.helpers import logger

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() for page in reader.pages)

def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

EXTRACTORS = {
    ".docx": extract_text_from_docx,
    ".doc": extract_text_from_docx,
    ".pdf": extract_text_from_pdf,
    ".txt": extract_text_from_txt,
    ".md": extract_text_from_txt,
}

def extract_content(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    extractor = EXTRACTORS.get(ext.lower())
    if extractor:
        try:
            return extractor(file_path)
        except Exception as e:
            logger.log.warning(f"No se ha podido extraer texto de {file_path}: {e}")
    return ""
