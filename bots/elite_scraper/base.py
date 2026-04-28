"""
Elite Scraper Base
==================

Base class for per-bot Elite Scrapers.  Each bot should subclass
``EliteScraperBase`` and implement ``_fetch_raw(query)`` to pull data
from its preferred source (GitHub API, web pages, databases, etc.).

The base class handles:
  * Applying the ``KnowledgeFilter`` to keep only high-relevance items.
  * Logging results to the ``BotLibraryManager`` scraper-run table.
  * Storing retained entries as learning data in the database.
  * Providing a ``run(query)`` convenience method that performs the full
    scrape → filter → store cycle in one call.

Usage
-----
    from bots.elite_scraper.base import EliteScraperBase

    class MyBotScraper(EliteScraperBase):
        bot_name = "my_bot"
        keywords  = ["workflow", "automation", "ci"]

        def _fetch_raw(self, query: str) -> list:
            # Return a list of dicts with at least a "content" key.
            return [{"content": "some scraped text", "source_url": "..."}]

    scraper = MyBotScraper(db_manager=mgr)
    result  = scraper.run("github actions automation")
    print(result["items_retained"], "items kept")
"""

from __future__ import annotations

import time
from typing import List, Optional

from bots.elite_scraper.knowledge_filter import KnowledgeFilter


# ---------------------------------------------------------------------------
# EliteScraperBase
# ---------------------------------------------------------------------------

class EliteScraperBase:
    """
    Abstract base for per-bot Elite Scrapers.

    Class attributes to override in subclasses
    ------------------------------------------
    bot_name : str
        Identifier used when storing data in the library manager.
    scraper_type : str
        Label for the scraper (e.g. ``"github"``, ``"web"``, ``"arxiv"``).
    keywords : list[str]
        Domain keywords used by :class:`~KnowledgeFilter` to score items.
    min_relevance : float
        Minimum score (0–100) to retain an item.

    Parameters
    ----------
    db_manager : optional
        A ``BotLibraryManager`` instance.  When provided, scrape results
        are automatically persisted.  Pass ``None`` (default) for stateless
        / test usage.
    min_relevance : float, optional
        Override the class-level default threshold.
    keywords : list[str], optional
        Override the class-level keyword list.
    """

    bot_name: str = "generic_bot"
    scraper_type: str = "generic"
    keywords: List[str] = []
    min_relevance: float = 40.0

    def __init__(
        self,
        db_manager=None,
        min_relevance: Optional[float] = None,
        keywords: Optional[List[str]] = None,
    ) -> None:
        self._db = db_manager
        _min = min_relevance if min_relevance is not None else self.__class__.min_relevance
        _kws = keywords if keywords is not None else list(self.__class__.keywords)
        self._filter = KnowledgeFilter(keywords=_kws, min_score=_min)

    # ------------------------------------------------------------------
    # Abstract method (subclasses must implement)
    # ------------------------------------------------------------------

    def _fetch_raw(self, query: str) -> List[dict]:
        """Fetch raw items for *query*.  Override in each bot scraper.

        Returns
        -------
        list[dict]
            Each dict must contain at least a ``"content"`` key (or one of
            the other keys recognised by :class:`~KnowledgeFilter`).
        """
        return []

    # ------------------------------------------------------------------
    # Core scrape pipeline
    # ------------------------------------------------------------------

    def scrape(self, query: str) -> dict:
        """
        Execute the full scrape → filter cycle for *query*.

        Returns
        -------
        dict
            Keys: ``query``, ``items_found``, ``items_retained``,
            ``items_discarded``, ``kept``, ``dropped``.
        """
        raw = self._fetch_raw(query)
        kept, dropped = self._filter.filter(raw)
        return {
            "query": query,
            "items_found": len(raw),
            "items_retained": len(kept),
            "items_discarded": len(dropped),
            "kept": kept,
            "dropped": dropped,
        }

    def run(self, query: str, data_type: str = "scraped") -> dict:
        """
        Full scrape cycle: fetch → filter → store.

        Persists retained entries and the run log to ``db_manager`` when
        one was provided at construction time.

        Parameters
        ----------
        query : str
            Search query passed to ``_fetch_raw``.
        data_type : str
            Category tag stored with each learning entry.

        Returns
        -------
        dict
            Scrape summary including ``items_retained`` and ``items_discarded``.
        """
        start = time.time()
        result = self.scrape(query)
        duration_ms = int((time.time() - start) * 1000)

        if self._db is not None:
            # Store each retained item as learning data
            for item in result["kept"]:
                content = str(
                    item.get("content") or item.get("title") or item.get("text") or item
                )
                source = str(item.get("source_url") or item.get("url") or self.scraper_type)
                self._db.store_learning(
                    bot_name=self.bot_name,
                    data_type=data_type,
                    content=content,
                    source=source,
                    relevance_score=item.get("relevance_score", 50.0),
                )

            # Log the scraper run
            self._db.log_scraper_run(
                bot_name=self.bot_name,
                query=query,
                items_found=result["items_found"],
                items_retained=result["items_retained"],
                scraper_type=self.scraper_type,
                status="success",
                duration_ms=duration_ms,
            )

        return {
            "bot_name": self.bot_name,
            "query": query,
            "scraper_type": self.scraper_type,
            "items_found": result["items_found"],
            "items_retained": result["items_retained"],
            "items_discarded": result["items_discarded"],
            "duration_ms": duration_ms,
        }

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def get_knowledge(
        self, data_type: Optional[str] = None, limit: int = 50
    ) -> List[dict]:
        """Return retained learning entries from the database.

        Requires ``db_manager`` to be set.
        """
        if self._db is None:
            return []
        return self._db.get_retained_learning(
            self.bot_name, data_type=data_type, limit=limit
        )

    def purge_stale(self, threshold: Optional[float] = None) -> int:
        """Discard low-relevance entries below *threshold*.

        Returns
        -------
        int
            Number of entries purged.
        """
        if self._db is None:
            return 0
        return self._db.purge_low_relevance(self.bot_name, threshold=threshold)
