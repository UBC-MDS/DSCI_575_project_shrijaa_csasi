import os
from dotenv import load_dotenv
load_dotenv()
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from src.semantic import load_faiss
from src.bm25 import load_bm25
from src.rag_pipeline import load_llm
from app.search_mode import render_search_mode
from app.rag_mode import render_rag_mode

st.set_page_config(page_title="Product Search Engine", layout="wide")

st.markdown("""
    <h1 style='text-align: center; font-size: 2.5rem; padding: 1rem 0 0.25rem 0;'>
        Amazon Review Search
    </h1>
    <p style='text-align: center; color: grey; margin-bottom: 2rem;'>
        Search and explore Amazon Digital Music reviews using BM25, Semantic Search, or AI-powered RAG
    </p>
    <hr/>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading search indices...")
def get_shared_faiss():
    """Loads and caches the FAISS vector store once for the entire app session."""
    return load_faiss()


@st.cache_resource(show_spinner="Loading BM25 index...")
def get_shared_bm25():
    """Loads and caches the BM25 retriever once for the entire app session."""
    return load_bm25()


@st.cache_resource
def get_shared_llm():
    """Loads and caches the Groq LLM client once for the entire app session."""
    return load_llm()


if "page" not in st.session_state:
    st.session_state.page = "Search"

with st.sidebar:
    if st.button("Search", use_container_width=True):
        st.session_state.page = "Search"
        st.rerun()
    if st.button("RAG", use_container_width=True):
        st.session_state.page = "RAG"
        st.rerun()

if st.session_state.page == "Search":
    render_search_mode(get_shared_bm25(), get_shared_faiss())
else:
    render_rag_mode(get_shared_faiss(), get_shared_bm25(), get_shared_llm())