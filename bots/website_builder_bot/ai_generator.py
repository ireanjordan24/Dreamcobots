"""
AI Website Generator — generate fully functional websites from natural-language prompts.

Supports e-commerce, blogs, portfolios, SaaS landing pages, corporate sites,
and more. Competes with Hostinger AI Builder, Shopify, GoDaddy, and Amazon.

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


class WebsiteType(Enum):
    """Supported website categories."""

    ECOMMERCE = "ecommerce"
    BLOG = "blog"
    PORTFOLIO = "portfolio"
    SAAS = "saas"
    CORPORATE = "corporate"
    LANDING_PAGE = "landing_page"
    RESTAURANT = "restaurant"
    NONPROFIT = "nonprofit"
    EDUCATION = "education"
    REAL_ESTATE = "real_estate"


# Keyword -> website type mapping for prompt detection
_TYPE_KEYWORDS: dict = {
    WebsiteType.ECOMMERCE: [
        "shop", "store", "ecommerce", "e-commerce", "sell", "product",
        "cart", "checkout", "shopify", "woocommerce",
    ],
    WebsiteType.BLOG: ["blog", "article", "post", "news", "journal", "writer"],
    WebsiteType.PORTFOLIO: [
        "portfolio", "showcase", "gallery", "photographer", "designer",
        "artist", "freelance",
    ],
    WebsiteType.SAAS: ["saas", "software", "app", "platform", "dashboard", "api"],
    WebsiteType.RESTAURANT: ["restaurant", "cafe", "food", "menu", "dining"],
    WebsiteType.NONPROFIT: ["nonprofit", "charity", "donation", "volunteer"],
    WebsiteType.EDUCATION: ["course", "school", "academy", "learn", "education"],
    WebsiteType.REAL_ESTATE: ["real estate", "property", "listing", "home", "realtor"],
    WebsiteType.LANDING_PAGE: ["launch", "landing", "coming soon", "waitlist"],
    WebsiteType.CORPORATE: ["company", "corporate", "business", "enterprise"],
}

_TYPE_SECTIONS: dict = {
    WebsiteType.ECOMMERCE: [
        "hero", "featured_products", "categories", "promotions",
        "testimonials", "newsletter", "footer",
    ],
    WebsiteType.BLOG: [
        "hero", "featured_posts", "categories", "recent_posts",
        "about_author", "newsletter", "footer",
    ],
    WebsiteType.PORTFOLIO: [
        "hero", "about", "services", "portfolio_grid",
        "testimonials", "contact", "footer",
    ],
    WebsiteType.SAAS: [
        "hero", "features", "how_it_works", "pricing",
        "testimonials", "faq", "cta", "footer",
    ],
    WebsiteType.CORPORATE: [
        "hero", "about", "services", "team", "case_studies",
        "awards", "contact", "footer",
    ],
    WebsiteType.RESTAURANT: [
        "hero", "about", "menu", "specials", "gallery",
        "reservations", "contact", "footer",
    ],
    WebsiteType.NONPROFIT: [
        "hero", "mission", "impact", "programs", "donate",
        "volunteer", "contact", "footer",
    ],
    WebsiteType.EDUCATION: [
        "hero", "courses", "instructors", "testimonials",
        "pricing", "faq", "enroll", "footer",
    ],
    WebsiteType.REAL_ESTATE: [
        "hero", "featured_listings", "search", "agents",
        "about", "testimonials", "contact", "footer",
    ],
    WebsiteType.LANDING_PAGE: [
        "hero", "features", "social_proof", "pricing", "faq", "cta", "footer",
    ],
}

_DEFAULT_COLOR_SCHEMES: dict = {
    WebsiteType.ECOMMERCE: {"primary": "#FF6B35", "secondary": "#004E89", "bg": "#FFFFFF"},
    WebsiteType.BLOG: {"primary": "#2D3748", "secondary": "#48BB78", "bg": "#F7FAFC"},
    WebsiteType.PORTFOLIO: {"primary": "#1A202C", "secondary": "#F6E05E", "bg": "#FFFFFF"},
    WebsiteType.SAAS: {"primary": "#4F46E5", "secondary": "#06B6D4", "bg": "#FAFAFA"},
    WebsiteType.CORPORATE: {"primary": "#1E3A5F", "secondary": "#C0392B", "bg": "#FFFFFF"},
    WebsiteType.RESTAURANT: {"primary": "#8B4513", "secondary": "#DAA520", "bg": "#FFF8DC"},
    WebsiteType.NONPROFIT: {"primary": "#2E7D32", "secondary": "#FF8F00", "bg": "#FFFFFF"},
    WebsiteType.EDUCATION: {"primary": "#1565C0", "secondary": "#E53935", "bg": "#F5F5F5"},
    WebsiteType.REAL_ESTATE: {"primary": "#1B4F72", "secondary": "#28B463", "bg": "#FDFEFE"},
    WebsiteType.LANDING_PAGE: {"primary": "#6C3483", "secondary": "#17A589", "bg": "#FFFFFF"},
}


@dataclass
class GeneratedWebsite:
    """Holds a fully generated website definition."""

    site_id: str
    user_prompt: str
    site_name: str
    website_type: WebsiteType
    sections: List[str]
    color_scheme: dict
    meta: dict
    html_scaffold: str
    css_scaffold: str
    js_scaffold: str
    pages: List[str]
    features: List[str]
    seo: dict
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class AIWebsiteGeneratorError(Exception):
    """Raised for invalid generator operations."""


class AIWebsiteGenerator:
    """Generate complete website definitions from natural-language prompts.

    Uses keyword analysis to detect the website type, then scaffolds a
    fully-structured site with HTML, CSS, JavaScript, SEO metadata, and
    page layout.
    """

    def __init__(self) -> None:
        self._generated: dict = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_website_type(self, prompt: str) -> WebsiteType:
        """Infer the most appropriate WebsiteType from *prompt*."""
        prompt_lower = prompt.lower()
        scores: dict = {wt: 0 for wt in WebsiteType}
        for wtype, keywords in _TYPE_KEYWORDS.items():
            for kw in keywords:
                if kw in prompt_lower:
                    scores[wtype] += 1
        best = max(scores, key=lambda k: scores[k])
        return best if scores[best] > 0 else WebsiteType.CORPORATE

    def generate_website(
        self,
        user_prompt: str,
        site_name: str,
        website_type: Optional[WebsiteType] = None,
        color_overrides: Optional[dict] = None,
    ) -> GeneratedWebsite:
        """Generate a complete website definition from *user_prompt*.

        Parameters
        ----------
        user_prompt:    Natural-language description of the desired site.
        site_name:      Name / brand for the site.
        website_type:   Explicit type; auto-detected from prompt if ``None``.
        color_overrides: Override the default color scheme (partial or full).

        Returns
        -------
        GeneratedWebsite
        """
        if not user_prompt or not user_prompt.strip():
            raise AIWebsiteGeneratorError("user_prompt must not be empty.")
        if not site_name or not site_name.strip():
            raise AIWebsiteGeneratorError("site_name must not be empty.")

        wtype = website_type or self.detect_website_type(user_prompt)
        sections = list(_TYPE_SECTIONS.get(wtype, _TYPE_SECTIONS[WebsiteType.CORPORATE]))
        color_scheme = dict(_DEFAULT_COLOR_SCHEMES.get(wtype, {}))
        if color_overrides:
            color_scheme.update(color_overrides)

        pages = self._build_pages(wtype)
        features = self._build_features(wtype)
        seo = self._build_seo(site_name, wtype, user_prompt)
        html = self._scaffold_html(site_name, wtype, sections, color_scheme, seo)
        css = self._scaffold_css(wtype, color_scheme)
        js = self._scaffold_js(wtype)

        site = GeneratedWebsite(
            site_id=str(uuid.uuid4()),
            user_prompt=user_prompt.strip(),
            site_name=site_name.strip(),
            website_type=wtype,
            sections=sections,
            color_scheme=color_scheme,
            meta={"type": wtype.value, "generated_by": "DreamCo Website Builder"},
            html_scaffold=html,
            css_scaffold=css,
            js_scaffold=js,
            pages=pages,
            features=features,
            seo=seo,
        )
        self._generated[site.site_id] = site
        return site

    def get_site(self, site_id: str) -> GeneratedWebsite:
        """Retrieve a previously generated site by ID."""
        if site_id not in self._generated:
            raise AIWebsiteGeneratorError(f"Site '{site_id}' not found.")
        return self._generated[site_id]

    def list_sites(self) -> List[GeneratedWebsite]:
        """Return all generated sites."""
        return list(self._generated.values())

    # ------------------------------------------------------------------
    # Internal scaffolding helpers
    # ------------------------------------------------------------------

    def _build_pages(self, wtype: WebsiteType) -> List[str]:
        pages_map = {
            WebsiteType.ECOMMERCE: [
                "Home", "Shop", "Product", "Cart", "Checkout", "About", "Contact"
            ],
            WebsiteType.BLOG: ["Home", "Blog", "Post", "About", "Archives", "Contact"],
            WebsiteType.PORTFOLIO: [
                "Home", "Portfolio", "About", "Services", "Contact"
            ],
            WebsiteType.SAAS: [
                "Home", "Features", "Pricing", "Docs", "Blog", "Login", "Contact"
            ],
            WebsiteType.CORPORATE: [
                "Home", "About", "Services", "Team", "Case Studies", "Contact"
            ],
            WebsiteType.RESTAURANT: [
                "Home", "Menu", "About", "Gallery", "Reservations", "Contact"
            ],
            WebsiteType.NONPROFIT: [
                "Home", "About", "Programs", "Donate", "Volunteer", "Contact"
            ],
            WebsiteType.EDUCATION: [
                "Home", "Courses", "Instructors", "Pricing", "Blog", "Contact"
            ],
            WebsiteType.REAL_ESTATE: [
                "Home", "Listings", "Agents", "About", "Blog", "Contact"
            ],
            WebsiteType.LANDING_PAGE: [
                "Home", "Features", "Pricing", "FAQ", "Contact"
            ],
        }
        return pages_map.get(wtype, ["Home", "About", "Contact"])

    def _build_features(self, wtype: WebsiteType) -> List[str]:
        common = [
            "SEO optimization", "Mobile responsive", "Fast page load",
            "Analytics dashboard",
        ]
        extra_map = {
            WebsiteType.ECOMMERCE: [
                "Product catalog", "Shopping cart", "Secure checkout",
                "Inventory management", "Order tracking", "Coupon codes",
                "Product reviews", "Wishlist",
            ],
            WebsiteType.BLOG: [
                "Rich text editor", "Categories & tags", "Author profiles",
                "Comment system", "RSS feed", "Social sharing",
            ],
            WebsiteType.SAAS: [
                "User authentication", "Subscription billing", "API access",
                "Usage analytics", "Multi-tenant support",
            ],
            WebsiteType.PORTFOLIO: [
                "Image gallery", "Project showcase", "Client testimonials",
                "Contact form", "Resume download",
            ],
        }
        return common + extra_map.get(wtype, [])

    def _build_seo(
        self, site_name: str, wtype: WebsiteType, prompt: str
    ) -> dict:
        label = wtype.value.replace("_", " ").title()
        desc = (
            f"{site_name} — {label} website built with DreamCo Website Builder."
        )
        return {
            "title": f"{site_name} | {label}",
            "description": desc,
            "keywords": [
                site_name.lower(),
                wtype.value.replace("_", " "),
                "website",
                "online",
            ],
            "og_title": site_name,
            "og_description": desc,
            "robots": "index, follow",
            "sitemap": "/sitemap.xml",
            "canonical": "/",
            "schema_type": "WebSite",
        }

    def _scaffold_html(
        self,
        site_name: str,
        wtype: WebsiteType,
        sections: List[str],
        colors: dict,
        seo: dict,
    ) -> str:
        section_html = "\n".join(
            f'    <section id="{s}" class="section section--{s}"></section>'
            for s in sections
        )
        return (
            f'<!DOCTYPE html>\n'
            f'<html lang="en">\n'
            f'<head>\n'
            f'  <meta charset="UTF-8">\n'
            f'  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'  <title>{seo["title"]}</title>\n'
            f'  <meta name="description" content="{seo["description"]}">\n'
            f'  <meta name="robots" content="{seo["robots"]}">\n'
            f'  <meta property="og:title" content="{seo["og_title"]}">\n'
            f'  <meta property="og:description" content="{seo["og_description"]}">\n'
            f'  <link rel="stylesheet" href="styles.css">\n'
            f'</head>\n'
            f'<body>\n'
            f'  <header id="site-header" class="site-header"></header>\n'
            f'  <main id="main-content">\n'
            f'{section_html}\n'
            f'  </main>\n'
            f'  <footer id="site-footer" class="site-footer"></footer>\n'
            f'  <script src="app.js"></script>\n'
            f'</body>\n'
            f'</html>\n'
        )

    def _scaffold_css(self, wtype: WebsiteType, colors: dict) -> str:
        primary = colors.get("primary", "#4F46E5")
        secondary = colors.get("secondary", "#06B6D4")
        bg = colors.get("bg", "#FFFFFF")
        return (
            f':root {{\n'
            f'  --color-primary: {primary};\n'
            f'  --color-secondary: {secondary};\n'
            f'  --color-bg: {bg};\n'
            f'  --font-base: "Inter", sans-serif;\n'
            f'  --max-width: 1200px;\n'
            f'}}\n\n'
            f'*, *::before, *::after {{'
            f' box-sizing: border-box; margin: 0; padding: 0; }}\n\n'
            f'body {{\n'
            f'  font-family: var(--font-base);\n'
            f'  background: var(--color-bg);\n'
            f'  color: #1A202C;\n'
            f'  line-height: 1.6;\n'
            f'}}\n\n'
            f'.section {{\n'
            f'  padding: 4rem 1.5rem;\n'
            f'  max-width: var(--max-width);\n'
            f'  margin: 0 auto;\n'
            f'}}\n\n'
            f'.btn-primary {{\n'
            f'  background: var(--color-primary);\n'
            f'  color: #fff;\n'
            f'  border: none;\n'
            f'  padding: 0.75rem 2rem;\n'
            f'  border-radius: 0.375rem;\n'
            f'  cursor: pointer;\n'
            f'  font-size: 1rem;\n'
            f'}}\n\n'
            f'.btn-primary:hover {{\n'
            f'  opacity: 0.9;\n'
            f'}}\n'
        )

    def _scaffold_js(self, wtype: WebsiteType) -> str:
        return (
            '"use strict";\n\n'
            '// DreamCo Website Builder — generated JavaScript scaffold\n\n'
            'document.addEventListener("DOMContentLoaded", function () {\n'
            '  initNavigation();\n'
            '  initAnimations();\n'
            '});\n\n'
            'function initNavigation() {\n'
            '  var headerElement = document.getElementById("site-header");\n'
            '  if (!headerElement) return;\n'
            '  window.addEventListener("scroll", function () {\n'
            '    headerElement.classList.toggle("scrolled", window.scrollY > 50);\n'
            '  });\n'
            '}\n\n'
            'function initAnimations() {\n'
            '  var sections = document.querySelectorAll(".section");\n'
            '  if (!("IntersectionObserver" in window)) return;\n'
            '  var observer = new IntersectionObserver(function (entries) {\n'
            '    entries.forEach(function (entry) {\n'
            '      if (entry.isIntersecting) {\n'
            '        entry.target.classList.add("visible");\n'
            '      }\n'
            '    });\n'
            '  }, { threshold: 0.1 });\n'
            '  sections.forEach(function (s) { observer.observe(s); });\n'
            '}\n'
        )
