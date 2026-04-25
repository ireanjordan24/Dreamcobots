"""
Live Preview Engine — render real-time HTML previews of website changes.

Assembles the current drag-and-drop layout + widgets + vibe-coded content
into a complete, renderable HTML document for instant browser preview.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class LivePreviewError(Exception):
    """Raised for invalid preview operations."""


class LivePreview:
    """Assembles real-time HTML previews from layout and widget data.

    Each call to ``render_preview`` produces a self-contained HTML document
    that can be served directly in an iframe, browser, or returned to clients.

    Previews are cached by ``preview_id`` and can be retrieved or invalidated.
    """

    # Inline CSS injected into every preview for baseline styling
    _BASE_CSS: str = (
        "body{margin:0;font-family:'Inter',sans-serif;background:#fff;color:#1a202c}"
        ".preview-section{padding:3rem 1.5rem;max-width:1200px;margin:0 auto}"
        ".preview-section+.preview-section{border-top:1px solid #e2e8f0}"
        ".preview-widget{border:1px dashed #a0aec0;border-radius:6px;"
        "padding:1rem;margin:.5rem 0;background:#f7fafc}"
        ".preview-widget__label{font-size:.75rem;font-weight:600;color:#4a5568;"
        "text-transform:uppercase;letter-spacing:.05em}"
        ".section-label{font-size:.7rem;font-weight:700;color:#a0aec0;"
        "text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem}"
        ".hidden-section{opacity:.4}"
    )

    def __init__(self) -> None:
        self._previews: dict = {}  # preview_id -> preview dict

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render_preview(
        self,
        site_name: str,
        sections: Optional[List[dict]] = None,
        widgets_by_section: Optional[dict] = None,
        custom_css: str = "",
        custom_js: str = "",
        color_scheme: Optional[dict] = None,
    ) -> dict:
        """Generate a live HTML preview document.

        Parameters
        ----------
        site_name:           Brand/site name shown in the ``<title>``.
        sections:            Ordered list of section dicts from DragDropEditor.
                             Each dict: ``{section_id, section_type, visible, config}``.
        widgets_by_section:  Mapping of ``section_id -> list[widget dicts]``.
        custom_css:          Additional CSS to inject (from VibeCoder or user).
        custom_js:           Additional JS to inject.
        color_scheme:        ``{primary, secondary, bg}`` color overrides.

        Returns
        -------
        dict  ``{preview_id, html, created_at, site_name}``
        """
        sections = sections or []
        widgets_by_section = widgets_by_section or {}
        colors = color_scheme or {
            "primary": "#4F46E5",
            "secondary": "#06B6D4",
            "bg": "#FFFFFF",
        }

        css_vars = (
            f"--color-primary:{colors.get('primary', '#4F46E5')};"
            f"--color-secondary:{colors.get('secondary', '#06B6D4')};"
            f"--color-bg:{colors.get('bg', '#FFFFFF')};"
        )

        sections_html = self._render_sections(sections, widgets_by_section)

        html = (
            f'<!DOCTYPE html>\n'
            f'<html lang="en">\n'
            f'<head>\n'
            f'  <meta charset="UTF-8">\n'
            f'  <meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'  <title>{site_name} \u2014 Live Preview</title>\n'
            f'  <style>:root{{{css_vars}}}{self._BASE_CSS}'
            f'{custom_css}</style>\n'
            f'</head>\n'
            f'<body style="background:var(--color-bg)">\n'
            f'  <header style="background:var(--color-primary);color:#fff;'
            f'padding:1rem 1.5rem;font-weight:700;font-size:1.25rem">'
            f'{site_name}</header>\n'
            f'{sections_html}\n'
            f'  <footer style="background:#1a202c;color:#a0aec0;text-align:center;'
            f'padding:1.5rem;font-size:.875rem">'
            f'&copy; {site_name} \u2014 Built with DreamCo Website Builder</footer>\n'
            f'  <script>{custom_js}</script>\n'
            f'</body>\n'
            f'</html>\n'
        )

        preview_id = f"prev_{uuid.uuid4().hex[:10]}"
        record = {
            "preview_id": preview_id,
            "html": html,
            "site_name": site_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._previews[preview_id] = record
        return record

    def get_preview(self, preview_id: str) -> dict:
        """Retrieve a previously rendered preview.

        Returns
        -------
        dict
        """
        if preview_id not in self._previews:
            raise LivePreviewError(f"Preview '{preview_id}' not found.")
        return self._previews[preview_id]

    def invalidate_preview(self, preview_id: str) -> dict:
        """Remove a cached preview.

        Returns
        -------
        dict  ``{"invalidated": preview_id}``
        """
        if preview_id not in self._previews:
            raise LivePreviewError(f"Preview '{preview_id}' not found.")
        self._previews.pop(preview_id)
        return {"invalidated": preview_id}

    def list_previews(self) -> List[dict]:
        """Return metadata (without full HTML) for all previews.

        Returns
        -------
        list[dict]
        """
        return [
            {
                "preview_id": p["preview_id"],
                "site_name": p["site_name"],
                "created_at": p["created_at"],
            }
            for p in self._previews.values()
        ]

    # ------------------------------------------------------------------
    # Internal rendering helpers
    # ------------------------------------------------------------------

    def _render_sections(
        self, sections: List[dict], widgets_by_section: dict
    ) -> str:
        if not sections:
            return (
                '  <div class="preview-section" style="text-align:center;'
                'color:#a0aec0;padding:4rem">No sections added yet. '
                'Drag a section from the panel to get started.</div>'
            )

        parts = []
        for sec in sections:
            sid = sec.get("section_id", "")
            stype = sec.get("section_type", "custom")
            visible = sec.get("visible", True)
            vis_class = "" if visible else " hidden-section"

            widgets_html = self._render_widgets(widgets_by_section.get(sid, []))

            parts.append(
                f'  <section id="{sid}" '
                f'class="preview-section{vis_class}">\n'
                f'    <div class="section-label">'
                f'{stype.replace("_", " ").upper()}</div>\n'
                f'{widgets_html}'
                f'  </section>'
            )
        return "\n".join(parts)

    def _render_widgets(self, widgets: List[dict]) -> str:
        if not widgets:
            return ""
        parts = []
        for w in widgets:
            wtype = w.get("widget_type", "widget")
            label = w.get("label", wtype)
            enabled = w.get("enabled", True)
            opacity = "1" if enabled else "0.4"
            parts.append(
                f'    <div class="preview-widget" style="opacity:{opacity}">\n'
                f'      <div class="preview-widget__label">{label}</div>\n'
                f'      <div style="font-size:.8rem;color:#718096">'
                f'{w.get("description", "")}</div>\n'
                f'    </div>'
            )
        return "\n".join(parts) + "\n"
