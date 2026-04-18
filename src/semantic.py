# src/semantic.py

import os
import logging
from pathlib import Path

# Silence HF logs
os.environ["HF_HUB_VERBOSITY"] = "error"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

from transformers import logging as transformers_logging
transformers_logging.set_verbosity_error()
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from src.utils import load_documents


# -------- Paths --------
_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH  = str(_ROOT / "data/processed/documents.parquet")
FAISS_PATH = str(_ROOT / "data/processed/faiss_index")


# -------- Embeddings --------
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


# -------- Build --------
def build_faiss(documents):
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store


# -------- Save --------
def save_faiss(vector_store):
    vector_store.save_local(FAISS_PATH)


# -------- Load --------
def load_faiss():
    embeddings = get_embeddings()
    vector_store = FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vector_store


# -------- Search --------
def search_faiss(query, vector_store, k=5):
    """
    Returns:
        List of (Document, score)
    """
    return vector_store.similarity_search_with_score(query, k=k)


# -------- Retriever (for LCEL) --------
def get_retriever(vector_store, k=5):
    return vector_store.as_retriever(search_kwargs={"k": k})


# -------- Main --------
if __name__ == "__main__":
    documents = load_documents(DATA_PATH)
    vector_store = build_faiss(documents)
    save_faiss(vector_store)
    print("FAISS index built and saved successfully.")