# System Design: Passage Analyzer

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI (app.py)                  │
│                   Text Input / PDF Upload                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Coordinator (coordinator.py)              │
│              Orchestrates agents + Arbiter logic            │
└──────────┬─────────────────────────────────┬────────────────┘
           │                                 │
           ▼                                 ▼
┌──────────────────────┐          ┌──────────────────────────┐
│   Offline Agent      │          │      LLM Agent           │
│  (offline_agent.py)  │          │    (llm_agent.py)        │
│                      │          │                          │
│  • Word count        │          │  • Groq API (Llama 3.1)  │
│  • Lexicon emotion   │          │  • Better summaries      │
│  • Extractive summary│          │  • Smarter book guesses  │
│  • Keyword book match│          │  • Context-aware emotion │
└──────────────────────┘          └──────────────────────────┘
           │                                 │
           └────────────┬────────────────────┘
                        ▼
              ┌─────────────────┐
              │  Final Result   │
              │  (Arbiter)      │
              └─────────────────┘
```

## Design Decisions

### 1. Dual-Agent Architecture
- **Offline Agent**: Fast, reliable, no API dependency. Works without internet.
- **LLM Agent**: Higher quality results but depends on external API.
- **Rationale**: Provides fallback reliability while offering enhanced analysis when available.

### 2. Arbiter Pattern
The coordinator acts as an arbiter that:
- Always uses offline word count (exact, no estimation)
- Prefers LLM for emotion/summary/books when available
- Falls back to offline on any LLM failure (rate limits, network issues)

### 3. Single API Call Design
Combined all LLM queries (emotion + books + summary) into one prompt to:
- Reduce rate limiting (429 errors)
- Lower latency
- Minimize API costs

### 4. Emotion Detection

**Offline Lexicon-Based:**
- 600+ emotion words across 6 categories + neutral
- Intensifier boosting ("very happy" → 1.5x score)
- Diminisher reduction ("slightly sad" → 0.5x score)
- Confidence score = top_emotion / total_emotion_words

**LLM-Based:**
- Context-aware understanding
- Better for sarcasm, nuance, complex passages

### 5. Summary Generation

**Offline (Extractive):**
- Scores sentences by word frequency importance
- Picks top 3 most representative sentences
- Preserves original text (no hallucination risk)

**LLM (Abstractive):**
- Generates new condensed text
- More natural and coherent
- May miss specific details

### 6. Book Identification
- Keyword matching against known book vocabularies
- Focuses on classic literary works per assignment requirements
- LLM can identify books not in predefined list

## Error Handling

| Error | Handling |
|-------|----------|
| 413 Payload Too Large | Truncate text to 12K chars (keep start + end) |
| 429 Rate Limited | Retry 3x with exponential backoff (2s, 3s, 5s) |
| API Timeout | 30s timeout, fallback to offline |
| Invalid LLM Response | Parse validation, fallback to offline |

## Trade-offs

| Choice | Pros | Cons |
|--------|------|------|
| Lexicon emotion | Fast, explainable, offline | Misses context/sarcasm |
| Extractive summary | No hallucination, fast | Less fluent |
| Single LLM call | Fewer rate limits | Harder to parse response |
| Keyword book match | Fast, predictable | Limited to known books |
