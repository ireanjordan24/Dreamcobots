"""
Pull Request Learning Bot — analyzes pull requests and generates feedback.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  — mandatory GLOBAL AI SOURCES FLOW import required by all DreamCo bots


class PullRequestLearningBot:
    """Bot that learns from pull request data and generates actionable feedback."""

    def __init__(self) -> None:
        self._pr_history: list[dict] = []
        self._patterns: dict[str, int] = {}
        self.status = "idle"

    def learn_from_pr(self, pr_data: dict) -> dict:
        """Ingest and learn from pull request data.

        Parameters
        ----------
        pr_data : dict
            Pull request metadata such as title, body, files changed,
            author, and labels.

        Returns
        -------
        dict
            Summary of what was learned including detected patterns.
        """
        if not isinstance(pr_data, dict):
            return {"status": "error", "message": "pr_data must be a dict"}

        self._pr_history.append({**pr_data, "_learned_at": datetime.now(timezone.utc).isoformat()})

        title = pr_data.get("title", "")
        labels = pr_data.get("labels", [])
        files = pr_data.get("files_changed", [])

        for label in labels:
            self._patterns[label] = self._patterns.get(label, 0) + 1

        for fname in files:
            ext = os.path.splitext(fname)[-1]
            if ext:
                key = f"ext:{ext}"
                self._patterns[key] = self._patterns.get(key, 0) + 1

        return {
            "status": "learned",
            "pr_title": title,
            "total_prs_seen": len(self._pr_history),
            "top_patterns": sorted(self._patterns.items(), key=lambda x: -x[1])[:5],
        }

    def generate_response(self, pr_data: dict) -> str:
        """Generate a review response for a pull request.

        Parameters
        ----------
        pr_data : dict
            Pull request metadata to respond to.

        Returns
        -------
        str
            Human-readable review comment or suggestion.
        """
        if not isinstance(pr_data, dict):
            return "⚠️ Invalid PR data provided."

        title = pr_data.get("title", "this pull request")
        files = pr_data.get("files_changed", [])
        body = pr_data.get("body", "")

        lines = [f"👋 Thank you for submitting **{title}**."]

        if files:
            lines.append(f"📁 {len(files)} file(s) changed: {', '.join(files[:5])}{'...' if len(files) > 5 else ''}.")

        if not body:
            lines.append("💡 Suggestion: Please add a description to help reviewers understand the changes.")

        if self._patterns:
            common = max(self._patterns, key=lambda k: self._patterns[k])
            lines.append(f"📊 Most common pattern in reviewed PRs: `{common}`.")

        lines.append("✅ Automated review complete. Please address any suggestions before merging.")
        return "\n".join(lines)

    def run(self) -> None:
        """Main entry point — print bot status and demonstrate capabilities."""
        self.status = "running"
        print("=== Pull Request Learning Bot ===")
        print(f"Status  : {self.status}")
        print(f"PRs seen: {len(self._pr_history)}")
        sample = {
            "title": "Add GlobalAISourcesFlow to pr_learning_bot",
            "body": "Implements the mandatory framework integration.",
            "labels": ["enhancement", "bot"],
            "files_changed": ["bots/pr_learning_bot.py"],
        }
        result = self.learn_from_pr(sample)
        print("Learned:", result)
        response = self.generate_response(sample)
        print("Response:\n", response)
        self.status = "idle"


if __name__ == "__main__":
    bot = PullRequestLearningBot()
    bot.run()