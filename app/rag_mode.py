import streamlit as st
import re
from src.semantic import load_faiss,search_faiss
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from src.prompts import build_rag_prompt
@st.cache_resource
def get_faiss():
    return load_faiss()

@st.cache_resource
def load_llm():
    model_name = "microsoft/Phi-4-mini-instruct"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,
        device_map="auto"
    )

    return tokenizer, model

def generate_answer(query, docs, tokenizer, model):

    prompt = build_rag_prompt(query, docs)

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    outputs = model.generate(
        **inputs,
        max_new_tokens=150,
        do_sample=True,
        temperature=0.7
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return response.split("Answer clearly and concisely:")[-1].strip()


def render_rag_mode():

    st.subheader("RAG Mode")

    # Mode selector
    rag_mode = st.radio(
        "RAG Retrieval Mode:",
        ["Semantic RAG", "Hybrid RAG"],
        horizontal=True,
        help="Semantic: FAISS retrieval. Hybrid: BM25 + Semantic (coming soon)."
    )

    st.caption(f"Current mode: {rag_mode}")

    #Load models
    faiss_retriever = get_faiss()
    tokenizer, model = load_llm()

    # Input
    query = st.text_input(
        "Ask a question",
        placeholder="e.g. What is a good relaxing album?"
    )

    # Run
    if st.button("Generate Answer") and query:

        # Retrieval (placeholder logic)
        if rag_mode == "Semantic RAG":
            st.info("Using Semantic RAG (FAISS retrieval)")
            docs = search_faiss(query, faiss_retriever, k=5)

        elif rag_mode == "Hybrid RAG":
            st.info("Hybrid RAG (BM25 + Semantic) coming soon...")
            docs = search_faiss(query, faiss_retriever, k=5)  

        # 🔹 Generate answer
        answer = generate_answer(query, docs, tokenizer, model)

        # 🔹 Answer panel 
        st.markdown("## 🤖 Answer")

        if rag_mode == "Hybrid RAG":
            st.caption("Hybrid retrieval not fully implemented yet. Using semantic fallback.")

        st.write(answer)

        st.divider()

        # 🔹 Retrieved documents
        st.markdown("## Retrieved Documents")

        for i, (doc, _) in enumerate(docs):
            st.markdown(f"### {i+1}. {doc.metadata.get('product_title')}")
            st.write(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(doc.page_content))).strip()[:200] + "...")
            st.divider()