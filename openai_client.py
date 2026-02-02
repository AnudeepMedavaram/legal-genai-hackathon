# openai_client.py
import streamlit as st
from openai import OpenAI
import json

# Read API key from Streamlit Secrets (works on Cloud) or .env locally
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    import os
    api_key = os.getenv("OPENAI_API_KEY")

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
        # Fallback mock response
        st.warning(f"OpenAI API failed or quota exceeded: {e}")
        return {
            "summary": "Mock summary: contract overview.",
            "risks": "Mock risks: payment delays, confidentiality issues, termination clauses.",
            "suggestions": "Mock suggestions: include penalties, enforce NDA, clarify payment schedule."
        }

