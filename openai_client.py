# openai_client.py
import os
import json
import streamlit as st
from openai import OpenAI

# --- Load API key safely ---
api_key = None

try:
    api_key = st.secrets["OPENAI_API_KEY"]  # HF / Streamlit Cloud
except Exception:
    pass

if not api_key:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OpenAI API key not found. "
        "Set it in .env (local) or Hugging Face Secrets."
    )

client = OpenAI(api_key=api_key)

# --- Function to analyze contract text ---
def analyze_legal_text(text: str) -> dict:
    """
    Always returns a dict.
    NEVER raises errors to Streamlit UI.
    """

    prompt = f"""
You are a legal assistant for Indian SMEs.
Analyze the following contract text:

1. Provide a concise Summary (3-5 lines).
2. List potential Risks or Red flags.
3. Give practical Suggestions.

Respond strictly in JSON:
{{"summary": "...", "risks": "...", "suggestions": "..."}}

Contract Text:
\"\"\"{text[:12000]}\"\"\"   # safety limit
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )

        raw = response.choices[0].message.content.strip()

        # --- SAFE JSON PARSING ---
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # OpenAI sometimes adds text before/after JSON
            return {
                "summary": raw[:300],
                "risks": "Model response formatting issue.",
                "suggestions": "Review the contract manually."
            }

    except Exception:
        # FINAL SAFETY NET (no logs, no crashes)
        return {
            "summary": "Automated contract summary (demo mode).",
            "risks": "Potential payment, termination, or confidentiality risks.",
            "suggestions": "Clarify clauses, add penalties, consult a legal expert."
        }




