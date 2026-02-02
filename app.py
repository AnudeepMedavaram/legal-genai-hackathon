import streamlit as st
from file_loader import extract_text
from openai_client import analyze_legal_text
import spacy
import hashlib, json, os, io, re
from fpdf import FPDF
from datetime import datetime
from langdetect import detect

# --- Load spaCy model (installed via requirements.txt) ---
nlp = spacy.load("en_core_web_sm")

# --- Logging setup ---
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
    with open(os.path.join(LOG_DIR, f"{hash_val}.json"), "w") as f:
        json.dump(log_data, f, indent=2)

# --- Clause detection helpers ---
CLAUSE_KEYWORDS = {
    "Termination": ["termination", "terminate", "notice period"],
    "Payment": ["shall pay", "payment", "invoice", "INR"],
    "Confidentiality": ["confidential", "non-disclosure", "nda"],
    "Penalty": ["penalty", "fine", "late fee"]
}

RISK_KEYWORDS = {
    "High": ["unilateral termination", "indemnity unlimited", "penalty", "confidentiality breach"],
    "Medium": ["automatic renewal", "late payment fees"],
    "Low": []
}

def split_clauses(text):
    clauses = re.split(r'\n\d+\.\s', text)
    return [c.strip() for c in clauses if c.strip()]

def detect_clause_type(clause):
    for ctype, keywords in CLAUSE_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in clause.lower():
                return ctype
    return "Other"

def score_risk(clause):
    for level, keywords in RISK_KEYWORDS.items():
        if any(kw in clause.lower() for kw in keywords):
            return level
    return "Low"

# --- PDF helpers ---
def safe_pdf_text(text):
    return ''.join([c if 32 <= ord(c) <= 126 else ' ' for c in text])

def safe_multi_cell(pdf, text, height=6):
    max_width = pdf.w - pdf.l_margin - pdf.r_margin - 2
    for line in text.split("\n"):
        pdf.multi_cell(max_width, height, safe_pdf_text(line.strip()))

def create_pdf(contract_text, clauses_info, analysis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    safe_multi_cell(pdf, "GenAI Legal Assistant Report\n\n")
    pdf.set_font("Helvetica", '', 12)
    safe_multi_cell(pdf, "📜 Contract Preview:\n" + contract_text[:2000] + "...\n\n")
    safe_multi_cell(pdf, "🔹 Clauses Detected:\n")
    for c in clauses_info:
        safe_multi_cell(pdf, f"{c['id']}: [{c['type']}] {c['text'][:200]}... Risk: {c['risk']}")
    safe_multi_cell(pdf, "\n📊 Analysis Summary:\n" + analysis.get("summary",""))
    safe_multi_cell(pdf, "\n⚠️ Risks:\n" + analysis.get("risks",""))
    safe_multi_cell(pdf, "\n💡 Suggestions:\n" + analysis.get("suggestions",""))
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- Streamlit UI ---
st.set_page_config(page_title="GenAI Legal Assistant", layout="wide")
st.title("📄 GenAI-Powered Legal Assistant for SMEs")
st.write("Upload a contract file (PDF, DOCX, TXT) to analyze clauses, risks, and summary.")

uploaded_file = st.file_uploader("Upload Contract", type=["pdf","docx","txt"])

if uploaded_file:
    st.success("File uploaded successfully!")
    contract_text = extract_text(uploaded_file)

    lang = detect(contract_text)
    if lang == "hi":
        st.info("Detected Hindi → translating to English internally")
        try:
            contract_text = analyze_legal_text(f"Translate this to English:\n\n{contract_text}")["summary"]
        except:
            st.warning("Translation fallback: using original text")

    st.subheader("📜 Contract Preview")
    st.text_area("Contract Content", contract_text[:3000], height=300)

    clauses = split_clauses(contract_text)
    clauses_info = []

    st.subheader("🔹 Clauses Detected")
    for i, clause in enumerate(clauses,1):
        ctype = detect_clause_type(clause)
        risk = score_risk(clause)
        doc = nlp(clause)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        clauses_info.append({"id":str(i),"text":clause,"type":ctype,"risk":risk,"entities":entities})

        color = "red" if risk=="High" else "orange" if risk=="Medium" else "green"
        st.markdown(f"**Clause {i} [{ctype}] (Risk: {risk})**: <span style='color:{color}'>{clause[:300]}...</span>", unsafe_allow_html=True)
        if entities:
            st.markdown(f"Entities: {entities}")

    st.subheader("📊 Analysis")
    with st.spinner("Analyzing contract..."):
        analysis = analyze_legal_text(contract_text)

    with st.expander("Summary"):
        st.write(analysis.get("summary","No summary generated."))
    with st.expander("Risks"):
        st.write(analysis.get("risks","No risks detected."))
    with st.expander("Suggestions"):
        st.write(analysis.get("suggestions","No suggestions generated."))

    log_session(uploaded_file.name, contract_text, [c["risk"] for c in clauses_info])

    pdf_buffer = create_pdf(contract_text, clauses_info, analysis)
    st.download_button(
        label="📥 Download Contract Analysis PDF",
        data=pdf_buffer,
        file_name="contract_analysis.pdf",
        mime="application/pdf"
    )




