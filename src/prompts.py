import re


# -----------------------------
# Utility
# -----------------------------
def clean_text(text):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(text))).strip()


# -----------------------------
# Version 1: Docs → Prompt (your current usage)
# -----------------------------
def build_rag_prompt_from_docs(query, docs, max_docs=3, max_chars=300):
    """
    Builds a prompt directly from retrieved documents.
    (Used in Streamlit app currently)
    """
    context_chunks = []

    for doc, _ in docs[:max_docs]:
        text = clean_text(doc.page_content)[:max_chars]
        context_chunks.append(f"- {text}")

    context = "\n\n".join(context_chunks)

    return f"""
You are a helpful assistant answering questions based on product reviews.

Use ONLY the information provided in the context below.
If the answer is not contained in the context, say you don't know.

Context:
{context}

Question:
{query}

Answer clearly and concisely:
"""


# -----------------------------
# Version 2: Context → Prompt (for rag_pipeline.py)
# -----------------------------
def build_rag_prompt(query, context):
    """
    Builds a prompt from pre-constructed context string.
    (Used in rag_pipeline.py)
    """
    return f"""
You are a helpful assistant answering questions based on product reviews.

Use ONLY the information provided in the context below.
If the answer is not contained in the context, say you don't know.

Context:
{context}

Question:
{query}

Answer clearly and concisely:
"""