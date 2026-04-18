import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from app.search_mode import render_search_mode
from app.rag_mode import render_rag_mode

st.set_page_config(page_title="Product Search Engine", layout="wide")

st.title("Amazon Review Search")
st.caption("Search through Amazon Digital Music reviews using keyword (BM25), semantic similarity, or RAG.")

# Tabs
tab1, tab2 = st.tabs(["🔍 Search", "RAG"])

with tab1:
    render_search_mode()

with tab2:
    render_rag_mode()