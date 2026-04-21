"""
Widget Library — SEO tools, marketing solutions, analytics, interactive elements.

Provides a catalogue of pre-built widgets (sliders, forms, chat, analytics,
maps, social feeds, etc.) that can be embedded into any website section.

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


class WidgetType(Enum):
    """Supported widget categories."""

    # SEO & Marketing
    SEO_ANALYZER = "seo_analyzer"
    META_EDITOR = "meta_editor"
    SITEMAP_GENERATOR = "sitemap_generator"
    ANALYTICS_DASHBOARD = "analytics_dashboard"
    HEATMAP = "heatmap"
    AB_TEST = "ab_test"
    EMAIL_CAPTURE = "email_capture"
    POPUP = "popup"
    LIVE_CHAT = "live_chat"
    SOCIAL_SHARE = "social_share"
    # Interactive UI
    IMAGE_SLIDER = "image_slider"
    VIDEO_PLAYER = "video_player"
    COUNTDOWN_TIMER = "countdown_timer"
    PROGRESS_BAR = "progress_bar"
    ACCORDION = "accordion"
    TABS = "tabs"
    MODAL = "modal"
    TOOLTIP = "tooltip"
    # Forms & Conversion
    CONTACT_FORM = "contact_form"
    LEAD_FORM = "lead_form"
    SURVEY = "survey"
    BOOKING_FORM = "booking_form"
    PAYMENT_FORM = "payment_form"
    NEWSLETTER_FORM = "newsletter_form"
    # E-commerce
    PRODUCT_CARD = "product_card"
    CART_WIDGET = "cart_widget"
    WISHLIST = "wishlist"
    REVIEW_STARS = "review_stars"
    PRICE_TABLE = "price_table"
    # Social & Community
    SOCIAL_FEED = "social_feed"
    COMMENTS = "comments"
    RATING = "rating"
    SHARE_BUTTONS = "share_buttons"
    # Maps & Location
    MAP_EMBED = "map_embed"
    STORE_LOCATOR = "store_locator"


WIDGET_TYPES: List[str] = [wt.value for wt in WidgetType]

_WIDGET_DESCRIPTIONS: dict = {
    WidgetType.SEO_ANALYZER: (
        "Real-time SEO score analysis with actionable recommendations."
    ),
    WidgetType.META_EDITOR: (
        "Visual editor for title, description, OG tags, and keywords."
    ),
    WidgetType.SITEMAP_GENERATOR: (
        "Auto-generate and submit XML sitemaps to search engines."
    ),
    WidgetType.ANALYTICS_DASHBOARD: (
        "Unified analytics: pageviews, sessions, conversions."
    ),
    WidgetType.HEATMAP: (
        "Visual heatmap overlay showing user click and scroll patterns."
    ),
    WidgetType.AB_TEST: (
        "A/B test any page element with automatic winner detection."
    ),
    WidgetType.EMAIL_CAPTURE: "High-converting email opt-in bar or inline form.",
    WidgetType.POPUP: (
        "Customizable exit-intent or timed popup with targeting rules."
    ),
    WidgetType.LIVE_CHAT: "Embedded live-chat widget with bot + human handoff.",
    WidgetType.SOCIAL_SHARE: (
        "One-click share buttons for all major social platforms."
    ),
    WidgetType.IMAGE_SLIDER: (
        "Responsive image slider / carousel with touch support."
    ),
    WidgetType.VIDEO_PLAYER: (
        "Embedded video player (YouTube, Vimeo, or self-hosted)."
    ),
    WidgetType.COUNTDOWN_TIMER: (
        "Customizable countdown timer for launches and promotions."
    ),
    WidgetType.PROGRESS_BAR: (
        "Animated progress bar for goals, fundraisers, or skills."
    ),
    WidgetType.ACCORDION: (
        "Collapsible FAQ/content accordion with smooth animation."
    ),
    WidgetType.TABS: "Tabbed content panel for organizing multiple content areas.",
    WidgetType.MODAL: (
        "Lightbox/modal overlay triggered by button, scroll, or delay."
    ),
    WidgetType.TOOLTIP: (
        "Contextual tooltips on hover for icons or interactive elements."
    ),
    WidgetType.CONTACT_FORM: (
        "Fully validated contact form with spam protection."
    ),
    WidgetType.LEAD_FORM: "Lead capture form with CRM integration support.",
    WidgetType.SURVEY: (
        "Multi-step survey with branching logic and results export."
    ),
    WidgetType.BOOKING_FORM: (
        "Calendar-based appointment / reservation booking form."
    ),
    WidgetType.PAYMENT_FORM: (
        "PCI-compliant payment form (Stripe / PayPal ready)."
    ),
    WidgetType.NEWSLETTER_FORM: (
        "Newsletter subscription form with double opt-in."
    ),
    WidgetType.PRODUCT_CARD: (
        "Rich product card with image, price, rating, and CTA."
    ),
    WidgetType.CART_WIDGET: "Floating shopping cart with item count badge.",
    WidgetType.WISHLIST: "Save-for-later wishlist with persistent storage.",
    WidgetType.REVIEW_STARS: (
        "Verified customer review stars with aggregated rating."
    ),
    WidgetType.PRICE_TABLE: "Responsive pricing table with highlighted plan.",
    WidgetType.SOCIAL_FEED: (
        "Live social media feed (Instagram, Twitter/X, etc.)."
    ),
    WidgetType.COMMENTS: "Threaded comment section with moderation controls.",
    WidgetType.RATING: (
        "Interactive star rating for products, posts, or experiences."
    ),
    WidgetType.SHARE_BUTTONS: "Floating or inline social share buttons.",
    WidgetType.MAP_EMBED: "Google Maps / OpenStreetMap embed with custom pin.",
    WidgetType.STORE_LOCATOR: (
        "Interactive store/branch locator with radius search."
    ),
}


@dataclass
class Widget:
    """A single widget instance embedded on a page."""

    widget_id: str
    widget_type: str
    label: str
    description: str
    config: dict
    enabled: bool = True
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class WidgetLibraryError(Exception):
    """Raised for invalid widget operations."""


class WidgetLibrary:
    """Catalogue and instance manager for website widgets.

    Usage::

        lib = WidgetLibrary()
        widget = lib.add_widget(
            "page_001", "seo_analyzer", {"target_keyword": "best pizza"}
        )
        widgets = lib.list_widgets("page_001")
    """

    def __init__(self) -> None:
        self._pages: dict = {}    # page_id -> list[widget_id]
        self._widgets: dict = {}  # widget_id -> Widget

    # ------------------------------------------------------------------
    # Widget management
    # ------------------------------------------------------------------

    def add_widget(
        self,
        page_id: str,
        widget_type: str,
        config: Optional[dict] = None,
        label: Optional[str] = None,
    ) -> Widget:
        """Add a widget to *page_id*.

        Parameters
        ----------
        page_id:     Identifier for the page/section hosting the widget.
        widget_type: One of ``WIDGET_TYPES``.
        config:      Widget-specific configuration dict.
        label:       Human-readable label (defaults to widget type).

        Returns
        -------
        Widget
        """
        if widget_type not in WIDGET_TYPES:
            raise WidgetLibraryError(
                f"Unknown widget_type '{widget_type}'. Valid: {WIDGET_TYPES}"
            )

        wt_enum = WidgetType(widget_type)
        widget = Widget(
            widget_id=str(uuid.uuid4()),
            widget_type=widget_type,
            label=label or widget_type.replace("_", " ").title(),
            description=_WIDGET_DESCRIPTIONS.get(wt_enum, ""),
            config=dict(config) if config else {},
        )
        self._widgets[widget.widget_id] = widget
        self._pages.setdefault(page_id, []).append(widget.widget_id)
        return widget

    def remove_widget(self, page_id: str, widget_id: str) -> dict:
        """Remove a widget from *page_id*.

        Returns
        -------
        dict  ``{"removed": widget_id}``
        """
        if page_id not in self._pages or widget_id not in self._pages[page_id]:
            raise WidgetLibraryError(
                f"Widget '{widget_id}' not found on page '{page_id}'."
            )
        self._pages[page_id].remove(widget_id)
        self._widgets.pop(widget_id, None)
        return {"removed": widget_id}

    def update_widget_config(self, widget_id: str, config: dict) -> Widget:
        """Merge *config* into an existing widget's configuration.

        Returns
        -------
        Widget
        """
        if widget_id not in self._widgets:
            raise WidgetLibraryError(f"Widget '{widget_id}' not found.")
        self._widgets[widget_id].config.update(config)
        return self._widgets[widget_id]

    def toggle_widget(self, widget_id: str) -> Widget:
        """Toggle a widget's ``enabled`` state.

        Returns
        -------
        Widget
        """
        if widget_id not in self._widgets:
            raise WidgetLibraryError(f"Widget '{widget_id}' not found.")
        self._widgets[widget_id].enabled = not self._widgets[widget_id].enabled
        return self._widgets[widget_id]

    def list_widgets(self, page_id: str) -> List[Widget]:
        """Return all widgets for *page_id*.

        Returns
        -------
        list[Widget]
        """
        return [
            self._widgets[wid]
            for wid in self._pages.get(page_id, [])
            if wid in self._widgets
        ]

    def get_widget(self, widget_id: str) -> Widget:
        """Return a single widget by ID.

        Returns
        -------
        Widget
        """
        if widget_id not in self._widgets:
            raise WidgetLibraryError(f"Widget '{widget_id}' not found.")
        return self._widgets[widget_id]

    def browse_catalogue(self) -> List[dict]:
        """Return the full widget catalogue with descriptions.

        Returns
        -------
        list[dict]
        """
        return [
            {
                "widget_type": wt.value,
                "label": wt.value.replace("_", " ").title(),
                "description": _WIDGET_DESCRIPTIONS.get(wt, ""),
            }
            for wt in WidgetType
        ]
