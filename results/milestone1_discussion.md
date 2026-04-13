## Milestone 1: Retrieval Evaluation (BM25 vs Semantic Search)

### Query 1: "taylor swift album"

#### BM25 Results
- Mostly relevant results containing Taylor Swift albums (e.g., *Red Deluxe Edition*, *Greatest Hits*).
- One irrelevant result (*CTI Masters of the Guitar*).

#### Semantic Results
- Also retrieves Taylor Swift albums.
- Includes slightly unrelated items (e.g., *Dolly Parton Gospel Collection*).

#### Analysis
BM25 performs slightly better because it matches the exact keyword "Taylor Swift". Semantic search retrieves relevant results but introduces more noise. Both methods perform reasonably well for this query.

---

### Query 2: "ed sheeran songs"

#### BM25 Results
- Top result is correct (*Ed Sheeran – Divide Deluxe Edition*).
- Several irrelevant results (e.g., anime-related songs, unrelated CDs).

#### Semantic Results
- Also retrieves the correct Ed Sheeran album.
- Includes unrelated artists (e.g., Chris Lane, Gunna).

#### Analysis
Both methods struggle here. BM25 benefits from exact keyword matching for the top result, but overall precision is low. Semantic search retrieves conceptually related "songs" but lacks precision.

---

### Query 3: "classical piano music"

#### BM25 Results
- Some relevant results (e.g., *Mozart Piano Sonatas*).
- Several partially relevant classical works not focused on piano.

#### Semantic Results
- More consistently relevant (e.g., *Oceanside Piano*, *Mozart Piano Sonatas*).
- Better alignment with "piano music" intent.

#### Analysis
Semantic search performs better because it captures the concept of "piano music" more effectively. BM25 retrieves classical music but not always piano-specific.

---

### Query 4: "jazz instrumental album"

#### BM25 Results
- Strong results (e.g., Jazz Crusaders, Jazz Istanbul).
- Mostly relevant instrumental jazz albums.

#### Semantic Results
- Also highly relevant (e.g., Benny Carter collection, Jazz albums).
- Slightly broader but still appropriate.

#### Analysis
Both methods perform well. BM25 has a slight edge due to precise keyword matching, while semantic search is slightly broader but still effective.

---

### Query 5: "music to relax while studying"

#### BM25 Results
- Mostly irrelevant (e.g., *Easy Listening Hits*, *Music Martinis*).
- Does not capture "studying" or "relax" intent.

#### Semantic Results
- Strong matches (e.g., *Oceanside Piano*, calming instrumental music).
- Clearly aligned with relaxation and focus.

#### Analysis
Semantic search clearly outperforms BM25. BM25 fails due to lack of keyword overlap, while semantic search captures the intended meaning.

---

### Query 6: "songs for a long road trip"

#### BM25 Results
- Mostly irrelevant (e.g., *Road to Hana Guide*, unrelated albums).
- Fails to interpret "road trip" context.

#### Semantic Results
- Some relevant results (e.g., albums described as good for driving or travel).
- Still slightly noisy.

#### Analysis
Semantic search performs better, although not perfectly. BM25 fails completely due to lack of keyword overlap.

---

### Query 7: "calming instrumental music"

#### BM25 Results
- Mixed results (e.g., pet calming music device, unrelated albums).
- Weak understanding of "calming".

#### Semantic Results
- Better matches (e.g., meditation music, instrumental tracks).
- Still includes some noise.

#### Analysis
Semantic search performs better overall because it understands "calming" as a concept. BM25 retrieves partial matches but lacks consistency.

---

### Query 8: "upbeat music for working out"

#### BM25 Results
- Mostly irrelevant (e.g., children’s music, Christmas albums).
- Does not capture "workout" intent.

#### Semantic Results
- Some relevant results (e.g., workout mix player, energetic tracks like *Happy Place*).
- Still slightly noisy.

#### Analysis
Semantic search performs better. BM25 fails due to lack of direct keyword matches for "workout".

---

### Query 9: "best album for heartbreak"

#### BM25 Results
- Matches generic "best album" phrases.
- Completely ignores emotional intent.

#### Semantic Results
- Slightly better results (e.g., *Taylor Swift – Speak Now*, *Lana Del Rey*).
- Still not strongly aligned with heartbreak context.

#### Analysis
Both methods struggle. BM25 fails entirely, while semantic search performs slightly better but still lacks emotional understanding.

---

### Query 10: "music without lyrics for focus"

#### BM25 Results
- Mostly irrelevant (albums with lyrics, unrelated content).
- Does not capture "instrumental" intent.

#### Semantic Results
- Includes some instrumental music (e.g., piano sonatas, Chinese instrumental music).
- Still partially noisy.

#### Analysis
Semantic search performs better but is not perfect. BM25 fails due to lack of exact keyword matching.

---

## Overall Insights

- BM25 performs well for keyword-based queries such as artist names and genres.
- Semantic search performs better for intent-based queries like "music for studying" or "relaxing music".
- BM25 relies heavily on exact keyword overlap and fails when queries are vague or descriptive.
- Semantic search captures contextual meaning but sometimes retrieves broader or less precise results.
- Both methods struggle with complex queries involving subjective or emotional intent (e.g., "heartbreak").
- A hybrid approach combining BM25 and semantic search could improve retrieval performance.