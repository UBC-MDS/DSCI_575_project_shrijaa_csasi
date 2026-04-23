# src/utils.py

import pandas as pd
import re
from langchain_core.documents import Document
import nltk
from nltk.corpus import stopwords
nltk.download("stopwords", quiet=True)
STOPWORDS = set(stopwords.words("english"))


def load_documents(data_path):
    """Loads documents from a Parquet file and returns a list of LangChain Document objects."""
    df = pd.read_parquet(data_path)
    if 'text_clean' not in df.columns:
        raise ValueError(
            "'text_clean' column not found. Re-run milestone1_exploration.ipynb."
        )
    df = df.dropna(subset=['text_clean'])
    return [
        Document(
            page_content=row['text_clean'],
            metadata={k: (v.tolist() if hasattr(v, 'tolist') else v)
                      for k, v in row.items() if k != 'text_clean'}
        )
        for _, row in df.iterrows()
    ]

def preprocess_text(text):
    """Preprocesses text by lowercasing, removing punctuation, and removing stopwords."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)   # remove punctuation
    tokens = [t for t in text.split() if t not in STOPWORDS]
    return tokens