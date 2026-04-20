import re

# Prompt Variant 1 — Basic
def prompt_v1(query, context):
    """Simple prompt that provides context and asks for an answer."""
    return f"""You are a helpful Amazon shopping assistant.
Answer the question using the following context (real product reviews + metadata).
Always cite the product ASIN when possible.

Context:
{context}

Question:
{query}

Answer:
"""

# Prompt Variant 2 — Strict
def prompt_v2(query, context):
    """Prompt that enforces answering only from the given context."""
    return f"""You are a helpful assistant answering questions using ONLY the given context.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{query}

Answer clearly and concisely:
"""

# Prompt Variant 3 — Structured (used by default)
def prompt_v3(query, context):
    """Structured prompt for music recommendations."""
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

# Default used by the pipeline
def build_rag_prompt(query, context):
    """Wrapper to build the RAG prompt. Currently uses the structured variant."""
    return prompt_v3(query, context)