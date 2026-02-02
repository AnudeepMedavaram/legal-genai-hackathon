# file_loader.py
from io import BytesIO
import docx2txt
from PyPDF2 import PdfReader

def extract_text(uploaded_file) -> str:
    """Extract text from PDF, DOCX, or TXT files. Always returns a string."""
    try:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name.lower()
        file_type = uploaded_file.type or ""

        # ---- PDF ----
        if "pdf" in file_type or file_name.endswith(".pdf"):
            reader = PdfReader(BytesIO(file_bytes))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text.strip()

        # ---- DOCX ----
        elif "word" in file_type or file_name.endswith(".docx"):
            text = docx2txt.process(BytesIO(file_bytes))
            return text.strip()

        # ---- TXT ----
        elif "text" in file_type or file_name.endswith(".txt"):
            return file_bytes.decode("utf-8", errors="ignore").strip()

        return ""

    except Exception as e:
        print(f"[Warning] Failed to extract text: {e}")
        return ""

