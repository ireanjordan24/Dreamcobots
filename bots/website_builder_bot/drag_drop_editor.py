"""
Drag-and-Drop Website Editor — real-time layout customization engine.

Allows users to add, remove, reorder, and configure website sections
and content blocks without writing code. Competes with Wix, Squarespace,
Elementor, and Webflow.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class SectionType(Enum):
    """Supported drag-and-drop section types."""

    HERO = "hero"
    FEATURES = "features"
    TESTIMONIALS = "testimonials"
    PRICING = "pricing"
    GALLERY = "gallery"
    TEAM = "team"
    FAQ = "faq"
    CONTACT = "contact"
    BLOG_GRID = "blog_grid"
    PRODUCT_GRID = "product_grid"
    VIDEO = "video"
    NEWSLETTER = "newsletter"
    CTA = "cta"
    FOOTER = "footer"
    HEADER = "header"
    CUSTOM = "custom"


SECTION_TYPES: List[str] = [st.value for st in SectionType]


@dataclass
class LayoutSection:
    """A single draggable section within a page layout."""

    section_id: str
    section_type: str
    position: int
    config: dict
    visible: bool = True
    locked: bool = False
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DragDropEditorError(Exception):
    """Raised for invalid editor operations."""


class DragDropEditor:
    """Visual drag-and-drop editor for website layouts.

    Sections can be added, removed, reordered, and configured in real-time.
    Each project maintains an ordered list of sections representing the page
    structure.
    """

    def __init__(self) -> None:
        self._projects: dict = {}  # project_id -> project dict
        self._sections: dict = {}  # section_id -> LayoutSection

    # ------------------------------------------------------------------
    # Project management
    # ------------------------------------------------------------------

    def create_project(self, user_id: str, site_name: str) -> dict:
        """Create a new editor project for *site_name*.

        Returns
        -------
        dict  Project record with ``id``, ``user_id``, ``site_name``,
              ``sections``, and ``created_at``.
        """
        if not site_name or not site_name.strip():
            raise DragDropEditorError("site_name must not be empty.")

        project_id = str(uuid.uuid4())
        record = {
            "id": project_id,
            "user_id": user_id,
            "site_name": site_name.strip(),
            "sections": [],  # ordered list of section IDs
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._projects[project_id] = record
        return record

    # ------------------------------------------------------------------
    # Section management
    # ------------------------------------------------------------------

    def add_section(
        self,
        project_id: str,
        section_type: str,
        config: Optional[dict] = None,
        position: Optional[int] = None,
    ) -> LayoutSection:
        """Add a new section to *project_id*.

        Parameters
        ----------
        section_type: One of ``SECTION_TYPES``.
        config:       Section-specific configuration.
        position:     Insert position (0-indexed). Appends if ``None``.

        Returns
        -------
        LayoutSection
        """
        project = self._get_project(project_id)
        if section_type not in SECTION_TYPES:
            raise DragDropEditorError(
                f"Invalid section_type '{section_type}'. Valid: {SECTION_TYPES}"
            )

        current_count = len(project["sections"])
        if position is None:
            pos = current_count
        else:
            pos = max(0, min(position, current_count))

        section = LayoutSection(
            section_id=str(uuid.uuid4()),
            section_type=section_type,
            position=pos,
            config=dict(config) if config else {},
        )
        self._sections[section.section_id] = section
        project["sections"].insert(pos, section.section_id)
        self._reindex(project)
        return section

    def remove_section(self, project_id: str, section_id: str) -> dict:
        """Remove a section from the project layout.

        Returns
        -------
        dict  ``{"removed": section_id}``
        """
        project = self._get_project(project_id)
        if section_id not in project["sections"]:
            raise DragDropEditorError(
                f"Section '{section_id}' not in project '{project_id}'."
            )
        project["sections"].remove(section_id)
        self._sections.pop(section_id, None)
        self._reindex(project)
        return {"removed": section_id}

    def move_section(
        self, project_id: str, section_id: str, new_position: int
    ) -> LayoutSection:
        """Move a section to *new_position* (drag-and-drop reorder).

        Returns
        -------
        LayoutSection  Updated section with new position.
        """
        project = self._get_project(project_id)
        if section_id not in project["sections"]:
            raise DragDropEditorError(
                f"Section '{section_id}' not in project '{project_id}'."
            )

        project["sections"].remove(section_id)
        clamped = max(0, min(new_position, len(project["sections"])))
        project["sections"].insert(clamped, section_id)
        self._reindex(project)
        return self._sections[section_id]

    def update_section_config(
        self, project_id: str, section_id: str, config: dict
    ) -> LayoutSection:
        """Update the configuration of an existing section.

        Returns
        -------
        LayoutSection  Section with merged config.
        """
        self._get_project(project_id)
        if section_id not in self._sections:
            raise DragDropEditorError(f"Section '{section_id}' not found.")
        self._sections[section_id].config.update(config)
        return self._sections[section_id]

    def toggle_section_visibility(
        self, project_id: str, section_id: str
    ) -> LayoutSection:
        """Toggle a section's ``visible`` flag.

        Returns
        -------
        LayoutSection
        """
        self._get_project(project_id)
        if section_id not in self._sections:
            raise DragDropEditorError(f"Section '{section_id}' not found.")
        self._sections[section_id].visible = not self._sections[section_id].visible
        return self._sections[section_id]

    def lock_section(self, project_id: str, section_id: str) -> LayoutSection:
        """Lock a section to prevent accidental edits.

        Returns
        -------
        LayoutSection
        """
        self._get_project(project_id)
        if section_id not in self._sections:
            raise DragDropEditorError(f"Section '{section_id}' not found.")
        self._sections[section_id].locked = True
        return self._sections[section_id]

    def unlock_section(self, project_id: str, section_id: str) -> LayoutSection:
        """Unlock a previously locked section.

        Returns
        -------
        LayoutSection
        """
        self._get_project(project_id)
        if section_id not in self._sections:
            raise DragDropEditorError(f"Section '{section_id}' not found.")
        self._sections[section_id].locked = False
        return self._sections[section_id]

    def list_sections(self, project_id: str) -> List[LayoutSection]:
        """Return all sections in render order.

        Returns
        -------
        list[LayoutSection]
        """
        project = self._get_project(project_id)
        return [
            self._sections[sid]
            for sid in project["sections"]
            if sid in self._sections
        ]

    def export_layout(self, project_id: str) -> dict:
        """Export the full ordered layout as a serialisable dict.

        Returns
        -------
        dict
        """
        project = self._get_project(project_id)
        sections = self.list_sections(project_id)
        return {
            "project_id": project_id,
            "site_name": project["site_name"],
            "sections": [
                {
                    "section_id": s.section_id,
                    "section_type": s.section_type,
                    "position": s.position,
                    "config": s.config,
                    "visible": s.visible,
                    "locked": s.locked,
                }
                for s in sections
            ],
            "total_sections": len(sections),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_project(self, project_id: str) -> dict:
        if project_id not in self._projects:
            raise DragDropEditorError(f"Project '{project_id}' not found.")
        return self._projects[project_id]

    def _reindex(self, project: dict) -> None:
        """Update the ``position`` field on every section in order."""
        for idx, sid in enumerate(project["sections"]):
            if sid in self._sections:
                self._sections[sid].position = idx
