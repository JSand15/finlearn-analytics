"""Behavioral finance memo quality analyzer."""

import re
from typing import Dict, List, Union

from .utils import validate_text
from .biases import detect_biases

# Phrases associated with overconfidence bias in investment memos
_OVERCONFIDENCE_PHRASES = [
    "guaranteed",
    "certain to",
    "will definitely",
    "no risk",
    "risk-free",
    "100%",
    "cannot fail",
    "sure thing",
    "obvious",
    "clearly will",
    "without a doubt",
    "no doubt",
    "impossible to lose",
    "can't go wrong",
]

# Simple positive/negative word lists for lightweight sentiment scoring
_POSITIVE_WORDS = {
    "growth", "profit", "gain", "strong", "outperform", "increase", "positive",
    "upside", "opportunity", "bullish", "recover", "improve", "robust", "solid",
    "momentum", "surge", "rally", "exceed", "beat", "favorable",
}
_NEGATIVE_WORDS = {
    "loss", "decline", "risk", "weak", "underperform", "decrease", "negative",
    "downside", "threat", "bearish", "drop", "fall", "miss", "concern",
    "volatile", "uncertain", "headwind", "pressure", "slump", "deteriorate",
}


def analyze_memo_quality(memo_text: str) -> Dict[str, Union[int, float, str, List[str]]]:
    """Analyze the quality and behavioral-finance characteristics of an investment memo.

    Evaluates word count, tone (sentiment), overconfidence language, structural
    clarity, and produces a plain-English recommendation for improvement.

    Args:
        memo_text: The full text of the investment memo as a string.

    Returns:
        Dictionary with the following keys:
            - word_count (int): Total number of words.
            - sentiment_score (float): Score from -1.0 (very negative) to
              +1.0 (very positive) based on financial vocabulary.
            - overconfidence_flags (list[str]): Phrases detected that indicate
              overconfidence bias.
            - behavioral_biases (list[str]): Keys of every behavioral-finance bias
              detected in the memo via the full catalog (see finlearn.biases). A
              superset of overconfidence detection, covering 60+ biases.
            - clarity_score (int): Estimated clarity from 0 to 100, based on
              average sentence length and vocabulary diversity.
            - recommendation (str): Plain-English suggestion for improvement.

    Raises:
        TypeError: If memo_text is not a string.
        ValueError: If memo_text is empty or whitespace-only.

    Example:
        >>> memo = "This investment is guaranteed to grow. Strong momentum and profit."
        >>> result = analyze_memo_quality(memo)
        >>> "guaranteed" in result['overconfidence_flags']
        True
    """
    text = validate_text(memo_text, "memo_text")

    # Word count: include alphanumeric tokens so financial terms like "Q3", "2024",
    # and "15%" are counted (strip trailing punctuation but keep the token).
    word_count = len(re.findall(r"\S+", text))

    # Sentiment scoring uses only alphabetic words against the finance lexicon.
    alpha_words = re.findall(r"[A-Za-z']+", text)
    lower_words = [w.lower() for w in alpha_words]

    # Sentiment score
    pos_count = sum(1 for w in lower_words if w in _POSITIVE_WORDS)
    neg_count = sum(1 for w in lower_words if w in _NEGATIVE_WORDS)
    total_sentiment = pos_count + neg_count
    if total_sentiment == 0:
        sentiment_score = 0.0
    else:
        sentiment_score = round((pos_count - neg_count) / total_sentiment, 4)

    # Overconfidence flags (kept for backward compatibility)
    text_lower = text.lower()
    overconfidence_flags = [phrase for phrase in _OVERCONFIDENCE_PHRASES if phrase in text_lower]

    # Full behavioral-bias screen using the catalog in finlearn.biases.
    behavioral_biases = [b["key"] for b in detect_biases(text)]

    # Clarity score: penalize very long sentences and low vocabulary diversity
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = len(sentences)

    avg_sentence_length = word_count / num_sentences if num_sentences > 0 else word_count
    # Ideal avg sentence length ~15-20 words; penalize >30
    length_penalty = max(0, (avg_sentence_length - 20) * 2)

    alpha_word_count = len(lower_words)
    unique_ratio = len(set(lower_words)) / alpha_word_count if alpha_word_count > 0 else 0
    diversity_bonus = unique_ratio * 30  # up to 30 points for vocabulary diversity

    clarity_score = int(max(0, min(100, 70 - length_penalty + diversity_bonus)))

    # Build recommendation
    issues = []
    if overconfidence_flags:
        issues.append(
            f"Remove overconfident language ({', '.join(overconfidence_flags[:3])})"
        )
    # Surface other behavioral biases beyond overconfidence (which is already covered above).
    other_biases = [b for b in behavioral_biases if b != "overconfidence"]
    if other_biases:
        issues.append(
            f"Address behavioral biases ({', '.join(other_biases[:3])})"
        )
    if avg_sentence_length > 25:
        issues.append("Shorten sentences for clarity")
    if word_count < 100:
        issues.append("Expand analysis — memo is brief")
    if sentiment_score > 0.6:
        issues.append("Balance tone; memo reads as overly optimistic")
    elif sentiment_score < -0.6:
        issues.append("Balance tone; memo reads as overly pessimistic")

    if issues:
        recommendation = "Suggested improvements: " + "; ".join(issues) + "."
    else:
        recommendation = "Memo quality is good. No major behavioral finance concerns detected."

    return {
        "word_count": word_count,
        "sentiment_score": sentiment_score,
        "overconfidence_flags": overconfidence_flags,
        "behavioral_biases": behavioral_biases,
        "clarity_score": clarity_score,
        "recommendation": recommendation,
    }
