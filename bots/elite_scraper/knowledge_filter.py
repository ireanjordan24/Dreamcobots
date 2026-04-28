"""
Knowledge Filter
================

Scores and filters scraped items so each Elite Scraper retains only the
most relevant knowledge for its parent bot.

The filter works by:
  1. Checking whether the item contains any of the bot's keyword tags.
  2. Applying a configurable minimum relevance threshold (default 40/100).
  3. Optionally de-duplicating identical or near-identical content.

Usage
-----
    from bots.elite_scraper.knowledge_filter import KnowledgeFilter

    filt = KnowledgeFilter(
        keywords=["scraping", "github", "workflow"],
        min_score=50.0,
    )
    items = [
        {"content": "Advanced GitHub Actions scraping workflow tutorial"},
        {"content": "Random unrelated text about cooking"},
    ]
    kept, dropped = filt.filter(items)
    # kept → first item (score ≥ 50)
    # dropped → second item (score < 50)
"""

from __future__ import annotations

import hashlib
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# KnowledgeFilter
# ---------------------------------------------------------------------------

class KnowledgeFilter:
    """
    Scores scraped items and returns only those above a relevance threshold.

    Parameters
    ----------
    keywords : list[str]
        Domain-specific terms for the parent bot.  Items containing more
        keywords score higher.
    min_score : float
        Minimum relevance score (0–100) to keep an item.  Default is 40.
    deduplicate : bool
        When True, items with identical content hashes are dropped after
        the first occurrence.
    """

    def __init__(
        self,
        keywords: Optional[List[str]] = None,
        min_score: float = 40.0,
        deduplicate: bool = True,
    ) -> None:
        self._keywords: List[str] = [k.lower() for k in (keywords or [])]
        self._min_score = max(0.0, min(100.0, float(min_score)))
        self._deduplicate = deduplicate
        self._seen_hashes: set = set()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score(self, item: dict) -> float:
        """
        Compute a relevance score (0–100) for a single scraped item.

        The scoring model:
          * Base score = 50 if no keywords are configured (neutral).
          * Keyword hits: +10 per unique keyword found in content/title
            (capped at +50 total from keywords).
          * Length bonus: +5 if content is >= 100 characters.
          * Length penalty: −20 if content is < 10 characters.

        Parameters
        ----------
        item : dict
            Must contain at least one of ``"content"``, ``"title"``,
            ``"description"``, or ``"text"`` keys.

        Returns
        -------
        float
            Score in [0, 100].
        """
        text = self._extract_text(item).lower()
        if not text:
            return 0.0

        if not self._keywords:
            base = 50.0
        else:
            hits = sum(1 for kw in self._keywords if kw in text)
            base = min(100.0, hits * 10.0)

        # Length bonuses / penalties
        length = len(text)
        if length >= 100:
            base = min(100.0, base + 5.0)
        elif length < 10:
            base = max(0.0, base - 20.0)

        return round(base, 2)

    def filter(self, items: List[dict]) -> Tuple[List[dict], List[dict]]:
        """
        Split *items* into ``(kept, dropped)`` based on relevance score
        and (optionally) deduplication.

        Parameters
        ----------
        items : list[dict]
            List of raw scraped items.

        Returns
        -------
        tuple[list[dict], list[dict]]
            ``(kept, dropped)`` — items meeting the threshold and those
            that do not.
        """
        kept: List[dict] = []
        dropped: List[dict] = []

        for item in items:
            # Deduplication check
            if self._deduplicate:
                h = self._content_hash(item)
                if h in self._seen_hashes:
                    dropped.append(item)
                    continue
                self._seen_hashes.add(h)

            score = self.score(item)
            enriched = {**item, "relevance_score": score}
            if score >= self._min_score:
                kept.append(enriched)
            else:
                dropped.append(enriched)

        return kept, dropped

    def reset_dedup_cache(self) -> None:
        """Clear the deduplication hash cache."""
        self._seen_hashes.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_text(item: dict) -> str:
        for key in ("content", "title", "description", "text", "body", "name"):
            val = item.get(key)
            if val and isinstance(val, str):
                return val
        return str(item)

    @staticmethod
    def _content_hash(item: dict) -> str:
        text = KnowledgeFilter._extract_text(item)
        return hashlib.md5(text.encode("utf-8", errors="replace")).hexdigest()
