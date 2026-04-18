import re


def clean_text(text):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(text))).strip()


def build_rag_prompt(query, docs, max_docs=3, max_chars=300):
    """
    Builds a prompt for RAG using retrieved documents.
    """

    context_chunks = []

    for doc, _ in docs[:max_docs]:
        text = clean_text(doc.page_content)[:max_chars]
        context_chunks.append(f"- {text}")

    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a helpful assistant answering questions based on product reviews.

Use ONLY the information provided in the context below.
If the answer is not contained in the context, say you don't know.

Context:
{context}

Question:
{query}

Answer clearly and concisely:
"""

    return prompt