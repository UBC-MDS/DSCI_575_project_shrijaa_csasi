# Milestone 2 Discussion

## Model Choice and Rationale

**Selected Model:** `llama3-8b-8192` via [Groq](https://groq.com/) (`langchain_groq`)

**Rationale:**

We chose the Groq-hosted Llama 3 8B model over locally-run HuggingFace alternatives for the following reasons:

1. **No local GPU required.** Running a 7–8B parameter model locally demands 16 GB of VRAM. Using the Groq inference API avoids this constraint entirely, making the pipeline reproducible on any machine.

2. **Fast inference.** Groq's LPU hardware delivers significantly faster token generation than CPU-based local inference, which is important when evaluating 10+ queries in Step 5.

3. **Simple LangChain integration.** `langchain_groq.ChatGroq` is a drop-in replacement for any `ChatModel` in LangChain LCEL chains, requiring no changes to the RAG pipeline structure.

4. **Strong instruction-following.** Llama 3 8B (instruct-tuned) performs well on question-answering tasks grounded in retrieved context, which is the core use case of our RAG pipeline.

5. **Free tier availability.** Groq's free tier (rate-limited) is sufficient for development and the manual evaluation in Step 5.

**Setup:**
```python
from langchain_groq import ChatGroq

llm = ChatGroq(model="llama3-8b-8192")
```
Requires a `GROQ_API_KEY` environment variable (obtainable at https://console.groq.com).

## Prompt Experiment Findings

We tested three prompt variants on the queries:
*"Which albums are good for studying?"*
*"What is the best phone?"*

### Prompt Variant 1 — Basic
- Generates answers even when context is weak or irrelevant.
- Tends to make assumptions (e.g., inferring study suitability from mood descriptions).
- Higher risk of hallucination but useful for exploratory responses.

### Prompt Variant 2 — Strict
- Most conservative and reliable.
- Correctly outputs "does not contain information" when the answer is not supported by context.
- Minimizes hallucinations; best for factual grounding.

### Prompt Variant 3 — Structured (selected as default)
- Produces more interpretable answers by inferring from album/artist context.
- Slightly more informative than V2 but may infer beyond explicit context.
- Best balance between informativeness and structure for a music domain.

**Selected default:** Variant 3, as it suits the music recommendation use case
where light inference from reviews is acceptable and useful.

## RAG Evaluation

**Pipeline evaluated:** Hybrid RAG (BM25 40% + FAISS 60%, top-k = 5)  
**Model:** `llama-3.1-8b-instant` via Groq  
**Prompt:** Variant 3 — Structured  
user can look up the exact product on Amazon (amazon.com/dp/<ASIN>) to verify the recommendation is real and not hallucinated

| # | Query | Type | Accuracy | Completeness | Fluency |
|---|-------|------|----------|--------------|---------|
| 1 | taylor swift album | Easy | Yes | Yes | Yes |
| 2 | ed sheeran songs | Easy | Yes | No | Yes |
| 3 | classical piano music | Easy | Yes | Yes | Yes |
| 4 | jazz instrumental album | Easy | No | Yes | Yes |
| 5 | music to relax while studying | Medium | Yes | Yes | Yes |
| 6 | songs for a long road trip | Medium | No | Yes | Yes |
| 7 | calming instrumental music | Medium | No | Yes | Yes |
| 8 | upbeat music for working out | Medium | Yes | Yes | Yes |
| 9 | best album for heartbreak | Complex | Yes | No | Yes |
| 10 | music without lyrics for focus | Complex | No | No | Yes |

#### Query 2: "ed sheeran songs"
- **Accuracy:** BM25 component retrieves keyword-matched Ed Sheeran reviews directly, giving the LLM strong grounding. Answer does name specific album.  
- **Completeness:** only mentions 1 album; the review corpus may not cover all Ed Sheeran releases.  
- **Fluency:** Structured prompt produces clean, readable output.

#### Query 4: "jazz instrumental album" 
- **Accuracy:** Hybrid search surface albums like *Happy Again by Jazz Crusaders (1995) Audio CD*, *Pickin' Up Steam*.  
- **Completeness:** Answer covers genre well but produces duplicates and may miss specific composers.  
- **Fluency:** Good — prompt encourages album/artist-level recommendations.

#### Query 5: "music to relax while studying"
- **Accuracy:** the hybrid answer is grounded in some of the retrieved reviews and inferred in some *Music to listen to after work and dinner*.  
- **Completeness:** hybrid retrieval returns loosely relevant docs.  
- **Fluency:** Structured prompt handles vague queries gracefully.

#### Query 9: "best album for heartbreak" 
- **Accuracy:** Complex emotional query, however the LLM isn't hallucinating album names not in the retrieved context.  
- **Completeness:** Likseems to be incomplete, emotional intent is hard to capture from review text.  
- **Fluency:** Answer is fluent but weakly grounded.

#### Query 10: "music without lyrics for focus"
- **Accuracy:** Instrumental/focus queries have limited explicit coverage in review text. 
- **Completeness:** Partial at best — reviews rarely describe whether an album is vocal or instrumental.  
- **Fluency:** Prompt V3 handles this gracefully by inferring from album/artist context.


### Observations

- **Easy keyword queries (1–4)** benefit from the BM25 component, which retrieves exact keyword matches. The LLM produces accurate, grounded answers for well-represented artists like Taylor Swift and jazz albums.
- **Medium semantic queries (5–8)** benefit from the FAISS component. BM25 alone fails these, but the hybrid fusion brings relevant documents into context.
- **Complex queries (9–10)** remain challenging. The review corpus lacks explicit emotional or functional labelling (e.g., "heartbreak", "focus"), so retrieved documents are only loosely relevant, limiting answer quality regardless of prompt design.
- Prompt Variant 3 consistently produces fluent, readable answers. Where context is weak, it infers from album/artist names rather than abstaining, which improves fluency but slightly risks inaccuracy.

### Limitations

1. **Corpus coverage gap.** The Amazon Digital Music review dataset does not contain explicit labels for mood, activity, or emotion. Queries like "music for studying" or "heartbreak album" have no direct textual match in reviews, limiting retrieval quality at the source.
2. **BM25 tokenization mismatch.** BM25 operates on preprocessed, stopword-removed tokens. Queries with common words (e.g., "songs for a long road trip") lose signal after preprocessing, reducing BM25's contribution in the hybrid fusion.
3. **No answer grounding check.** The pipeline does not verify whether the LLM's answer is supported by the retrieved context. Prompt V3 allows inference, which can produce fluent but unverifiable recommendations.
4. **Fixed retrieval weights.** BM25 (40%) and FAISS (60%) weights are static. For keyword-heavy queries, BM25 should carry more weight; for semantic queries, FAISS should dominate. A dynamic weighting strategy would improve performance across query types.

### Potential Improvements

1. **Query-adaptive weighting.** Detect whether a query is keyword-heavy or semantic (e.g., by checking if the query terms appear literally in the corpus) and adjust BM25/FAISS weights dynamically.
2. **Metadata-enriched retrieval.** Index additional product metadata fields (genre tags, product descriptions) alongside review text so mood/activity queries have more surface area to match against.
3. **Answer verification step.** Add a post-generation check that confirms at least one retrieved document supports the answer, falling back to a "not enough information" response if not.
4. **Re-ranking with a cross-encoder.** Apply a cross-encoder model (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`) to re-rank the top-k retrieved documents before context building, improving precision for complex queries.