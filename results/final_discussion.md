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

### LLM Experiment

**Models considered and why they were excluded:**

| Model | Status | Reason excluded |
|---|---|---|
| `mixtral-8x7b-32768` | Decommissioned | Groq returned `model_decommissioned` error: "no longer supported" |
| `gemma2-9b-it` | Decommissioned | Groq returned `model_decommissioned` error: "no longer supported" |
| `qwen/qwen3-32b` | Excluded | Reasoning model — outputs a `<think>...</think>` chain-of-thought block before the actual answer; with `max_tokens=200` the token budget runs out inside the thinking trace, producing no usable answer. Even with thinking disabled, a 32B model introduces noticeable latency on Groq's free-tier rate limits, making it unsuitable for an interactive app. |

**Models compared:**

| Model | Family | Parameters | Provider |
|---|---|---|---|
| `llama-3.1-8b-instant` | Meta Llama 3.1 | 8B | Groq API |
| `llama-3.3-70b-versatile` | Meta Llama 3.3 | 70B | Groq API |

**Why these two models:** Both are from Meta's Llama family, which isolates the effect of model scale (8B vs 70B) while keeping architecture and training consistent. Both are available and actively supported on Groq.

**Prompt used (Variant 3 — Structured):**
>You are a music recommendation assistant.
>
>Use the context to answer the query. If exact details (like song names)
>are not present, give a helpful recommendation based on the album or artist.
>
>Rules:
>- Prefer album or artist names if song names are missing
>- You may infer general recommendations
>- Keep answer under 200 characters
>- Do NOT say "I don't know" unless context is completely irrelevant
>
>Context:
>{context}
>
>Question:
>{query}
>
>Answer:

**Results:**

| Query | Llama 3.1 8B Instant | Llama 3.3 70B Versatile |
|---|---|---|
| Good album for studying? | "Lyrical Lion" by Klondike Kat — laid-back, may help focus | *Tubular Bells LP* by Mike Oldfield |
| Relaxing jazz album | Earl Klugh Trio Volume One or Best of so Far | The Earl Klugh Trio Volume One or similar Earl Klugh albums |
| Best Taylor Swift album | Fearless Taylor's Version (highest similarity score, all 5-star) | Fearless Taylor's Version |
| Music for a long road trip | Jack Johnson or Brushfire Fairytales | "Be There" or "Last Flight Out" |
| Upbeat album for working out | Cardio Coach series or Experience Joy Instrumental | Cardio Coach or Experience Joy Instrumental |

**Key observations:**
- **Conciseness:** Llama 3.3 70B consistently produces shorter, more direct answers and better adheres to the "under 200 characters" constraint in the prompt. Llama 3.1 8B sometimes produces verbose answers and occasionally leaks retrieval metadata (e.g., mentioning similarity scores) into the answer.
- **Relevance:** Llama 3.3 70B made a more contextually appropriate recommendation for the studying query (*Tubular Bells* is a well-known ambient instrumental album), suggesting stronger world knowledge informing its inference from context.
- **Grounding:** Both models stay grounded in retrieved documents. Neither hallucinates album names not present in context.
- **Consistency:** For straightforward queries (Taylor Swift, workout), both models produce near-identical answers — confirming that for well-represented queries, retrieval quality dominates over model size.

**Model chosen for the app:** `llama-3.1-8b-instant`  
**Reason:** The quality improvement from 70B is modest and limited to subtle conciseness and relevance gains. For an interactive application, `llama-3.1-8b-instant` provides significantly lower latency on Groq's free tier, making it the better choice where response speed matters. If the application were batch-processing or offline, the 70B model would be preferred.

## Cloud Deployment Plan
This section outlines a high-level plan for deploying the Amazon - Digital Music product recommendation system on AWS.

### Data Storage

- **Raw Data**  
  Stored in **Amazon S3** as compressed `.jsonl.gz` files. S3 provides scalable and durable storage for large datasets.

- **Processed Data**  
  Cleaned and structured data (e.g., `documents.parquet`) stored in S3 for efficient access and reuse.

- **Vector Index (FAISS)**  
  The FAISS index is stored in S3 and downloaded to the application instance at startup. This avoids recomputation and reduces deployment time.

- **BM25 Index**  
  BM25 index files (`.pkl`) are also stored in S3 and loaded into memory when the app initializes.

### Compute

- **Application Hosting**  
  The application can be deployed using **AWS EC2** or containerized using **AWS ECS/Fargate** for better scalability and management.

- **Handling Multiple Users (Concurrency)**  
  - Use a load balancer (e.g., **Application Load Balancer**) to distribute traffic  
  - Scale instances horizontally using **Auto Scaling Groups** or ECS services  
  - Cache frequently accessed data (e.g., indexes) in memory to reduce latency  

- **LLM Inference**  
  - Use external API (e.g., **Groq API**) for inference to avoid managing GPU infrastructure  
  - This ensures low latency and simplifies deployment  
  - Optionally, a hosted model on **SageMaker** could be used for full control  

### Streaming / Updates

- **Incorporating New Products**  
  - Periodically ingest new review data into S3  
  - Trigger a batch pipeline (e.g., via AWS Lambda or scheduled jobs) to update processed data and indexes  

- **Keeping the Pipeline Up to Date**  
  - Rebuild FAISS and BM25 indexes on a schedule (e.g., daily/weekly)  
  - Use versioned storage in S3 to manage updates  
  - Deploy updated indexes without downtime by reloading them in new instances  

### Summary

This architecture leverages S3 for storage, scalable compute (EC2/ECS), and external LLM APIs to create a cost-effective, scalable, and maintainable deployment for the recommendation system.