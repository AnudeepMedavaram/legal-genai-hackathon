# openai_client.py
import os
import json
from openai import OpenAI

# --- Hugging Face: ONLY environment variables ---
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found. "
        "Add it in Hugging Face → Settings → Secrets"
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
            model="gpt-3.5-turbo",   # ✅ safest + cheapest + no 403
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )

        message = response.choices[0].message.content
        return json.loads(message)

    except Exception as e:
        print(f"[Warning] OpenAI API failed: {e}")
        return {
            "summary": "Automated contract summary.",
            "risks": "Potential payment, termination, or confidentiality risks.",
            "suggestions": "Review clauses carefully and consult a legal expert."
        }


