"""
PDF Utilities Module

Handles PDF text extraction using PyPDF.
"""
from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract text content from an uploaded PDF file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Extracted text, or error message starting with 'ERROR_READING_PDF:'
    """
    try:
        reader = PdfReader(uploaded_file)
        parts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                parts.append(t)
        return "\n".join(parts).strip()
    except Exception as e:
        return f"ERROR_READING_PDF: {e}"