# src/rag_pipeline.py

import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain_core.runnables import RunnableLambda
from src.semantic import load_faiss, search_faiss
from src.prompts import build_rag_prompt


MODEL_NAME = "microsoft/Phi-4-mini-instruct"


# -----------------------------
# LLM Loading
# -----------------------------
def load_llm(model_name: str = MODEL_NAME):
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        use_fast=False
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,
        device_map="auto"
    )

    return tokenizer, model


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
    """
    Retrieve top-k documents from FAISS.
    
    Returns:
        list of (Document, score)
    """
    return search_faiss(query, vector_store, k=k)


# -----------------------------
# Context Building
# -----------------------------
def build_context(docs_with_scores, max_docs: int = 3, max_chars: int = 500) -> str:
    """
    Convert retrieved documents into a prompt-ready context block.
    """
    context_blocks = []

    for i, (doc, score) in enumerate(docs_with_scores[:max_docs], start=1):
        title = doc.metadata.get("product_title", "Unknown Product")
        review_title = doc.metadata.get("title", "No review title")
        review_text = clean_text(doc.page_content)[:max_chars]

        block = (
            f"[Document {i}]\n"
            f"Product Title: {title}\n"
            f"Review Title: {review_title}\n"
            f"Review Text: {review_text}\n"
            f"Similarity Score: {score:.4f}"
        )
        context_blocks.append(block)

    return "\n\n".join(context_blocks)


# -----------------------------
# Generation
# -----------------------------
def generate_answer(prompt: str, tokenizer, model, max_new_tokens: int = 200) -> str:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.7
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if "Answer clearly and concisely:" in response:
        return response.split("Answer clearly and concisely:")[-1].strip()

    return response.strip()


# -----------------------------
# Full RAG Pipeline
# -----------------------------
def run_rag_pipeline(
    query: str,
    vector_store=None,
    tokenizer=None,
    model=None,
    k: int = 5,
    max_docs: int = 3,
):
    """
    Full RAG pipeline:
    1. Retrieve documents
    2. Build context
    3. Build prompt
    4. Generate answer

    Returns:
        dict with answer, prompt, context, retrieved_docs
    """
    if vector_store is None:
        vector_store = load_faiss()

    if tokenizer is None or model is None:
        tokenizer, model = load_llm()

    retrieved_docs = retrieve_documents(query, vector_store, k=k)
    context = build_context(retrieved_docs, max_docs=max_docs)
    prompt = build_rag_prompt(query, context)
    answer = generate_answer(prompt, tokenizer, model)

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


def make_generation_step(tokenizer, model):
    return RunnableLambda(lambda prompt: generate_answer(prompt, tokenizer, model))


def build_lcel_rag_chain(vector_store, tokenizer, model, k: int = 5, max_docs: int = 3):
    """
    Build a simple LCEL-style RAG chain.
    Input: query (str)
    Output: answer (str)
    """
    retrieval_step = make_retrieval_step(vector_store, k=k)
    context_step = make_context_step(max_docs=max_docs)

    def prepare_prompt_inputs(query: str):
        docs = retrieval_step.invoke(query)
        context = context_step.invoke(docs)
        return {"query": query, "context": context}

    prompt_input_step = RunnableLambda(prepare_prompt_inputs)
    prompt_step = make_prompt_step()
    generation_step = make_generation_step(tokenizer, model)

    chain = prompt_input_step | prompt_step | generation_step
    return chain