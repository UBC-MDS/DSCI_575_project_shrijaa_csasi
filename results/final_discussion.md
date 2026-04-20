# Final Discussion

## Step 1: Improve Your Workflow

### Dataset Scaling
**Dataset used:** Amazon Reviews 2023 — Digital Music category  
**Number of products:** ~67,000 unique products (out of ~70,000 total in the metadata file; ~3,000 are excluded due to missing review text or no metadata match)  
**Number of documents indexed:** ~67,000 (one document per product)

**Previous approach (Milestone 1):**  
The original pipeline downloaded only the first 20,000 rows of the reviews file using `LIMIT 20000` and applied a stratified sampling strategy with `SAMPLE_PER_STRATUM = 50`. This produced ~1,400 documents — a heavily under-sampled dataset that covered a small fraction of available products.

**New sampling strategy — 1 best review per product:**  
The `LIMIT` was removed, and the sampling query was restructured to select exactly **one review per unique product** (`parent_asin`), choosing the review with the highest `helpful_vote` count. This is implemented as a `ROW_NUMBER()` window function partitioned by `parent_asin` and ordered by `helpful_vote DESC`.

**Why this decision was made:**  
- The primary goal of scaling is **product coverage** — the retrieval system should be able to answer questions about as many products as possible. Having 50 reviews for 28 products is less useful than having 1 review for 67,000 products.  
- Helpful votes are a reliable proxy for review quality — the most upvoted review for a product tends to be the most informative and representative.  
- One document per product avoids duplicate retrieval: without this, BM25 and FAISS would return multiple reviews of the same product in the top-k results, reducing result diversity.

**How it helps the pipeline:**  
- BM25 benefits from a larger vocabulary — more products means more unique terms, improving keyword-based recall for niche or specific artist/album queries.  
- FAISS benefits from denser product coverage — the semantic index now spans the full range of Digital Music, so embedding-based similarity search has a much higher chance of finding a relevant product for any given query.  
- The RAG pipeline retrieves more diverse products in its context window, reducing the chance of the LLM receiving redundant or overlapping reviews.
