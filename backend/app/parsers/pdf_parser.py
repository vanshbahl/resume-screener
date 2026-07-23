import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts raw text from a PDF document sequentially.
    No OCR is performed in this phase.
    """
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""
