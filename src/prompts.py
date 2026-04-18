import re

def clean_text(text):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(text))).strip()

def build_rag_prompt(query, context):
    return f"""
You are a music recommendation assistant.

Use the context to answer the query. If exact details (like song names)
are not present, give a helpful recommendation based on the album or artist.

Rules:
- Prefer album or artist names if song names are missing
- You may infer general recommendations
- Keep answer under 200 characters
- Do NOT say "I don't know" unless context is completely irrelevant

Context:
{context}

Question:
{query}

Answer:
"""