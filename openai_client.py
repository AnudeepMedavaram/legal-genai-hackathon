# openai_client.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

load_dotenv()  # Load .env for local dev

# --- Safe way to get API key ---
api_key = None

try:
    # Try Streamlit Cloud secrets
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass  # ignore if running locally

# Fallback to .env key
if not api_key:
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OpenAI API key not found! "
        "Set it in .env (local) or secrets.toml (Streamlit Cloud)"
    )

client = OpenAI(api_key=api_key)

def analyze_legal_text(text: str) -> dict:
    """Analyze contract text via OpenAI. Returns a dict always."""
    prompt = f"""
You are a legal assistant for Indian SMEs.
Analyze the following contract text:
1. Provide a concise Summary (3-5 lines).
2. List potential Risks/Red flags.
3. Give practical Suggestions.

Respond strictly in JSON format:
{{"summary": "...", "risks": "...", "suggestions": "..."}}

Contract Text:
\"\"\"{text}\"\"\"
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
        message = response.choices[0].message.content
        if isinstance(message, str):
            return json.loads(message)
        return message
    except Exception as e:
        print(f"[Warning] OpenAI API failed: {e}")
        return {
            "summary": "Mock summary: contract overview.",
            "risks": "Mock risks: payment delays, confidentiality issues, termination clauses.",
            "suggestions": "Mock suggestions: include penalties, enforce NDA, clarify payment schedule."
        }



