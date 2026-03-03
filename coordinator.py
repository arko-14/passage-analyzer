"""
Coordinator Module

Orchestrates the analysis pipeline:
1. Always runs offline analysis (fast, reliable)
2. Optionally runs LLM analysis for enhanced results
3. Arbitrates between results (LLM preferred when available)
4. Falls back to offline if LLM fails
"""
from __future__ import annotations
from typing import Dict, Any, List

from offline_agent import run_offline
from llm_agent import run_llm


def analyze(text: str, use_llm: bool) -> Dict[str, Any]:
    """
    Main analysis function.
    
    Args:
        text: The passage to analyze
        use_llm: Whether to attempt LLM enhancement
        
    Returns:
        Dict containing word_count, predominant_emotion, emotion_confidence,
        possible_books, summary, and debug info
    """
    offline = run_offline(text)
    llm = None
    llm_errors: List[str] = []

    if use_llm:
        try:
            llm = run_llm(text)
        except Exception as e:
            llm_errors.append(str(e))
            llm = None

    used_llm = bool(llm)
    emotion_confidence = None if used_llm else offline.get("emotion_confidence", 0.0)
    
    return {
        "word_count": offline["word_count"],
        "predominant_emotion": llm["predominant_emotion"] if llm else offline["predominant_emotion"],
        "emotion_confidence": emotion_confidence,
        "possible_books": llm["possible_books"] if llm else offline["possible_books"],
        "summary": llm["summary"] if llm else offline["summary"],
        "debug": {
            "used_llm": used_llm,
            "llm_errors": llm_errors,
            "offline_emotion_scores": offline.get("emotion_scores", {}),
            "offline_emotion_confidence": offline.get("emotion_confidence", 0.0),
        }
    }