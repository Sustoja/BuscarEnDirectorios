import os
from docx import Document
from pypdf import PdfReader
from typing import Callable


DOCU_EXTENSIONS = ('.docx', '.pdf')
TEXT_EXTENSIONS = ('.txt', '.md')
VALID_EXTENSIONS = DOCU_EXTENSIONS + TEXT_EXTENSIONS

def _extract_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

def _extract_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() for page in reader.pages)

def _extract_from_text(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()

def _get_extractor(extension: str) -> Callable[[str], str]:
    extension = f".{extension.lower().lstrip('.')}"

    extractors = {
        ".docx": _extract_from_docx,
        ".pdf": _extract_from_pdf,
    }

    # Añadimos una misma función para todas las extensiones que representan fichero de texto plano
    for doctype in TEXT_EXTENSIONS:
        extractors.update({doctype:_extract_from_text})

    return extractors.get(extension, None)

def extract_content(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    extractor_func =_get_extractor(ext)

    if not extractor_func:
        raise ValueError(f"No se admiten fichero con extensión '{ext}'.")

    try:
        return extractor_func(file_path)
    except Exception as e:
        raise ValueError(f"Error al extraer texto de {file_path}: {e}")
