import streamlit as st
import pandas as pd
from datetime import datetime 
import os


# Config
st.set_page_config(page_title="Product Search Engine", layout="wide")

#file variables
FEEDBACK_FILE = "feedback.csv"
top_k = 3


# Session State 
if "results" not in st.session_state:
    st.session_state.results = []
if "query" not in st.session_state:
    st.session_state.query = ""


col1, col2 = st.columns([4, 1])

with col1:
    st.title("Amazon Review Search")

with col2:
    if st.button("Reset"):
        st.session_state.results = []
        st.session_state.query = ""
        st.session_state.search_box = ""
        st.rerun()

# Search Mode
search_mode = st.radio(
    "Select Search Mode:",
    ["BM25", "Semantic"]
)

# Track previous mode
if "prev_mode" not in st.session_state:
    st.session_state.prev_mode = search_mode

# If mode changed -> reset results
if st.session_state.prev_mode != search_mode:
    st.session_state.results = []
    st.session_state.query = ""
    st.session_state.search_box = ""  
    st.session_state.prev_mode = search_mode
    st.rerun()

# Dummy Retrieval Functions
def bm25_search(query, top_k):
    return [
        {
            "title": f"BM25 Product {i+1}",
            "review": "This is a sample review text for BM25...",
            "rating": 4.5,
            "score": 12.3 - i
        }
        for i in range(top_k)
    ]

def semantic_search(query, top_k):
    return [
        {
            "title": f"Semantic Product {i+1}",
            "review": "This is a semantic search result...",
            "rating": 4.8,
            "score": 0.95 - (i * 0.05)
        }
        for i in range(top_k)
    ]


# Save Feedback
def save_feedback(query, result, feedback):
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

    if os.path.exists(FEEDBACK_FILE):
        df.to_csv(FEEDBACK_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(FEEDBACK_FILE, index=False)


# Search Form
with st.form("search_form"):
    query = st.text_input(
    "Search",
    placeholder="e.g. noise cancelling headphones",
    key="search_box"
)
    submitted = st.form_submit_button("Search")

if submitted and query:
    if search_mode == "BM25":
        st.session_state.results = bm25_search(query, top_k)
    else:
        st.session_state.results = semantic_search(query, top_k)

    st.session_state.query = query

if "search_box" in st.session_state:
    query = st.session_state.search_box
# Display Results
if st.session_state.results:
    st.subheader(f"Results for: {st.session_state.query}")

    for i, res in enumerate(st.session_state.results):
        with st.container():
            st.markdown(f"### {i+1}. {res['title']}")

            st.write(f"**Review:** {res['review'][:200]}...")
            st.write(f"**Rating:** {res['rating']}")
            st.write(f"**Score:** {res['score']}")

            # Feedback buttons

            col0, col1, col2,col3 = st.columns([3,1, 1, 1])
            with col1: 
                st.write("**Was this result helpful ?**")

            with col2:
                if st.button("👍", key=f"up_{i}"):
                    save_feedback(st.session_state.query, res, "upvote")
                    st.success("Thanks ! Glad you found this helpful!")

            with col3:
                if st.button("👎", key=f"down_{i}"):
                    save_feedback(st.session_state.query, res, "downvote")
                    st.warning("Got it! We'll try to improve our results!")

            st.divider()