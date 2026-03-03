from __future__ import annotations
from typing import Dict, Any, List

from offline_agent import run_offline
from llm_agent import run_llm

def analyze(text: str, use_llm: bool) -> Dict[str, Any]:
    offline = run_offline(text)
    llm = None
    llm_errors: List[str] = []

    if use_llm:
        try:
            llm = run_llm(text)
        except Exception as e:
            llm_errors.append(str(e))
            llm = None

    # Arbiter: choose per-field (LLM if available + sane, else offline)
    emotion_confidence = offline.get("emotion_confidence", 0.0)
    final = {
        "word_count": offline["word_count"],  # always offline exact
        "predominant_emotion": (llm["predominant_emotion"] if llm else offline["predominant_emotion"]),
        "emotion_confidence": emotion_confidence,
        "possible_books": (llm["possible_books"] if llm else offline["possible_books"]),
        "summary": (llm["summary"] if llm else offline["summary"]),
        "debug": {
            "used_llm": bool(llm),
            "llm_errors": llm_errors,
            "offline_emotion_scores": offline.get("emotion_scores", {}),
            "offline_emotion_confidence": emotion_confidence,
        }
    }
    return final