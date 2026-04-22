"""
DreamCo GitHub Analyzer Bot

Autonomously discovers, extracts, and learns from top-of-the-line bot
systems published on GitHub.  Insights are used to evolve DreamCo bot
configurations and workflows.

Responsibilities
----------------
1. Autonomous Discovery   — search public GitHub repositories for trending
   bot systems across any category using the GitHub Search API.
2. Data Extraction        — fetch and parse workflows.json, bot metadata,
   and automation schemas from discovered repositories.
3. Integration            — generate new DreamCo-compatible bot configuration
   snippets from extracted patterns.
4. AI-Powered Learning    — categorise repositories, rank them by relevance,
   and surface best-practice recommendations.
"""

import json
import math
import base64
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class GitHubAnalyzerBotError(Exception):
    """Base error for the GitHub Analyzer Bot."""


class GitHubAPIError(GitHubAnalyzerBotError):
    """Raised when a GitHub API call fails."""


# ---------------------------------------------------------------------------
# Bot categories understood by the AI categoriser
# ---------------------------------------------------------------------------

BOT_CATEGORIES = [
    "automation",
    "chatbot",
    "ci_cd",
    "crypto_trading",
    "customer_support",
    "data_pipeline",
    "ecommerce",
    "finance",
    "lead_generation",
    "marketing",
    "real_estate",
    "security",
    "social_media",
    "web_scraping",
    "workflow_orchestration",
]

# Keyword → category mapping used by the lightweight AI categoriser.
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "automation":             ["automat", "rpa", "robot"],
    "chatbot":                ["chatbot", "chat bot", "conversational", "nlp", "dialogue"],
    "ci_cd":                  ["ci/cd", "pipeline", "deploy", "github actions", "workflow"],
    "crypto_trading":         ["crypto", "bitcoin", "ethereum", "trading bot", "defi", "binance"],
    "customer_support":       ["customer support", "helpdesk", "ticket", "zendesk"],
    "data_pipeline":          ["etl", "data pipeline", "data ingestion", "airflow", "kafka"],
    "ecommerce":              ["shopify", "woocommerce", "amazon", "ecommerce", "e-commerce"],
    "finance":                ["finance", "accounting", "invoic", "payroll", "stripe"],
    "lead_generation":        ["lead gen", "prospecting", "outreach", "crm"],
    "marketing":              ["marketing", "campaign", "seo", "social media"],
    "real_estate":            ["real estate", "zillow", "mls", "property", "realty"],
    "security":               ["security", "vulnerability", "penetration", "scanner"],
    "social_media":           ["twitter", "instagram", "tiktok", "linkedin", "social"],
    "web_scraping":           ["scraping", "crawler", "spider", "selenium", "playwright"],
    "workflow_orchestration": ["workflow", "orchestrat", "schedule", "cron", "zapier", "make.com"],
}


# ---------------------------------------------------------------------------
# Main bot class
# ---------------------------------------------------------------------------

class GitHubAnalyzerBot:
    """Discover and learn from top bot repositories on GitHub.

    Parameters
    ----------
    github_token:
        Optional GitHub personal-access token (increases the rate limit
        from 60 to 5,000 requests per hour).
    max_results_per_query:
        Maximum number of repositories to return per search query
        (capped at 100 by the GitHub Search API).
    """

    GITHUB_API_BASE = "https://api.github.com"
    SEARCH_QUERIES = [
        "bot automation stars:>50 language:python",
        "workflow automation bot stars:>100",
        "chatbot framework stars:>200",
        "trading bot crypto stars:>100",
        "lead generation bot stars:>50",
    ]

    def __init__(
        self,
        github_token: str | None = None,
        max_results_per_query: int = 10,
    ) -> None:
        self._token = github_token
        self._max = min(max(1, max_results_per_query), 100)
        self._discovered: list[dict[str, Any]] = []
        self._insights: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def discover_repositories(self, queries: list[str] | None = None) -> list[dict[str, Any]]:
        """Search GitHub for trending bot repositories.

        Parameters
        ----------
        queries:
            Optional list of search queries.  Defaults to
            ``GitHubAnalyzerBot.SEARCH_QUERIES``.

        Returns
        -------
        list[dict]
            Deduplicated list of repository metadata records.
        """
        queries = queries or self.SEARCH_QUERIES
        seen: set[int] = set()
        results: list[dict[str, Any]] = []

        for query in queries:
            try:
                repos = self._search_repositories(query)
            except GitHubAPIError:
                continue

            for repo in repos:
                repo_id = repo.get("id")
                if repo_id not in seen:
                    seen.add(repo_id)
                    results.append(self._normalise_repo(repo))

        self._discovered = results
        return results

    def extract_workflows(self, repo_full_name: str) -> dict[str, Any]:
        """Attempt to fetch a ``workflows.json`` file from a repository.

        Parameters
        ----------
        repo_full_name:
            GitHub repository in ``owner/repo`` format.

        Returns
        -------
        dict
            Parsed JSON content, or an empty dict if not found.
        """
        path = "workflows.json"
        raw = self._fetch_file(repo_full_name, path)
        if raw is None:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def analyze_repository(self, repo: dict[str, Any]) -> dict[str, Any]:
        """Analyse a single repository record and extract insights.

        Parameters
        ----------
        repo:
            A normalised repository dict returned by
            :meth:`discover_repositories`.

        Returns
        -------
        dict
            Insight record containing category, score, and recommendations.
        """
        category = self._categorise(repo)
        score = self._score_repo(repo)
        workflows = self.extract_workflows(repo["full_name"])
        recommendations = self._build_recommendations(repo, workflows)

        insight = {
            "repo": repo["full_name"],
            "category": category,
            "relevance_score": score,
            "stars": repo["stars"],
            "language": repo["language"],
            "workflows_found": bool(workflows),
            "recommendations": recommendations,
            "analysed_at": datetime.now(timezone.utc).isoformat(),
        }
        self._insights.append(insight)
        return insight

    def analyze_all(self) -> list[dict[str, Any]]:
        """Run :meth:`analyze_repository` on every discovered repository.

        Returns
        -------
        list[dict]
            All insight records, sorted by relevance score descending.
        """
        if not self._discovered:
            self.discover_repositories()

        insights = [self.analyze_repository(repo) for repo in self._discovered]
        insights.sort(key=lambda x: x["relevance_score"], reverse=True)
        self._insights = insights
        return insights

    def generate_bot_config(self, insight: dict[str, Any]) -> dict[str, Any]:
        """Generate a DreamCo-compatible bot configuration from an insight.

        Parameters
        ----------
        insight:
            An insight record returned by :meth:`analyze_repository`.

        Returns
        -------
        dict
            A bot configuration stub ready for integration into DreamCo.
        """
        repo_slug = insight["repo"].replace("/", "_").replace("-", "_").lower()
        return {
            "id": f"github_{repo_slug}",
            "name": f"GitHub-Sourced Bot — {insight['repo']}",
            "category": insight["category"],
            "source_repo": insight["repo"],
            "relevance_score": insight["relevance_score"],
            "trigger": {
                "type": "cron",
                "schedule": "0 */12 * * *",
            },
            "automation": {
                "retry_attempts": 3,
                "timeout_seconds": 300,
                "notify_on_completion": True,
            },
            "monetization": {
                "model": "service_sales",
                "revenue_per_cycle": 0,
                "affiliate_programs": [],
                "payment_processor": "stripe",
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "metadata": {
                "stars": insight["stars"],
                "language": insight["language"],
                "recommendations": insight["recommendations"],
            },
        }

    def generate_all_configs(self) -> list[dict[str, Any]]:
        """Generate bot configs for every insight record.

        Returns
        -------
        list[dict]
            List of DreamCo-compatible bot configuration stubs.
        """
        if not self._insights:
            self.analyze_all()
        return [self.generate_bot_config(insight) for insight in self._insights]

    def get_top_insights(self, n: int = 5) -> list[dict[str, Any]]:
        """Return the top *n* insights sorted by relevance score.

        Parameters
        ----------
        n:
            Number of insights to return.

        Returns
        -------
        list[dict]
        """
        if not self._insights:
            self.analyze_all()
        return self._insights[:n]

    def get_trend_summary(self) -> dict[str, Any]:
        """Summarise category trends across all analysed repositories.

        Returns
        -------
        dict
            A summary with category counts, top categories, and metadata.
        """
        if not self._insights:
            self.analyze_all()

        category_counts: dict[str, int] = {}
        for insight in self._insights:
            cat = insight["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

        sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        return {
            "total_repositories_analysed": len(self._insights),
            "category_distribution": category_counts,
            "top_categories": [c for c, _ in sorted_cats[:3]],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _get(self, url: str) -> Any:
        """Perform an authenticated GET request against the GitHub API."""
        req = urllib.request.Request(url, headers=self._build_headers())
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise GitHubAPIError(f"HTTP {exc.code} fetching {url}") from exc
        except (urllib.error.URLError, OSError) as exc:
            raise GitHubAPIError(f"Network error fetching {url}: {exc}") from exc

    def _search_repositories(self, query: str) -> list[dict[str, Any]]:
        """Call the GitHub repository search endpoint."""
        params = urllib.parse.urlencode({
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": self._max,
        })
        url = f"{self.GITHUB_API_BASE}/search/repositories?{params}"
        data = self._get(url)
        return data.get("items", [])

    def _fetch_file(self, repo_full_name: str, file_path: str) -> str | None:
        """Fetch the raw content of a file from a repository.

        Returns ``None`` if the file does not exist or cannot be fetched.
        """
        url = f"{self.GITHUB_API_BASE}/repos/{repo_full_name}/contents/{file_path}"
        try:
            data = self._get(url)
        except GitHubAPIError:
            return None

        # GitHub returns file content as base64 when using the contents API.
        content = data.get("content", "")
        encoding = data.get("encoding", "base64")
        if encoding == "base64":
            try:
                return base64.b64decode(content).decode("utf-8")
            except Exception:
                return None
        return content or None

    @staticmethod
    def _normalise_repo(raw: dict[str, Any]) -> dict[str, Any]:
        """Extract the fields we care about from a raw GitHub API repo record."""
        return {
            "id": raw.get("id"),
            "full_name": raw.get("full_name", ""),
            "description": raw.get("description") or "",
            "stars": raw.get("stargazers_count", 0),
            "forks": raw.get("forks_count", 0),
            "language": raw.get("language") or "unknown",
            "topics": raw.get("topics", []),
            "url": raw.get("html_url", ""),
            "created_at": raw.get("created_at", ""),
            "updated_at": raw.get("updated_at", ""),
        }

    def _categorise(self, repo: dict[str, Any]) -> str:
        """Lightweight AI-style categorisation based on keyword matching.

        Combines the repository description and topics to determine the most
        likely bot category.
        """
        text = " ".join([
            repo.get("description", ""),
            repo.get("full_name", ""),
            " ".join(repo.get("topics", [])),
        ]).lower()

        scores: dict[str, int] = {cat: 0 for cat in BOT_CATEGORIES}
        for category, keywords in _CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    scores[category] += 1

        best = max(scores, key=lambda c: scores[c])
        return best if scores[best] > 0 else "automation"

    @staticmethod
    def _score_repo(repo: dict[str, Any]) -> float:
        """Score a repository on a 0–100 scale based on popularity signals."""
        stars = repo.get("stars", 0)
        forks = repo.get("forks", 0)
        has_description = 1 if repo.get("description") else 0
        has_topics = min(len(repo.get("topics", [])), 5)

        # Logarithmic star score (0–60 points)
        star_score = min(math.log1p(stars) / math.log1p(10000) * 60, 60)
        # Fork score (0–20 points)
        fork_score = min(math.log1p(forks) / math.log1p(1000) * 20, 20)
        # Metadata quality (0–20 points)
        meta_score = has_description * 10 + has_topics * 2

        return round(star_score + fork_score + meta_score, 2)

    @staticmethod
    def _build_recommendations(
        repo: dict[str, Any],
        workflows: dict[str, Any],
    ) -> list[str]:
        """Generate human-readable best-practice recommendations."""
        recs: list[str] = []

        if repo.get("stars", 0) > 1000:
            recs.append("High-star repo — consider adopting its architecture patterns.")

        if workflows:
            wf_count = len(workflows.get("workflows", []))
            if wf_count >= 5:
                recs.append(
                    f"Rich workflow registry ({wf_count} workflows) — "
                    "review for reusable automation steps."
                )
            if workflows.get("global_settings"):
                recs.append("Has global_settings block — adopt for DreamCo global config.")

        topics = repo.get("topics", [])
        if "machine-learning" in topics or "ai" in topics:
            recs.append("AI/ML capabilities detected — integrate AI decision layer.")

        if not recs:
            recs.append("Standard bot pattern — review source for reusable components.")

        return recs
