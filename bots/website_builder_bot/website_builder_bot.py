"""
Website Builder Bot — Main Entry Point.

Composes the AI Generator, Drag-Drop Editor, Widget Library, Live Preview,
Deployment Engine, and Vibe Coder into a unified website-creation platform
that competes with Hostinger, Shopify, GoDaddy, and Amazon.

Architecture::

    DreamCobots
    └── website_builder_bot
          ├── AIWebsiteGenerator  — prompt → full website scaffold
          ├── DragDropEditor      — visual layout editor
          ├── WidgetLibrary       — SEO, analytics, forms, sliders, etc.
          ├── LivePreview         — real-time HTML preview
          ├── DeploymentEngine    — one-click deploy (AWS/Vercel/Netlify/…)
          └── VibeCoder           — code generation for every framework

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datetime import datetime, timezone
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401

from bots.website_builder_bot.ai_generator import (
    AIWebsiteGenerator,
    AIWebsiteGeneratorError,
    GeneratedWebsite,
    WebsiteType,
)
from bots.website_builder_bot.deployment_engine import (
    DeploymentEngine,
    DeploymentEngineError,
    DeployTarget,
    DEPLOY_TARGETS,
)
from bots.website_builder_bot.drag_drop_editor import (
    DragDropEditor,
    DragDropEditorError,
    LayoutSection,
    SectionType,
    SECTION_TYPES,
)
from bots.website_builder_bot.live_preview import LivePreview, LivePreviewError
from bots.website_builder_bot.vibe_coder import (
    VibeCoder,
    VibeCoderError,
    Framework,
    FRAMEWORKS,
)
from bots.website_builder_bot.widget_library import (
    Widget,
    WidgetLibrary,
    WidgetLibraryError,
    WidgetType,
    WIDGET_TYPES,
)


class WebsiteBuilderBotError(Exception):
    """Raised for top-level Website Builder Bot errors."""


class WebsiteBuilderBot:
    """All-in-one website builder bot.

    Provides a unified interface to generate, design, customise, preview,
    and deploy fully functional websites from natural-language prompts.

    Competes with: Hostinger AI Builder, Shopify, GoDaddy Website Builder,
    Amazon Web Services Amplify, Wix, Squarespace, Webflow.

    Usage::

        bot = WebsiteBuilderBot()

        # 1. Generate a site from a prompt
        site = bot.generate("Build me an online coffee shop", "Brew & Co")

        # 2. Open the drag-and-drop editor
        project = bot.open_editor(site.site_id, "user_001")
        bot.add_section(project["id"], "hero")
        bot.add_section(project["id"], "product_grid")

        # 3. Add widgets
        bot.add_widget(project["id"], "seo_analyzer")

        # 4. Live preview
        preview = bot.preview(project["id"])

        # 5. Deploy
        dep = bot.deploy(site.site_id, site.site_name, "vercel")
    """

    def __init__(self) -> None:
        self._generator = AIWebsiteGenerator()
        self._editor = DragDropEditor()
        self._widgets = WidgetLibrary()
        self._preview = LivePreview()
        self._deployment = DeploymentEngine()
        self._vibe_coder = VibeCoder()
        # Maps site_id -> editor project_id for convenience
        self._site_projects: dict = {}

    # ------------------------------------------------------------------
    # 1. AI Generation
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        site_name: str,
        website_type: Optional[WebsiteType] = None,
        color_overrides: Optional[dict] = None,
    ) -> GeneratedWebsite:
        """Generate a complete website from a natural-language *prompt*.

        Parameters
        ----------
        prompt:          What the site should be about.
        site_name:       Brand name for the site.
        website_type:    Force a specific type; auto-detected if ``None``.
        color_overrides: Partial/full ``{primary, secondary, bg}`` overrides.

        Returns
        -------
        GeneratedWebsite
        """
        return self._generator.generate_website(
            prompt, site_name, website_type, color_overrides
        )

    def detect_type(self, prompt: str) -> WebsiteType:
        """Detect the website type from *prompt* without generating the site."""
        return self._generator.detect_website_type(prompt)

    def list_sites(self) -> List[GeneratedWebsite]:
        """Return all generated sites."""
        return self._generator.list_sites()

    # ------------------------------------------------------------------
    # 2. Drag-and-Drop Editor
    # ------------------------------------------------------------------

    def open_editor(self, site_id: str, user_id: str) -> dict:
        """Open a drag-and-drop editor project for *site_id*.

        If a project already exists for *site_id* it is returned immediately.

        Returns
        -------
        dict  Editor project record.
        """
        if site_id in self._site_projects:
            proj_id = self._site_projects[site_id]
            return self._editor._projects[proj_id]  # noqa: SLF001

        site = self._generator.get_site(site_id)
        project = self._editor.create_project(user_id, site.site_name)
        self._site_projects[site_id] = project["id"]
        # Pre-populate with sections from the generated site
        for section_name in site.sections:
            # Map generated section names to valid SectionTypes where possible
            stype = self._map_section(section_name)
            self._editor.add_section(project["id"], stype)
        return project

    def add_section(
        self,
        project_id: str,
        section_type: str,
        config: Optional[dict] = None,
        position: Optional[int] = None,
    ) -> LayoutSection:
        """Add a draggable section to the editor project.

        Returns
        -------
        LayoutSection
        """
        return self._editor.add_section(project_id, section_type, config, position)

    def remove_section(self, project_id: str, section_id: str) -> dict:
        """Remove a section from the editor project."""
        return self._editor.remove_section(project_id, section_id)

    def move_section(
        self, project_id: str, section_id: str, new_position: int
    ) -> LayoutSection:
        """Reorder a section by drag-and-drop."""
        return self._editor.move_section(project_id, section_id, new_position)

    def update_section(
        self, project_id: str, section_id: str, config: dict
    ) -> LayoutSection:
        """Update section configuration."""
        return self._editor.update_section_config(project_id, section_id, config)

    def export_layout(self, project_id: str) -> dict:
        """Export the full page layout as a serialisable dict."""
        return self._editor.export_layout(project_id)

    # ------------------------------------------------------------------
    # 3. Widgets
    # ------------------------------------------------------------------

    def add_widget(
        self,
        page_id: str,
        widget_type: str,
        config: Optional[dict] = None,
        label: Optional[str] = None,
    ) -> Widget:
        """Add a widget to *page_id*.

        Returns
        -------
        Widget
        """
        return self._widgets.add_widget(page_id, widget_type, config, label)

    def list_widgets(self, page_id: str) -> List[Widget]:
        """Return all widgets for *page_id*."""
        return self._widgets.list_widgets(page_id)

    def browse_widgets(self) -> List[dict]:
        """Return the full widget catalogue."""
        return self._widgets.browse_catalogue()

    # ------------------------------------------------------------------
    # 4. Live Preview
    # ------------------------------------------------------------------

    def preview(
        self,
        project_id: str,
        custom_css: str = "",
        custom_js: str = "",
        color_scheme: Optional[dict] = None,
    ) -> dict:
        """Render a live HTML preview for *project_id*.

        Returns
        -------
        dict  ``{preview_id, html, site_name, created_at}``
        """
        layout = self._editor.export_layout(project_id)
        sections_raw = layout["sections"]

        # Gather widgets for each section
        widgets_by_section: dict = {}
        for sec in sections_raw:
            sid = sec["section_id"]
            wlist = self._widgets.list_widgets(sid)
            if wlist:
                widgets_by_section[sid] = [
                    {
                        "widget_type": w.widget_type,
                        "label": w.label,
                        "description": w.description,
                        "enabled": w.enabled,
                    }
                    for w in wlist
                ]

        return self._preview.render_preview(
            site_name=layout["site_name"],
            sections=sections_raw,
            widgets_by_section=widgets_by_section,
            custom_css=custom_css,
            custom_js=custom_js,
            color_scheme=color_scheme,
        )

    # ------------------------------------------------------------------
    # 5. Deployment
    # ------------------------------------------------------------------

    def deploy(
        self,
        site_id: str,
        site_name: str,
        target: str,
        custom_domain: Optional[str] = None,
        config: Optional[dict] = None,
    ) -> dict:
        """Deploy *site_id* to *target* platform.

        Parameters
        ----------
        site_id:       ID of the generated website.
        site_name:     Human-readable name (used in the URL slug).
        target:        One of ``DEPLOY_TARGETS``.
        custom_domain: Optional custom domain.

        Returns
        -------
        dict  Deployment record.
        """
        return self._deployment.deploy(
            site_id, site_name, target, custom_domain, config
        )

    def go_live(self, deployment_id: str) -> dict:
        """Mark a deployment as LIVE (simulate successful deployment)."""
        return self._deployment.simulate_live(deployment_id)

    def rollback_deployment(self, deployment_id: str) -> dict:
        """Roll back a deployment."""
        return self._deployment.rollback(deployment_id)

    def list_deploy_targets(self) -> List[dict]:
        """Return all available deployment targets with features."""
        return self._deployment.get_targets_info()

    # ------------------------------------------------------------------
    # 6. Vibe Coding
    # ------------------------------------------------------------------

    def vibe_code(
        self,
        framework: str,
        prompt: str,
        component_name: Optional[str] = None,
    ) -> dict:
        """Generate framework-specific code from a natural-language *prompt*.

        Parameters
        ----------
        framework:       Any of the supported web frameworks (react, vue, etc.).
        prompt:          What the component should do.
        component_name:  Optional explicit name.

        Returns
        -------
        dict  ``{snippet_id, framework, component_name, code, extension}``
        """
        return self._vibe_coder.generate_component(framework, prompt, component_name)

    def scaffold(self, framework: str, project_name: str) -> dict:
        """Return a full project scaffold for *framework*.

        Returns
        -------
        dict  ``{framework, project_name, install_cmd, files, directories}``
        """
        return self._vibe_coder.scaffold_project(framework, project_name)

    def convert_code(self, snippet_id: str, target_framework: str) -> dict:
        """Convert a saved snippet to another framework."""
        return self._vibe_coder.convert_snippet(snippet_id, target_framework)

    def list_frameworks(self) -> List[dict]:
        """Return all supported frameworks."""
        return self._vibe_coder.list_frameworks()

    # ------------------------------------------------------------------
    # Process / Chat interface (GLOBAL AI SOURCES FLOW)
    # ------------------------------------------------------------------

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point.

        Dispatches ``payload["action"]`` to the appropriate sub-system.
        Supported actions: ``generate``, ``preview``, ``deploy``, ``vibe_code``.
        """
        action = payload.get("action", "")

        if action == "generate":
            site = self.generate(
                prompt=payload["prompt"],
                site_name=payload["site_name"],
            )
            return {
                "action": "generate",
                "site_id": site.site_id,
                "website_type": site.website_type.value,
                "pages": site.pages,
                "features": site.features,
            }

        if action == "preview":
            result = self.preview(payload["project_id"])
            return {"action": "preview", "preview_id": result["preview_id"]}

        if action == "deploy":
            dep = self.deploy(
                site_id=payload["site_id"],
                site_name=payload["site_name"],
                target=payload.get("target", "vercel"),
            )
            return {
                "action": "deploy",
                "deployment_id": dep["deployment_id"],
                "endpoint_url": dep["endpoint_url"],
                "status": dep["status"],
            }

        if action == "vibe_code":
            result = self.vibe_code(
                framework=payload["framework"],
                prompt=payload["prompt"],
            )
            return {
                "action": "vibe_code",
                "snippet_id": result["snippet_id"],
                "framework": result["framework"],
                "extension": result["extension"],
            }

        return {
            "error": f"Unknown action '{action}'.",
            "supported_actions": ["generate", "preview", "deploy", "vibe_code"],
        }

    def chat(self, message: str) -> dict:
        """Natural-language chat interface for the Website Builder Bot."""
        msg_lower = message.lower()

        if any(w in msg_lower for w in ("build", "create", "make", "generate")):
            return {
                "response": (
                    "I can build any website from a simple description. "
                    "Just tell me the site name and what it's about, and I'll "
                    "generate the full HTML, CSS, JS, SEO, and a deployment plan!"
                ),
                "suggested_action": "generate",
            }

        if any(w in msg_lower for w in ("deploy", "publish", "launch", "go live")):
            return {
                "response": (
                    "Ready to go live? I support one-click deployments to "
                    "Vercel, Netlify, AWS, GitHub Pages, Cloudflare, Docker, "
                    "and local servers."
                ),
                "suggested_action": "deploy",
            }

        if any(w in msg_lower for w in ("preview", "see", "show", "view")):
            return {
                "response": (
                    "I'll generate a live HTML preview of your site instantly. "
                    "You can see every section and widget in real-time."
                ),
                "suggested_action": "preview",
            }

        if any(w in msg_lower for w in ("code", "react", "vue", "svelte", "framework")):
            return {
                "response": (
                    "I support every major web framework: React, Vue, Svelte, "
                    "Angular, Astro, Next.js, Nuxt, SvelteKit, Remix, Gatsby, "
                    "and more — plus TypeScript, Tailwind, SCSS, and Styled Components."
                ),
                "suggested_action": "vibe_code",
            }

        return {
            "response": (
                "Welcome to DreamCo Website Builder! I can generate websites, "
                "provide drag-and-drop editing, add widgets, show live previews, "
                "and deploy to the cloud. What would you like to build?"
            ),
            "supported_actions": ["generate", "preview", "deploy", "vibe_code"],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _map_section(self, section_name: str) -> str:
        """Map an AI-generated section name to a valid SectionType value."""
        mapping = {
            "hero": "hero",
            "features": "features",
            "featured_products": "product_grid",
            "categories": "product_grid",
            "promotions": "cta",
            "testimonials": "testimonials",
            "newsletter": "newsletter",
            "footer": "footer",
            "about": "custom",
            "about_author": "custom",
            "services": "features",
            "portfolio_grid": "gallery",
            "how_it_works": "features",
            "pricing": "pricing",
            "faq": "faq",
            "cta": "cta",
            "team": "team",
            "case_studies": "custom",
            "awards": "custom",
            "contact": "contact",
            "menu": "custom",
            "specials": "product_grid",
            "gallery": "gallery",
            "reservations": "contact",
            "mission": "custom",
            "impact": "custom",
            "programs": "features",
            "donate": "cta",
            "volunteer": "contact",
            "courses": "features",
            "instructors": "team",
            "enroll": "cta",
            "featured_listings": "product_grid",
            "search": "custom",
            "agents": "team",
            "social_proof": "testimonials",
            "featured_posts": "blog_grid",
            "recent_posts": "blog_grid",
        }
        return mapping.get(section_name, "custom")
