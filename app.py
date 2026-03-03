"""
Passage Analyzer - Streamlit UI

Main entry point for the web application. Provides interface for:
- Text input (paste) or PDF upload
- Optional LLM enhancement
- Display of analysis results (word count, emotion, books, summary)
"""
import streamlit as st
from pdf_utils import extract_text_from_pdf
from coordinator import analyze

st.set_page_config(page_title="Passage Analyzer (Mini-Agents)", layout="wide")
st.title("Passage Analyzer (Mini-Agent + Fallback)")

input_method = st.radio("Input type:", ["Paste Text", "Upload PDF"], horizontal=True)

text = ""
if input_method == "Paste Text":
    text = st.text_area("Paste passage:", height=280)
else:
    up = st.file_uploader("Upload PDF (text-based preferred)", type=["pdf"])
    if up:
        text = extract_text_from_pdf(up)
        if text.startswith("ERROR_READING_PDF"):
            st.error(text)
        elif not text.strip():
            st.warning("No extractable text found. PDF may be scanned (OCR not enabled).")

use_llm = st.checkbox("Improve with LLM (optional)", value=False)
show_debug = st.checkbox("Show debug", value=False)

if st.button("Analyze", type="primary"):
    if not text.strip():
        st.error("Please provide some text or a readable PDF.")
    else:
        with st.spinner("Analyzing..."):
            result = analyze(text, use_llm=use_llm)

        st.subheader("✅ Results")
        st.write("**1) Total number of words:**", result["word_count"])
        
        emotion = result["predominant_emotion"]
        confidence = result.get("emotion_confidence")
        if confidence is not None:
            st.write(f"**2) Predominant emotion:** {emotion} (confidence: {int(confidence * 100)}%)")
        else:
            st.write(f"**2) Predominant emotion:** {emotion} (via LLM)")
        
        st.write("**3) Possible books (2–3):**", result["possible_books"])
        st.write("**4) Summary (2–3 sentences):**")
        st.write(result["summary"])

        if result["debug"]["llm_errors"]:
            st.warning("LLM failed; fallback used:\n- " + "\n- ".join(result["debug"]["llm_errors"]))

        if show_debug:
            st.subheader("Debug")
            st.json(result["debug"])