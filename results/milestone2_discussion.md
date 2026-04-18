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

We tested three prompt variants on the queries 
*"Which albums are good for studying?"*
*"What is the best phone"*

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