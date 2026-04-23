import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import re

from src.bm25 import search as bm25_search
from src.semantic import search_faiss as semantic_search

FEEDBACK_FILE = Path(__file__).resolve().parents[1] / "feedback.csv"
TOP_K = 5


def save_feedback(query, result, feedback):
    """Appends a feedback row (upvote/downvote) to the feedback CSV file."""
    row = {
        "query": query,
        "title": result["title"],
        "review": result["review"],
        "rating": result["rating"],
        "score": result["score"],
        "feedback": feedback,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    df = pd.DataFrame([row])
    if FEEDBACK_FILE.exists():
        df.to_csv(FEEDBACK_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(FEEDBACK_FILE, index=False)


def render_search_mode(bm25_retriever, faiss_retriever):
    """Renders the Search tab UI using pre-loaded BM25 and FAISS indices."""
    # Session State
    if "results" not in st.session_state:
        st.session_state.results = []
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "input_counter" not in st.session_state:
        st.session_state.input_counter = 0

    search_mode = st.radio(
        "Search mode:",
        ["BM25", "Semantic"],
        horizontal=True,
        help="BM25: fast keyword matching. Semantic: meaning-based similarity using sentence embeddings." 
    )

    if "prev_mode" not in st.session_state:
        st.session_state.prev_mode = search_mode

    if st.session_state.prev_mode != search_mode:
        st.session_state.results = []
        st.session_state.query = ""
        st.session_state.input_counter += 1
        st.session_state.prev_mode = search_mode
        st.rerun()

    st.caption(f"Current mode: {search_mode}")
    
    # Form
    with st.form("search_form"):
        query = st.text_input(
            "Enter your search query:",
            placeholder="e.g. Taylor Swift - Red (Deluxe Edition)",
            key=f"search_box_{st.session_state.input_counter}"
        )

        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            submitted = st.form_submit_button("Search", type="primary", use_container_width=True)
        with col2:
            reset = st.form_submit_button("Reset", use_container_width=True)

    if reset:
        st.session_state.results = []
        st.session_state.query = ""
        st.session_state.input_counter += 1
        st.rerun()

    if submitted and query:
        if search_mode == "BM25":
            docs = bm25_search(query, bm25_retriever, k=TOP_K)

            st.session_state.results = [
                {
                    "title": doc.metadata.get("product_title"),
                    "review_title": doc.metadata.get("title", "No title"),
                    # only removing HTML tags and extra whitespace, no tokenization or stopword removal since we want to show the original review text in the results
                    "review": re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(doc.metadata.get("text", "")))).strip(), 
                    "rating": doc.metadata.get("rating", "N/A"),
                    "score": f"BM25 rank #{i+1}"
                }
                for i, doc in enumerate(docs)
            ]

        else:
            docs_and_scores = semantic_search(query, faiss_retriever, k=TOP_K)

            st.session_state.results = [
                {
                    "title": doc.metadata.get("product_title"),
                    "review_title": doc.metadata.get("title", "No title"),
                    # only removing HTML tags and extra whitespace, no tokenization or stopword removal since we want to show the original review text in the results
                    "review": re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(doc.metadata.get("text", "")))).strip(),  
                    "rating": doc.metadata.get("rating", "N/A"),
                    "score": f"Similarity rank #{i+1}"
                }
                for i, (doc, _) in enumerate(docs_and_scores)
            ]

        st.session_state.query = query

    # Display
    if st.session_state.results:
        st.markdown(f"**Results for:** _{st.session_state.query}_")

        for i, res in enumerate(st.session_state.results):
            with st.container(border=True):
                # Title + score on same row
                h_col, s_col = st.columns([4, 1]) 
                with h_col:
                    st.markdown(f"#### {i+1}. {res['title']}")
                with s_col:
                    st.caption(res["score"])

                st.markdown(f"**Review Title:** {res['review_title']}")
                # Star rating
                try:
                    r = float(res['rating'])
                    stars = "★" * int(r) + "☆" * (5 - int(r))
                    st.markdown(f"**Rating:** {stars} ({res['rating']})")
                except (ValueError, TypeError):
                    st.markdown(f"**Rating:** {res['rating']}")

                # Review preview + expandable full review
                review_text = res['review']
                if len(review_text) > 300:
                    st.write(review_text[:300] + "...")
                    with st.expander("Read full review"):
                        st.write(review_text)
                else:
                    st.write(review_text)

                # Feedback row
                f_col, up_col, down_col = st.columns([6, 1, 1])
                with f_col:
                    st.caption("Was this result helpful?")
                with up_col:
                    if st.button("👍 Yes", key=f"up_{i}", use_container_width=True):
                        save_feedback(st.session_state.query, res, "upvote")
                        st.success("Thanks! Glad this was helpful.")
                with down_col:
                    if st.button("👎 No", key=f"down_{i}", use_container_width=True):
                        save_feedback(st.session_state.query, res, "downvote")
                        st.warning("Got it! We'll work on improving results.")