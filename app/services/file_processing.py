import os
import re
from typing import List
import pymupdf  # 'import fitz' replaced with 'pymupdf' to clear deprecation warning
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None


def save_upload_file(upload_file, destination_dir: str = "uploads") -> str:
    """Saves the uploaded file to disk and returns its file path."""
    os.makedirs(destination_dir, exist_ok=True)
    file_path = os.path.join(destination_dir, upload_file.filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
        
    return file_path


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text from a PDF file using updated PyMuPDF API."""
    extracted_text = []
    
    # Using pymupdf.open instead of fitz.open
    with pymupdf.open(pdf_path) as doc:
        for page in doc:
            text = page.get_text()
            if text:
                extracted_text.append(text)
                
    return "\n".join(extracted_text)


def extract_text_from_image(image_path: str) -> str:
    """Extracts text from an image file using OCR (Tesseract)."""
    if not pytesseract:
        raise RuntimeError("pytesseract is not installed or configured on the system.")
        
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


def detect_questions(text: str) -> List[str]:
    """Splits raw extracted text into individual questions based on common numbering patterns."""
    if not text:
        return []

    # Matches question formats like: 1., Q1., Question 1:, 1), etc.
    pattern = r'(?:\n|\A)(?:Q(?:uestion)?\s*\d+[\.:\)]|\d+[\.\)])\s*'
    
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    
    # Filter empty/short fragments
    questions = [q.strip() for q in parts if len(q.strip()) > 10]
    
    # Fallback if pattern matching doesn't find distinct splits
    if not questions and text.strip():
        questions = [text.strip()]
        
    return questions