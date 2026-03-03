# Passage Analyzer

Analyzes book passages to extract:
1. **Word count** - Total words in passage
2. **Predominant emotion** - joy, sadness, anger, fear, disgust, surprise, or neutral (with confidence %)
3. **Possible books (2-3)** - Likely source books based on content
4. **Summary (2-3 sentences)** - Key points from the passage

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key (optional, for LLM enhancement)
echo GROQ_API_KEY=your_key_here > .env

# Run
streamlit run app.py
```

## Features
- **Paste text** or **upload PDF**
- Works **offline** (no API needed)
- Optional **LLM enhancement** via Groq API
- Automatic **fallback** if LLM fails

## Architecture
See [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for details.

```
app.py          → Streamlit UI
coordinator.py  → Orchestrates agents
offline_agent.py → Lexicon-based analysis (no API)
llm_agent.py    → Groq LLM analysis (optional)
pdf_utils.py    → PDF text extraction
```

## Requirements
- Python 3.8+
- Dependencies: `streamlit`, `requests`, `python-dotenv`, `PyMuPDF`

## Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, select `app.py`
4. Add secrets in **Settings → Secrets**:
   ```toml
   GROQ_API_KEY = "your_key_here"
   ```
5. Deploy!