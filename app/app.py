import streamlit as st
import pandas as pd
from datetime import datetime 
import os
import sys
import re
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from src.bm25 import load_bm25, search as bm25_search




print("ROOT_DIR:", ROOT_DIR)
print("SYS PATH:", sys.path)

# Config
st.set_page_config(page_title="Product Search Engine", layout="wide")

#file variables
FEEDBACK_FILE = "feedback.csv"
top_k = 5

# Load BM25 retriever (cached)
@st.cache_resource
def get_bm25():
    return load_bm25()

bm25_retriever = get_bm25()

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

#Dummy Retrieval Functions
def semantic_search(query, top_k):
    return [
        {
            "title": f"Semantic Product {i+1}",
            "review_title":f"Semantic Product Review Title {i+1}",
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
    placeholder="e.g. Taylor Swift - Red (Deluxe Edition)",
    key="search_box"
)
    submitted = st.form_submit_button("Search")

if submitted and query:
    if search_mode == "BM25":
        docs = bm25_search(query, bm25_retriever, k=top_k)

        # Convert LangChain Documents → your app format
        st.session_state.results = [
            {
                
                "title": doc.metadata.get("product_title"),
                "review_title": doc.metadata.get("title", "No title"),
                "review": re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(doc.page_content))).strip(),
                "rating": doc.metadata.get("rating", "N/A"),
                "score": "BM25"
            }
            for doc in docs
        ]
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
            st.markdown(f"**Review Title:** {res['review_title']}")
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