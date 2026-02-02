# file_loader.py
from io import BytesIO
import docx2txt
from PyPDF2 import PdfReader

def extract_text(uploaded_file) -> str:
    """Extract text from PDF, DOCX, or TXT files. Always returns string."""
    file_type = uploaded_file.type
    try:
        if "pdf" in file_type:
            pdf_reader = PdfReader(BytesIO(uploaded_file.read()))
            text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
            return text
        elif "word" in file_type or uploaded_file.name.endswith(".docx"):
            uploaded_file.seek(0)
            text = docx2txt.process(uploaded_file)
            return text
        elif "text" in file_type or uploaded_file.name.endswith(".txt"):
            uploaded_file.seek(0)
            return uploaded_file.read().decode("utf-8")
        else:
            return ""
    except Exception as e:
        print(f"[Warning] Failed to extract text: {e}")
        return ""
