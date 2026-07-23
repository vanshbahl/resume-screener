import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import numpy as np
import cv2

# Initialize PaddleOCR globally to avoid loading it on every call.
# Use use_angle_cls=True to automatically rotate skewed images.
# show_log=False prevents paddleocr from spamming the console.
try:
    ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
except Exception as e:
    print(f"Warning: Failed to initialize PaddleOCR. Fallback OCR will not work. Error: {e}")
    ocr = None

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF document.
    First tries PyMuPDF text extraction.
    If the extracted text is too short (likely a scanned image), falls back to PaddleOCR.
    """
    doc = fitz.open(file_path)
    text_content = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text").strip()
        text_content.append(text)
        
    full_text = "\n".join(text_content).strip()
    
    # Heuristic: If the PDF has very little text compared to its size or number of pages,
    # it might be a scanned document. We use a simple length threshold here.
    if len(full_text) < 50 and ocr is not None:
        print(f"Text too sparse in {file_path}, falling back to OCR...")
        full_text = extract_text_with_ocr(file_path, doc)
        
    return full_text

def extract_text_with_ocr(file_path: str, doc: fitz.Document) -> str:
    """
    Renders PDF pages to images and uses PaddleOCR to extract text.
    """
    extracted_text = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Render page to an image (pixmap)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x scale for better OCR
        
        # Convert PyMuPDF pixmap to numpy array for PaddleOCR
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        
        # If image has alpha channel, convert to BGR (PaddleOCR expects BGR/RGB)
        if pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # Run OCR
        result = ocr.ocr(img, cls=True)
        
        # Parse result
        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                extracted_text.append(text)
                
    return "\n".join(extracted_text)
