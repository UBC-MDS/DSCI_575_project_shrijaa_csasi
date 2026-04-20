# app/rag_mode.py

import streamlit as st
import re

from src.rag_pipeline import run_rag_pipeline, run_hybrid_rag_pipeline
from src.prompts import prompt_v1, prompt_v2, prompt_v3, build_rag_prompt

def render_rag_mode():

    # Mode selector
    rag_mode = st.radio(
        "RAG Retrieval Mode:",
        ["Semantic RAG", "Hybrid RAG"],
        horizontal=True,
        help="Semantic: FAISS retrieval. Hybrid: BM25 + Semantic ensemble."
    )

    st.caption(f"Current mode: {rag_mode}")

    # Do not delete: this section is to test different prompt variants for RAG answer generation. 
    # prompt_variant = st.selectbox(
    #     "Prompt variant:",
    #     ["V3 — Structured (default)", "V1 — Basic", "V2 — Strict"],
    #     help="Experiment with different prompt styles."
    # )
    # PROMPT_MAP = {
    #     "V1 — Basic": prompt_v1,
    #     "V2 — Strict": prompt_v2,
    #     "V3 — Structured (default)": prompt_v3,
    # }
    # selected_prompt_fn = PROMPT_MAP[prompt_variant]

    # Input
    with st.form("rag_form"):
        query = st.text_input(
            "Ask a question",
            placeholder="e.g. What is a good relaxing album?"
        )
        submitted = st.form_submit_button("Generate Answer", type="primary")

    # Run
    if submitted and query:

        if rag_mode == "Semantic RAG":
            st.info("Using Semantic RAG (full pipeline)")
            result = run_rag_pipeline(query)
            docs = result["retrieved_docs"]

        elif rag_mode == "Hybrid RAG":
            st.info("Using Hybrid RAG (BM25 + Semantic ensemble)")
            result = run_hybrid_rag_pipeline(query)
            docs = [(doc, None) for doc in result["retrieved_docs"]]

        # Extract outputs
        answer = result["answer"]        
        context = result["context"]

        # Answer panel 
        st.markdown("### Answer")
        st.write(answer)
        st.divider()

        # Optional: show context (good for demo)
        with st.expander("Context used for answer"):
            st.write(context)

        # Retrieved documents
        st.markdown("### Retrieved Documents")
        for i, (doc, score) in enumerate(docs):
            with st.container(border=True):    
                st.markdown(f"#### {i+1}. {doc.metadata.get('product_title', 'Unknown')}")
                # only removing HTML tags and extra whitespace, no tokenization or stopword removal since we want to show the original review text in the results
                st.write(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(doc.metadata.get("text", "")))).strip()[:200] + "...")
                if score is not None:
                    st.caption(f"Score: {score:.4f}")
                else:
                    st.caption(f"Rank: {i+1}")
                #st.divider()