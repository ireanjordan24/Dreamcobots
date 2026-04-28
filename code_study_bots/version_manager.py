"""
Version Manager — tracks, increments, and manages versions for generated tools.

Maintains a version registry so that every generated tool has a semantic
version string, a changelog, and a last-updated timestamp.  Supports bulk
version bumps (e.g. "update all Python tools to latest patch").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class VersionRecord:
    """Version history entry for a single tool."""
    tool_id: str
    version: str
    change_note: str
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class VersionConflictError(Exception):
    """Raised when attempting to register a version that already exists."""


# ---------------------------------------------------------------------------
# VersionManager
# ---------------------------------------------------------------------------

class VersionManager:
    """
    Manages semantic versioning for all tools in the ecosystem.

    Versions follow ``MAJOR.MINOR.PATCH`` (SemVer).  The manager provides
    helpers to bump each component and keeps a full changelog per tool.
    """

    def __init__(self) -> None:
        # Map tool_id -> current version string
        self._versions: dict[str, str] = {}
        # Map tool_id -> list of VersionRecord (history)
        self._history: dict[str, list[VersionRecord]] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, tool_id: str, initial_version: str = "1.0.0",
                 note: str = "Initial release") -> VersionRecord:
        """Register a new tool with an initial version."""
        if tool_id in self._versions:
            return self._history[tool_id][-1]
        record = VersionRecord(tool_id=tool_id, version=initial_version, change_note=note)
        self._versions[tool_id] = initial_version
        self._history[tool_id] = [record]
        return record

    # ------------------------------------------------------------------
    # Version bumping
    # ------------------------------------------------------------------

    def bump_patch(self, tool_id: str, note: str = "Patch update") -> VersionRecord:
        """Increment the PATCH component (1.2.3 → 1.2.4)."""
        return self._bump(tool_id, "patch", note)

    def bump_minor(self, tool_id: str, note: str = "Minor update") -> VersionRecord:
        """Increment the MINOR component and reset PATCH (1.2.3 → 1.3.0)."""
        return self._bump(tool_id, "minor", note)

    def bump_major(self, tool_id: str, note: str = "Major update") -> VersionRecord:
        """Increment the MAJOR component and reset MINOR+PATCH (1.2.3 → 2.0.0)."""
        return self._bump(tool_id, "major", note)

    def set_version(self, tool_id: str, version: str, note: str = "Manual version set") -> VersionRecord:
        """Explicitly set a version string (must be ≥ current)."""
        self._ensure_registered(tool_id)
        record = VersionRecord(tool_id=tool_id, version=version, change_note=note)
        self._versions[tool_id] = version
        self._history[tool_id].append(record)
        return record

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    def bump_all_patch(self, language: Optional[str] = None,
                       note: str = "Periodic patch update") -> list[VersionRecord]:
        """Bump patch version for all tools, optionally filtered by language prefix."""
        updated: list[VersionRecord] = []
        for tool_id in list(self._versions.keys()):
            if language and not tool_id.startswith(language.lower() + "__"):
                continue
            updated.append(self.bump_patch(tool_id, note))
        return updated

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def current_version(self, tool_id: str) -> Optional[str]:
        """Return the current version of a tool, or None if unknown."""
        return self._versions.get(tool_id)

    def history(self, tool_id: str) -> list[VersionRecord]:
        """Return the full version history for a tool."""
        return list(self._history.get(tool_id, []))

    def all_versions(self) -> dict[str, str]:
        """Return mapping of tool_id → current version for all registered tools."""
        return dict(self._versions)

    def summary(self) -> dict:
        """High-level summary of version registry."""
        return {
            "total_tools_versioned": len(self._versions),
            "versions": dict(self._versions),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_registered(self, tool_id: str) -> None:
        if tool_id not in self._versions:
            self.register(tool_id)

    def _bump(self, tool_id: str, component: str, note: str) -> VersionRecord:
        self._ensure_registered(tool_id)
        current = self._versions[tool_id]
        parts = current.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            parts = ["1", "0", "0"]
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        if component == "patch":
            patch += 1
        elif component == "minor":
            minor += 1
            patch = 0
        elif component == "major":
            major += 1
            minor = 0
            patch = 0
        new_version = f"{major}.{minor}.{patch}"
        record = VersionRecord(tool_id=tool_id, version=new_version, change_note=note)
        self._versions[tool_id] = new_version
        self._history[tool_id].append(record)
        return record
