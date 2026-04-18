# src/rag_pipeline.py

import re
import os
from groq import Groq
from langchain_core.runnables import RunnableLambda

from src.semantic import load_faiss, search_faiss
from src.prompts import build_rag_prompt
from src.hybrid import build_hybrid_retriever, search_hybrid


MODEL_NAME = "llama-3.1-8b-instant"


# -----------------------------
# LLM Loading (GROQ)
# -----------------------------
def load_llm():
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return client


# -----------------------------
# Text Cleaning
# -----------------------------
def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", str(text))
    text = re.sub(r"\s+", " ", text).strip()
    return text


# -----------------------------
# Retrieval
# -----------------------------
def retrieve_documents(query: str, vector_store, k: int = 5):
    return search_faiss(query, vector_store, k=k)


# -----------------------------
# Context Building
# -----------------------------
def build_context(docs_with_scores, max_docs: int = 3, max_chars: int = 500):

    context_blocks = []

    for i, (doc, score) in enumerate(docs_with_scores[:max_docs], start=1):
        title = doc.metadata.get("product_title", "Unknown Product")
        review_title = doc.metadata.get("title", "No review title")
        review_text = clean_text(doc.page_content)[:max_chars]

        # the user can look up the exact product on Amazon (amazon.com/dp/<ASIN>) to verify the recommendation is real and not hallucinated
        asin = doc.metadata.get("parent_asin", "N/A")
        rating = doc.metadata.get("rating", "N/A")
        block = (
            f"[Document {i}]\n"
            f"Product ASIN: {asin}\n"
            f"Product Title: {title}\n"
            f"Rating: {rating}\n"
            f"Review Title: {review_title}\n"
            f"Review Text: {review_text}\n"
            f"Similarity Score: {score:.4f}"
        )
        context_blocks.append(block)

    return "\n\n".join(context_blocks)


# -----------------------------
# Generation (GROQ)
# -----------------------------
def generate_answer(prompt, client):

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()


# -----------------------------
# Full RAG Pipeline
# -----------------------------
def run_rag_pipeline(
    query: str,
    vector_store=None,
    llm=None,
    k: int = 5,
    max_docs: int = 3
    #prompt_fn=None
):

    if vector_store is None:
        vector_store = load_faiss()

    if llm is None:
        llm = load_llm()

    retrieved_docs = retrieve_documents(query, vector_store, k=k)

    context = build_context(retrieved_docs, max_docs=max_docs)

    prompt = build_rag_prompt(query, context)
    # if prompt_fn is None:
    #     prompt_fn = build_rag_prompt
    # prompt = prompt_fn(query, context) 

    answer = generate_answer(prompt, llm)

    return {
        "query": query,
        "answer": answer,
        "context": context,
        "prompt": prompt,
        "retrieved_docs": retrieved_docs,
    }

# -----------------------------
# Hybrid RAG Pipeline
# -----------------------------
def run_hybrid_rag_pipeline(
        query: str, 
        hybrid_retriever=None, 
        llm=None, 
        k: int = 5, 
        max_docs: int = 3
        # prompt_fn=None
    ):

    if hybrid_retriever is None:
        hybrid_retriever = build_hybrid_retriever(k=k)

    if llm is None:
        llm = load_llm()

    retrieved_docs = search_hybrid(query, hybrid_retriever, k=k)

    # search_hybrid returns plain documents (no scores), so we assign a default score for context building
    docs_with_scores = [(doc, 0.0) for doc in retrieved_docs]

    context = build_context(docs_with_scores, max_docs=max_docs)

    prompt = build_rag_prompt(query, context)
    # if prompt_fn is None:
    #     prompt_fn = build_rag_prompt
    # prompt = prompt_fn(query, context)

    answer = generate_answer(prompt, llm)

    return {
        "query": query,
        "answer": answer,
        "context": context,
        "prompt": prompt,
        "retrieved_docs": retrieved_docs,
    }

# -----------------------------
# LCEL / Runnable Components
# -----------------------------
def make_retrieval_step(vector_store, k: int = 5):
    return RunnableLambda(lambda query: retrieve_documents(query, vector_store, k=k))


def make_context_step(max_docs: int = 3, max_chars: int = 500):
    return RunnableLambda(lambda docs: build_context(docs, max_docs=max_docs, max_chars=max_chars))


def make_prompt_step():
    return RunnableLambda(lambda x: build_rag_prompt(x["query"], x["context"]))


def make_generation_step(llm):
    return RunnableLambda(lambda prompt: generate_answer(prompt, llm))


def build_lcel_rag_chain(vector_store, llm, k: int = 5, max_docs: int = 3):

    retrieval_step = make_retrieval_step(vector_store, k=k)
    context_step = make_context_step(max_docs=max_docs)

    def prepare_prompt_inputs(query: str):
        docs = retrieval_step.invoke(query)
        context = context_step.invoke(docs)
        return {"query": query, "context": context}

    prompt_input_step = RunnableLambda(prepare_prompt_inputs)
    prompt_step = make_prompt_step()
    generation_step = make_generation_step(llm)

    chain = prompt_input_step | prompt_step | generation_step
    return chain