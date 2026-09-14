import fitz  # PyMuPDF
from typing import List, Dict, Any

class DocumentParser:
    """Extracts text, metadata, and page numbers from PDF files."""

    @staticmethod
    def parse_pdf(file_path: str) -> List[Dict[str, Any]]:
        pages_data = []
        doc = fitz.open(file_path)
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    pages_data.append({
                        "page_number": page_num + 1,
                        "text": text.strip()
                    })
        finally:
            doc.close()
        return pages_data
