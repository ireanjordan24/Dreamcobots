"""
github_scraper.py — GitHub scraper module.

Ingests repositories, READMEs, and code artefacts from GitHub to feed
the DreamCo global learning pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GitHubRepo:
    """Represents a scraped GitHub repository."""

    full_name: str
    description: Optional[str]
    url: str
    stars: int
    language: Optional[str]
    topics: List[str] = field(default_factory=list)
    readme_excerpt: Optional[str] = None


class GitHubScraper:
    """
    Scrapes GitHub repositories relevant to AI/ML topics.

    Parameters
    ----------
    token : str | None
        Optional GitHub personal-access token for authenticated requests.
    max_results : int
        Maximum number of repositories to return per search.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None, max_results: int = 50):
        self.token = token
        self.max_results = max_results
        self._ingested: List[GitHubRepo] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def search_repositories(self, query: str, language: Optional[str] = None) -> List[GitHubRepo]:
        """
        Search GitHub for repositories matching *query*.

        Parameters
        ----------
        query : str
            Topic or keyword string.
        language : str | None
            Optional programming language filter.

        Returns
        -------
        list[GitHubRepo]
        """
        repos = self._fetch_repos(query, language)
        self._ingested.extend(repos)
        return repos

    def get_ingested(self) -> List[GitHubRepo]:
        """Return all repositories collected during this session."""
        return list(self._ingested)

    def clear(self) -> None:
        """Clear the in-memory ingestion cache."""
        self._ingested = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_repos(self, query: str, language: Optional[str]) -> List[GitHubRepo]:
        """Return mock repository records for *query*."""
        results: List[GitHubRepo] = []
        for i in range(min(3, self.max_results)):
            lang = language or "Python"
            results.append(
                GitHubRepo(
                    full_name=f"dreamco-org/{query.replace(' ', '-')}-{i + 1}",
                    description=f"Sample repo #{i + 1} for query '{query}'",
                    url=f"https://github.com/dreamco-org/{query.replace(' ', '-')}-{i + 1}",
                    stars=(i + 1) * 100,
                    language=lang,
                    topics=[query.lower(), "ai", "machine-learning"],
                    readme_excerpt=f"README excerpt for {query} repo #{i + 1}.",
                )
            )
        return results
