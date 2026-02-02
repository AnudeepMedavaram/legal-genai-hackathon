# app.py
import streamlit as st
from file_loader import extract_text
from openai_client import analyze_legal_text
import re
from fpdf import FPDF
import io
from langdetect import detect
import spacy
import hashlib
import os
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Clause splitting
def split_clauses(text: str):
    clauses = re.split(r'\n\d+\.\s', text)
    clauses = [c.strip() for c in clauses if c.strip()]
    return clauses

# Clause type detection
CLAUSE_KEYWORDS = {
    "Termination": ["termination", "terminate", "notice period"],
    "Payment": ["shall pay", "payment", "invoice", "INR"],
    "Confidentiality": ["confidential", "non-disclosure", "nda"],
    "Penalty": ["penalty", "fine", "late fee"]
}

def detect_clause_type(clause):
    for ctype, keywords in CLAUSE_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in clause.lower():
                return ctype
    return "Other"

# Risk scoring
RISK_KEYWORDS = {
    "High": ["unilateral termination", "indemnity unlimited", "penalty", "confidentiality breach"],
    "Medium": ["automatic renewal", "late payment fees"],
    "Low": []
}

def score_risk(clause):
    clause_lower = clause.lower()
    for level, keywords in RISK_KEYWORDS.items():
        if any(kw in clause_lower for kw in keywords):
            return level
    return "Low"

# Audit logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_session(file_name, contract_text, risk_summary):
    hash_val = hashlib.sha256(contract_text.encode()).hexdigest()
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "file_name": file_name,
        "file_hash": hash_val,
        "risk_score": risk_summary
    }
    log_file = os.path.join(LOG_DIR, f"{hash_val}.json")
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)

# Safe PDF helpers
def safe_pdf_text(text):
    return ''.join([c if 32 <= ord(c) <= 126 else ' ' for c in text])

def safe_multi_cell(pdf, text, height=6):
    text = safe_pdf_text(text)
    max_width = pdf.w - pdf.l_margin - pdf.r_margin - 2
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            pdf.multi_cell(max_width, height, "")
            continue
        words = line.split(" ")
        current_line = ""
        for word in words:
            if pdf.get_string_width(current_line + " " + word) > max_width:
                if current_line:
                    pdf.multi_cell(max_width, height, current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
        if current_line:
            pdf.multi_cell(max_width, height, current_line)

def create_pdf(contract_text, clauses_info, analysis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    safe_multi_cell(pdf, "GenAI Legal Assistant Report\n\n")
    pdf.set_font("Helvetica", '', 12)
    safe_multi_cell(pdf, "📜 Contract Preview:\n" + safe_pdf_text(contract_text[:2000]) + "...\n\n")
    safe_multi_cell(pdf, "🔹 Clauses Detected:\n")
    for c in clauses_info:
        clause_text = safe_pdf_text(c['text'][:200])
        safe_multi_cell(pdf, f"{c['id']}: [{c['type']}] {clause_text}... Risk: {c['risk']}\n")
    safe_multi_cell(pdf, "\n📊 Analysis Summary:\n" + safe_pdf_text(analysis.get("summary", "")) + "\n")
    safe_multi_cell(pdf, "\n⚠️ Risks:\n" + safe_pdf_text(analysis.get("risks", "")) + "\n")
    safe_multi_cell(pdf, "\n💡 Suggestions:\n" + safe_pdf_text(analysis.get("suggestions", "")) + "\n")
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- Streamlit UI ---
st.set_page_config(page_title="GenAI Legal Assistant", layout="wide")
st.title("📄 GenAI-Powered Legal Assistant for SMEs")
st.write("Upload a contract file (PDF, DOCX, TXT) to analyze clauses, risks, and summary.")

uploaded_file = st.file_uploader("Upload Contract", type=["pdf", "docx", "txt"])

if uploaded_file:
    st.success("File uploaded successfully!")
    contract_text = extract_text(uploaded_file)
    lang = detect(contract_text)
    if lang == "hi":
        st.info("Detected language: Hindi → Translating to English internally")
        try:
            contract_text = analyze_legal_text(f"Translate this to English:\n\n{contract_text}")["summary"]
        except:
            st.warning("Translation fallback: using original text")

    st.subheader("📜 Contract Preview")
    st.text_area("Contract Content", contract_text[:3000], height=300)

    clauses = split_clauses(contract_text)
    clauses_info = []
    st.subheader("🔹 Clauses Detected")
    for i, clause in enumerate(clauses, 1):
        ctype = detect_clause_type(clause)
        risk = score_risk(clause)
        doc = nlp(clause)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        clauses_info.append({"id": str(i), "text": clause, "type": ctype, "risk": risk, "entities": entities})
        color = "red" if risk=="High" else "orange" if risk=="Medium" else "green"
        st.markdown(f"**Clause {i} [{ctype}] (Risk: {risk})**: <span style='color:{color}'>{clause[:300]}...</span>", unsafe_allow_html=True)
        if entities:
            st.markdown(f"Entities: {entities}")

    st.subheader("📊 Analysis")
    with st.spinner("Analyzing contract..."):
        analysis = analyze_legal_text(contract_text)
    with st.expander("Summary"):
        st.write(analysis.get("summary", "No summary generated."))
    with st.expander("Risks"):
        st.write(analysis.get("risks", "No risks detected."))
    with st.expander("Suggestions"):
        st.write(analysis.get("suggestions", "No suggestions generated."))

    log_session(uploaded_file.name, contract_text, [c["risk"] for c in clauses_info])

    pdf_buffer = create_pdf(contract_text, clauses_info, analysis)
    st.download_button(
        label="📥 Download Contract Analysis PDF",
        data=pdf_buffer,
        file_name="contract_analysis.pdf",
        mime="application/pdf"
    )



