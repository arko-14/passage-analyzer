"""
LLM Agent Module

Provides enhanced passage analysis using Groq API (Llama 3.1):
- Context-aware emotion detection
- Intelligent book identification
- Abstractive summarization

Includes rate limiting handling and automatic retries.
"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def _get_secret(key: str, default: str = "") -> str:
    """Get secret from environment or Streamlit secrets (for cloud deployment)."""
    value = os.getenv(key, "")
    if not value:
        try:
            import streamlit as st
            value = st.secrets.get(key, default)
        except:
            pass
    return value or default

ALLOWED_EMOTIONS = {"joy","sadness","anger","fear","disgust","surprise","neutral"}
MAX_TEXT_CHARS = 12000

def _truncate_text(text: str, max_chars: int = MAX_TEXT_CHARS) -> str:
    """Truncate text to avoid payload too large errors."""
    if len(text) <= max_chars:
        return text
    # Keep beginning and end for better context
    half = max_chars // 2
    return text[:half] + "\n\n[... truncated ...]\n\n" + text[-half:]

def _call_llm(prompt: str, max_retries: int = 3) -> str:
    """
    Send prompt to Groq API with retry logic.
    
    Args:
        prompt: The prompt to send
        max_retries: Number of retries on rate limit (429)
        
    Returns:
        LLM response text
        
    Raises:
        RuntimeError: If API key not set
        HTTPError: If request fails after retries
    """
    api_key = _get_secret("GROQ_API_KEY")
    base_url = _get_secret("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    model = _get_secret("GROQ_MODEL", "llama-3.1-8b-instant")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    for attempt in range(max_retries):
        r = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "Follow format strictly. No extra commentary."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
            },
            timeout=30,
        )
        
        if r.status_code == 429:
            # Rate limited - wait and retry with exponential backoff
            wait_time = (2 ** attempt) + 1  # 2s, 3s, 5s
            time.sleep(wait_time)
            continue
        
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    
    # If all retries exhausted, raise the last error
    r.raise_for_status()
    return ""

def run_llm(text: str):
    """
    Returns dict with keys: predominant_emotion, possible_books, summary
    Raises on failure (coordinator will fallback).
    """
    # Truncate large texts to avoid 413 Payload Too Large errors
    text = _truncate_text(text)
    
    # Combined prompt - single API call to avoid rate limiting
    combined_prompt = f"""
Analyze the following book passage and respond in EXACTLY this format:

EMOTION: <one of: joy, sadness, anger, fear, disgust, surprise, neutral>
BOOKS:
- <book title 1>
- <book title 2>
- <book title 3>
SUMMARY: <2-3 sentence summary>

Consider classic literary works like The Alchemist, Man's Search for Meaning, To Kill a Mockingbird, Pride and Prejudice, 1984, The Great Gatsby, etc.
Identify the actual source book if recognizable, or suggest similar classic books based on themes and style.

Passage:
\"\"\"{text}\"\"\"
""".strip()

    response = _call_llm(combined_prompt)
    
    # Parse the response
    lines = response.strip().split('\n')
    emo = "neutral"
    books = []
    summ = ""
    
    parsing_books = False
    summary_lines = []
    
    for line in lines:
        line_lower = line.lower().strip()
        if line_lower.startswith("emotion:"):
            emo = line.split(":", 1)[1].strip().lower()
            parsing_books = False
        elif line_lower.startswith("books:"):
            parsing_books = True
        elif line_lower.startswith("summary:"):
            parsing_books = False
            summ_part = line.split(":", 1)[1].strip()
            if summ_part:
                summary_lines.append(summ_part)
        elif parsing_books and line.strip().startswith("-"):
            book = line.strip().lstrip("-•").strip()
            if book:
                books.append(book)
        elif not parsing_books and summary_lines is not None and line.strip() and not line_lower.startswith(("emotion", "books")):
            # Continue collecting summary if it spans multiple lines
            if summary_lines:
                summary_lines.append(line.strip())
    
    summ = " ".join(summary_lines).strip()
    
    # Validate
    if emo not in ALLOWED_EMOTIONS:
        emo = "neutral"
    
    if len(summ) < 20:
        raise ValueError("LLM summary too short")
    
    books = books[:3]
    if len(books) < 2:
        raise ValueError("LLM returned <2 book guesses")

    return {
        "predominant_emotion": emo,
        "possible_books": books,
        "summary": summ,
    }