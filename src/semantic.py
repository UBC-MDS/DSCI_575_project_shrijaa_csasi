# src/semantic.py

import os
import logging

# Must be set before ANY HuggingFace-related imports
os.environ["HF_HUB_VERBOSITY"] = "error"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

from pathlib import Path
from transformers import logging as transformers_logging
transformers_logging.set_verbosity_error()
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from src.utils import load_documents

# Paths
_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH  = str(_ROOT / "data/processed/documents.parquet")
FAISS_PATH = str(_ROOT / "data/processed/faiss_index")

# Build FAISS Index
def build_faiss(documents):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store

# Save FAISS Index
def save_faiss(vector_store):
    vector_store.save_local(FAISS_PATH)

# Load FAISS Index
def load_faiss():
    vector_store = FAISS.load_local(
        FAISS_PATH, 
        HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
        allow_dangerous_deserialization=True  # safe: index was built locally by this project
    )
    return vector_store

# Search FAISS Index
def search_faiss(query, vector_store, k=5):
    results = vector_store.similarity_search_with_score(query, k=k)
    return results

# Main function to build and save FAISS index
if __name__ == "__main__":
    documents = load_documents(DATA_PATH)
    vector_store = build_faiss(documents)
    save_faiss(vector_store)
    print("FAISS index built and saved successfully.")