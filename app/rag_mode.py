# app/rag_mode.py

import streamlit as st
import re

from src.rag_pipeline import run_rag_pipeline


def clean_text(text):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(text))).strip()


def render_rag_mode():

    st.subheader("RAG Mode")

    # 🔹 Mode selector
    rag_mode = st.radio(
        "RAG Retrieval Mode:",
        ["Semantic RAG", "Hybrid RAG"],
        horizontal=True,
        help="Semantic: FAISS retrieval. Hybrid: BM25 + Semantic (coming soon)."
    )

    st.caption(f"Current mode: {rag_mode}")

    # 🔹 Input
    query = st.text_input(
        "Ask a question",
        placeholder="e.g. What is a good relaxing album?"
    )

    # 🔹 Run
    if st.button("Generate Answer") and query:

        if rag_mode == "Semantic RAG":
            st.info("Using Semantic RAG (full pipeline)")
            result = run_rag_pipeline(query)

        elif rag_mode == "Hybrid RAG":
            st.info("Hybrid RAG (coming soon) — using semantic fallback")
            result = run_rag_pipeline(query)

        # 🔹 Extract outputs
        answer = result["answer"]
        docs = result["retrieved_docs"]
        context = result["context"]

        # 🔹 Answer panel (required)
        st.markdown("## 🤖 Answer")

        if rag_mode == "Hybrid RAG":
            st.caption("⚠️ Hybrid retrieval not implemented yet. Using semantic fallback.")

        st.write(answer)

        st.divider()

        # 🔹 Optional: show context (good for demo)
        with st.expander("🔍 Context used for answer"):
            st.write(context)

        # 🔹 Retrieved documents
        st.markdown("## 📄 Retrieved Documents")

        for i, (doc, score) in enumerate(docs):
            st.markdown(f"### {i+1}. {doc.metadata.get('product_title')}")
            st.write(clean_text(doc.page_content)[:200] + "...")
            st.caption(f"Score: {score:.4f}")
            st.divider()