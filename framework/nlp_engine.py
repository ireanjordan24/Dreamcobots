"""
framework/nlp_engine.py

Rule-based / regex NLP engine for DreamCobots.
No external ML libraries required at runtime.
"""

from __future__ import annotations

import logging
import re
import string
from collections import Counter
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stopwords
# ---------------------------------------------------------------------------
_STOPWORDS: frozenset[str] = frozenset(
    {
        "a", "an", "the", "is", "it", "in", "on", "at", "to", "for",
        "of", "and", "or", "but", "not", "be", "was", "were", "are",
        "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "this", "that", "these",
        "those", "with", "from", "by", "about", "as", "into", "through",
        "i", "you", "we", "he", "she", "they", "my", "your", "our",
        "his", "her", "their", "me", "him", "us", "them",
    }
)

# ---------------------------------------------------------------------------
# Intent patterns  (order matters – first match wins)
# ---------------------------------------------------------------------------
_INTENT_PATTERNS: list[tuple[str, list[str]]] = [
    ("greeting",    [r"\b(hello|hi|hey|greetings|howdy)\b"]),
    ("farewell",    [r"\b(bye|goodbye|see you|take care|farewell)\b"]),
    ("question",    [r"^(what|who|where|when|why|how|which|can|could|is|are|do|does)\b"]),
    ("command",     [r"^(please\s+)?(find|get|show|list|search|give|tell|create|make|generate|calculate|analyze|analyse)\b"]),
    ("affirmation", [r"^(yes|yeah|yep|sure|ok|okay|absolutely|definitely|right|correct)\b"]),
    ("negation",    [r"^(no|nope|nah|not really|never)\b"]),
    ("help",        [r"\bhelp\b"]),
    ("status",      [r"\b(status|state|running|health)\b"]),
    ("unknown",     [r".*"]),
]

# ---------------------------------------------------------------------------
# Sentiment word lists
# ---------------------------------------------------------------------------
_POSITIVE_WORDS: frozenset[str] = frozenset(
    {
        "good", "great", "excellent", "amazing", "awesome", "fantastic",
        "wonderful", "best", "love", "happy", "pleased", "thrilled",
        "perfect", "brilliant", "superb", "positive", "outstanding",
        "impressive", "nice", "helpful", "easy", "fun", "enjoy",
        "beautiful", "incredible", "delightful", "glad", "grateful",
    }
)
_NEGATIVE_WORDS: frozenset[str] = frozenset(
    {
        "bad", "terrible", "awful", "horrible", "worst", "hate", "dislike",
        "sad", "angry", "frustrated", "disappointed", "poor", "wrong",
        "broken", "fail", "failed", "failure", "difficult", "hard",
        "ugly", "annoying", "useless", "problem", "issue", "error",
        "bug", "crash", "slow", "boring", "confusing", "complicated",
    }
)
_NEGATORS: frozenset[str] = frozenset({"not", "no", "never", "neither", "nor", "don't", "doesn't", "didn't", "won't", "can't", "cannot"})

# ---------------------------------------------------------------------------
# Simple entity patterns
# ---------------------------------------------------------------------------
_ENTITY_PATTERNS: list[tuple[str, str]] = [
    ("EMAIL",    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
    ("URL",      r"https?://[^\s]+"),
    ("PHONE",    r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"),
    ("DATE",     r"\b(?:\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{2}[/\-]\d{2})\b"),
    ("TIME",     r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APap][Mm])?\b"),
    ("MONEY",    r"\$\s*\d+(?:[,\d]*)?(?:\.\d{1,2})?|\b\d+(?:[,\d]*)?\s*(?:dollars?|USD|euros?|EUR)\b"),
    ("PERCENT",  r"\b\d+(?:\.\d+)?\s*%"),
    ("NUMBER",   r"\b\d+(?:,\d{3})*(?:\.\d+)?\b"),
]


class NLPEngine:
    """
    Rule-based NLP engine providing tokenisation, intent extraction,
    entity recognition, sentiment analysis, and basic summarisation.

    No external ML libraries are required at runtime.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger("NLPEngine")
        # Pre-compile all patterns
        self._intent_compiled: list[tuple[str, list[re.Pattern[str]]]] = [
            (intent, [re.compile(p, re.IGNORECASE) for p in patterns])
            for intent, patterns in _INTENT_PATTERNS
        ]
        self._entity_compiled: list[tuple[str, re.Pattern[str]]] = [
            (label, re.compile(pattern, re.IGNORECASE))
            for label, pattern in _ENTITY_PATTERNS
        ]
        self.logger.debug("NLPEngine initialised.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def tokenize(self, text: str) -> list[str]:
        """
        Tokenise *text* into a list of lowercase, punctuation-stripped tokens
        with stopwords removed.

        Args:
            text: Raw input string.

        Returns:
            List of token strings.
        """
        if not text or not text.strip():
            return []
        # Lower-case and split on whitespace / punctuation
        tokens = re.findall(r"\b[a-zA-Z0-9']+\b", text.lower())
        # Remove stopwords and very short tokens
        return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]

    def extract_intent(self, text: str) -> str:
        """
        Classify the dominant intent of *text* using regex rules.

        Args:
            text: Input message.

        Returns:
            One of: ``greeting``, ``farewell``, ``question``, ``command``,
            ``affirmation``, ``negation``, ``help``, ``status``, ``unknown``.
        """
        if not text or not text.strip():
            return "unknown"
        cleaned = text.strip().lower()
        for intent, patterns in self._intent_compiled:
            for pattern in patterns:
                if pattern.search(cleaned):
                    return intent
        return "unknown"

    def extract_entities(self, text: str) -> list[dict[str, str]]:
        """
        Extract named entities from *text* using regex patterns.

        Args:
            text: Input string.

        Returns:
            List of dicts with ``type`` and ``value`` keys.
        """
        if not text or not text.strip():
            return []
        entities: list[dict[str, str]] = []
        seen: set[str] = set()
        for label, pattern in self._entity_compiled:
            for match in pattern.finditer(text):
                value = match.group(0).strip()
                key = f"{label}:{value}"
                if key not in seen:
                    seen.add(key)
                    entities.append({"type": label, "value": value})
        return entities

    def sentiment_analysis(self, text: str) -> dict[str, float]:
        """
        Perform simple lexicon-based sentiment analysis.

        Args:
            text: Input string.

        Returns:
            Dict with ``positive``, ``negative``, ``neutral`` scores
            (each in ``[0.0, 1.0]``) and a ``label`` key
            (``"positive"``, ``"negative"``, or ``"neutral"``).
        """
        if not text or not text.strip():
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0, "label": "neutral"}

        tokens = re.findall(r"\b[a-zA-Z']+\b", text.lower())
        pos_score = 0
        neg_score = 0
        negation_active = False

        for token in tokens:
            if token in _NEGATORS:
                negation_active = True
                continue
            if token in _POSITIVE_WORDS:
                if negation_active:
                    neg_score += 1
                else:
                    pos_score += 1
                negation_active = False
            elif token in _NEGATIVE_WORDS:
                if negation_active:
                    pos_score += 1
                else:
                    neg_score += 1
                negation_active = False
            else:
                negation_active = False

        total = pos_score + neg_score
        if total == 0:
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0, "label": "neutral"}

        pos_ratio = pos_score / total
        neg_ratio = neg_score / total
        # Scale to leave room for neutral
        positive = round(pos_ratio * 0.9, 4)
        negative = round(neg_ratio * 0.9, 4)
        neutral = round(1.0 - positive - negative, 4)
        label = (
            "positive" if positive > negative
            else "negative" if negative > positive
            else "neutral"
        )
        return {"positive": positive, "negative": negative, "neutral": neutral, "label": label}

    def summarize(self, text: str, max_length: int = 150) -> str:
        """
        Produce an extractive summary of *text* limited to *max_length* chars.

        Uses a simple TF-based sentence scoring approach.

        Args:
            text: Input document.
            max_length: Maximum character length of the summary.

        Returns:
            A summary string.
        """
        if not text or not text.strip():
            return ""

        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        if len(sentences) == 1:
            return sentences[0][:max_length]

        # Score each sentence by term frequency of its tokens
        all_tokens = self.tokenize(text)
        if not all_tokens:
            return sentences[0][:max_length]

        tf: Counter[str] = Counter(all_tokens)

        def score_sentence(sent: str) -> float:
            toks = self.tokenize(sent)
            if not toks:
                return 0.0
            return sum(tf[t] for t in toks) / len(toks)

        scored = [(score_sentence(s), i, s) for i, s in enumerate(sentences)]
        scored.sort(key=lambda x: x[0], reverse=True)

        # Take top sentences until we reach max_length
        selected: list[tuple[int, str]] = []
        total_len = 0
        for _, idx, sent in scored:
            if total_len + len(sent) + 1 > max_length:
                break
            selected.append((idx, sent))
            total_len += len(sent) + 1

        if not selected:
            return scored[0][2][:max_length]

        # Restore original order
        selected.sort(key=lambda x: x[0])
        return " ".join(s for _, s in selected)[:max_length]
