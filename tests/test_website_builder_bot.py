"""
Tests for bots/website_builder_bot — Website Builder Bot.

Covers:
  - AIWebsiteGenerator (prompt detection, website generation)
  - DragDropEditor (sections, reorder, visibility, export)
  - WidgetLibrary (add, remove, catalogue)
  - LivePreview (render, retrieve, invalidate)
  - DeploymentEngine (deploy, simulate live, rollback, targets)
  - VibeCoder (component generation, scaffold, convert)
  - WebsiteBuilderBot (integration, process, chat)
"""
from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.website_builder_bot.ai_generator import (
    AIWebsiteGenerator,
    AIWebsiteGeneratorError,
    GeneratedWebsite,
    WebsiteType,
)
from bots.website_builder_bot.drag_drop_editor import (
    DragDropEditor,
    DragDropEditorError,
    LayoutSection,
    SectionType,
    SECTION_TYPES,
)
from bots.website_builder_bot.widget_library import (
    Widget,
    WidgetLibrary,
    WidgetLibraryError,
    WidgetType,
    WIDGET_TYPES,
)
from bots.website_builder_bot.live_preview import LivePreview, LivePreviewError
from bots.website_builder_bot.deployment_engine import (
    DeploymentEngine,
    DeploymentEngineError,
    DeployTarget,
    DEPLOY_TARGETS,
)
from bots.website_builder_bot.vibe_coder import (
    VibeCoder,
    VibeCoderError,
    Framework,
    FRAMEWORKS,
)
from bots.website_builder_bot.website_builder_bot import (
    WebsiteBuilderBot,
    WebsiteBuilderBotError,
)


# ===========================================================================
# AIWebsiteGenerator
# ===========================================================================


class TestAIWebsiteGeneratorDetection:
    def setup_method(self):
        self.gen = AIWebsiteGenerator()

    def test_detects_ecommerce(self):
        assert self.gen.detect_website_type("I want to sell products online") == WebsiteType.ECOMMERCE

    def test_detects_blog(self):
        assert self.gen.detect_website_type("Create a blog for my travel stories") == WebsiteType.BLOG

    def test_detects_portfolio(self):
        assert self.gen.detect_website_type("Show my photography portfolio") == WebsiteType.PORTFOLIO

    def test_detects_saas(self):
        assert self.gen.detect_website_type("SaaS platform with dashboard") == WebsiteType.SAAS

    def test_detects_restaurant(self):
        assert self.gen.detect_website_type("Restaurant cafe food menu site") == WebsiteType.RESTAURANT

    def test_defaults_to_corporate(self):
        result = self.gen.detect_website_type("something completely generic")
        assert isinstance(result, WebsiteType)


class TestAIWebsiteGeneratorGeneration:
    def setup_method(self):
        self.gen = AIWebsiteGenerator()

    def test_returns_generated_website(self):
        site = self.gen.generate_website("Online shoe shop", "ShoeCo")
        assert isinstance(site, GeneratedWebsite)

    def test_site_has_id(self):
        site = self.gen.generate_website("Online shoe shop", "ShoeCo")
        assert site.site_id and len(site.site_id) > 0

    def test_site_name_set(self):
        site = self.gen.generate_website("Online shoe shop", "ShoeCo")
        assert site.site_name == "ShoeCo"

    def test_explicit_type_respected(self):
        site = self.gen.generate_website(
            "generic prompt", "MySite", website_type=WebsiteType.BLOG
        )
        assert site.website_type == WebsiteType.BLOG

    def test_color_overrides_applied(self):
        site = self.gen.generate_website(
            "Shop", "Store", color_overrides={"primary": "#FF0000"}
        )
        assert site.color_scheme["primary"] == "#FF0000"

    def test_html_scaffold_generated(self):
        site = self.gen.generate_website("Blog about cooking", "FoodBlog")
        assert "<!DOCTYPE html>" in site.html_scaffold
        assert "FoodBlog" in site.html_scaffold

    def test_css_scaffold_generated(self):
        site = self.gen.generate_website("Blog about cooking", "FoodBlog")
        assert ":root" in site.css_scaffold
        assert "--color-primary" in site.css_scaffold

    def test_js_scaffold_generated(self):
        site = self.gen.generate_website("Blog", "Blog")
        assert "DOMContentLoaded" in site.js_scaffold

    def test_seo_keys_present(self):
        site = self.gen.generate_website("Online shop", "Shop")
        for key in ("title", "description", "keywords", "og_title", "robots"):
            assert key in site.seo

    def test_pages_not_empty(self):
        site = self.gen.generate_website("Saas app", "AppCo")
        assert len(site.pages) > 0

    def test_features_not_empty(self):
        site = self.gen.generate_website("Ecommerce store", "Store")
        assert len(site.features) > 0

    def test_empty_prompt_raises(self):
        with pytest.raises(AIWebsiteGeneratorError):
            self.gen.generate_website("", "Site")

    def test_empty_site_name_raises(self):
        with pytest.raises(AIWebsiteGeneratorError):
            self.gen.generate_website("Some prompt", "")

    def test_get_site(self):
        site = self.gen.generate_website("Portfolio", "MyPort")
        retrieved = self.gen.get_site(site.site_id)
        assert retrieved.site_id == site.site_id

    def test_get_unknown_site_raises(self):
        with pytest.raises(AIWebsiteGeneratorError):
            self.gen.get_site("nonexistent-id")

    def test_list_sites(self):
        self.gen.generate_website("Site 1", "One")
        self.gen.generate_website("Site 2", "Two")
        assert len(self.gen.list_sites()) >= 2


# ===========================================================================
# DragDropEditor
# ===========================================================================


class TestDragDropEditorProject:
    def setup_method(self):
        self.editor = DragDropEditor()

    def test_create_project_returns_dict(self):
        proj = self.editor.create_project("user1", "My Site")
        assert isinstance(proj, dict)
        assert proj["site_name"] == "My Site"
        assert "id" in proj

    def test_empty_site_name_raises(self):
        with pytest.raises(DragDropEditorError):
            self.editor.create_project("user1", "")

    def test_project_has_sections(self):
        proj = self.editor.create_project("u", "S")
        assert proj["sections"] == []


class TestDragDropEditorSections:
    def setup_method(self):
        self.editor = DragDropEditor()
        self.proj = self.editor.create_project("u1", "TestSite")
        self.pid = self.proj["id"]

    def test_add_hero_section(self):
        sec = self.editor.add_section(self.pid, "hero")
        assert isinstance(sec, LayoutSection)
        assert sec.section_type == "hero"

    def test_add_section_invalid_type_raises(self):
        with pytest.raises(DragDropEditorError):
            self.editor.add_section(self.pid, "invalid_section_type")

    def test_list_sections_ordered(self):
        self.editor.add_section(self.pid, "hero")
        self.editor.add_section(self.pid, "features")
        self.editor.add_section(self.pid, "footer")
        sections = self.editor.list_sections(self.pid)
        assert len(sections) == 3
        assert sections[0].section_type == "hero"
        assert sections[2].section_type == "footer"

    def test_remove_section(self):
        sec = self.editor.add_section(self.pid, "hero")
        result = self.editor.remove_section(self.pid, sec.section_id)
        assert result["removed"] == sec.section_id
        assert len(self.editor.list_sections(self.pid)) == 0

    def test_remove_unknown_section_raises(self):
        with pytest.raises(DragDropEditorError):
            self.editor.remove_section(self.pid, "bad-id")

    def test_move_section_reorders(self):
        s1 = self.editor.add_section(self.pid, "hero")
        s2 = self.editor.add_section(self.pid, "features")
        s3 = self.editor.add_section(self.pid, "footer")
        self.editor.move_section(self.pid, s3.section_id, 0)
        ordered = self.editor.list_sections(self.pid)
        assert ordered[0].section_id == s3.section_id
        assert ordered[1].section_id == s1.section_id

    def test_update_section_config(self):
        sec = self.editor.add_section(self.pid, "hero", {"title": "Hello"})
        updated = self.editor.update_section_config(
            self.pid, sec.section_id, {"subtitle": "World"}
        )
        assert updated.config["title"] == "Hello"
        assert updated.config["subtitle"] == "World"

    def test_toggle_visibility(self):
        sec = self.editor.add_section(self.pid, "hero")
        assert sec.visible is True
        toggled = self.editor.toggle_section_visibility(self.pid, sec.section_id)
        assert toggled.visible is False

    def test_lock_unlock_section(self):
        sec = self.editor.add_section(self.pid, "hero")
        locked = self.editor.lock_section(self.pid, sec.section_id)
        assert locked.locked is True
        unlocked = self.editor.unlock_section(self.pid, sec.section_id)
        assert unlocked.locked is False

    def test_positions_reindexed_after_move(self):
        self.editor.add_section(self.pid, "hero")
        s2 = self.editor.add_section(self.pid, "features")
        self.editor.add_section(self.pid, "footer")
        self.editor.move_section(self.pid, s2.section_id, 0)
        sections = self.editor.list_sections(self.pid)
        for i, sec in enumerate(sections):
            assert sec.position == i


class TestDragDropEditorExport:
    def setup_method(self):
        self.editor = DragDropEditor()
        self.proj = self.editor.create_project("u1", "ExportSite")
        self.pid = self.proj["id"]

    def test_export_layout_keys(self):
        self.editor.add_section(self.pid, "hero")
        layout = self.editor.export_layout(self.pid)
        assert "project_id" in layout
        assert "site_name" in layout
        assert "sections" in layout
        assert "total_sections" in layout

    def test_export_section_count(self):
        self.editor.add_section(self.pid, "hero")
        self.editor.add_section(self.pid, "features")
        layout = self.editor.export_layout(self.pid)
        assert layout["total_sections"] == 2


# ===========================================================================
# WidgetLibrary
# ===========================================================================


class TestWidgetLibrary:
    def setup_method(self):
        self.lib = WidgetLibrary()

    def test_add_seo_widget(self):
        w = self.lib.add_widget("page1", "seo_analyzer")
        assert isinstance(w, Widget)
        assert w.widget_type == "seo_analyzer"

    def test_add_invalid_widget_raises(self):
        with pytest.raises(WidgetLibraryError):
            self.lib.add_widget("page1", "not_a_widget")

    def test_list_widgets(self):
        self.lib.add_widget("p1", "seo_analyzer")
        self.lib.add_widget("p1", "contact_form")
        widgets = self.lib.list_widgets("p1")
        assert len(widgets) == 2

    def test_list_widgets_empty_page(self):
        assert self.lib.list_widgets("unknown_page") == []

    def test_remove_widget(self):
        w = self.lib.add_widget("page1", "image_slider")
        result = self.lib.remove_widget("page1", w.widget_id)
        assert result["removed"] == w.widget_id
        assert len(self.lib.list_widgets("page1")) == 0

    def test_remove_unknown_widget_raises(self):
        with pytest.raises(WidgetLibraryError):
            self.lib.remove_widget("page1", "bad-widget-id")

    def test_update_widget_config(self):
        w = self.lib.add_widget("p1", "popup", {"delay": 3})
        updated = self.lib.update_widget_config(w.widget_id, {"delay": 5})
        assert updated.config["delay"] == 5

    def test_toggle_widget_disables(self):
        w = self.lib.add_widget("p1", "live_chat")
        assert w.enabled is True
        toggled = self.lib.toggle_widget(w.widget_id)
        assert toggled.enabled is False

    def test_get_widget(self):
        w = self.lib.add_widget("p1", "countdown_timer")
        retrieved = self.lib.get_widget(w.widget_id)
        assert retrieved.widget_id == w.widget_id

    def test_browse_catalogue_not_empty(self):
        catalogue = self.lib.browse_catalogue()
        assert len(catalogue) > 0
        assert all("widget_type" in item for item in catalogue)

    def test_all_widget_types_in_catalogue(self):
        catalogue = self.lib.browse_catalogue()
        types_in_cat = {item["widget_type"] for item in catalogue}
        for wt in WIDGET_TYPES:
            assert wt in types_in_cat

    def test_widget_has_description(self):
        w = self.lib.add_widget("p1", "seo_analyzer")
        assert len(w.description) > 0


# ===========================================================================
# LivePreview
# ===========================================================================


class TestLivePreview:
    def setup_method(self):
        self.lp = LivePreview()

    def test_render_returns_preview_id(self):
        result = self.lp.render_preview("TestSite")
        assert "preview_id" in result
        assert result["preview_id"].startswith("prev_")

    def test_render_returns_html(self):
        result = self.lp.render_preview("TestSite")
        assert "html" in result
        assert "<!DOCTYPE html>" in result["html"]

    def test_html_contains_site_name(self):
        result = self.lp.render_preview("AwesomeSite")
        assert "AwesomeSite" in result["html"]

    def test_render_with_sections(self):
        sections = [
            {"section_id": "s1", "section_type": "hero", "visible": True, "config": {}},
            {"section_id": "s2", "section_type": "features", "visible": True, "config": {}},
        ]
        result = self.lp.render_preview("MySite", sections=sections)
        assert "HERO" in result["html"]
        assert "FEATURES" in result["html"]

    def test_render_with_widgets(self):
        sections = [
            {"section_id": "s1", "section_type": "hero", "visible": True, "config": {}}
        ]
        widgets = {
            "s1": [
                {
                    "widget_type": "image_slider",
                    "label": "Image Slider",
                    "description": "desc",
                    "enabled": True,
                }
            ]
        }
        result = self.lp.render_preview("MySite", sections=sections, widgets_by_section=widgets)
        assert "Image Slider" in result["html"]

    def test_hidden_section_class(self):
        sections = [
            {"section_id": "s1", "section_type": "hero", "visible": False, "config": {}}
        ]
        result = self.lp.render_preview("Site", sections=sections)
        assert "hidden-section" in result["html"]

    def test_empty_sections_placeholder(self):
        result = self.lp.render_preview("EmptySite", sections=[])
        assert "No sections added yet" in result["html"]

    def test_get_preview(self):
        result = self.lp.render_preview("Site")
        retrieved = self.lp.get_preview(result["preview_id"])
        assert retrieved["preview_id"] == result["preview_id"]

    def test_get_unknown_preview_raises(self):
        with pytest.raises(LivePreviewError):
            self.lp.get_preview("bad-id")

    def test_invalidate_preview(self):
        result = self.lp.render_preview("Site")
        pid = result["preview_id"]
        invalidated = self.lp.invalidate_preview(pid)
        assert invalidated["invalidated"] == pid
        with pytest.raises(LivePreviewError):
            self.lp.get_preview(pid)

    def test_list_previews(self):
        self.lp.render_preview("Site A")
        self.lp.render_preview("Site B")
        previews = self.lp.list_previews()
        assert len(previews) >= 2
        assert all("html" not in p for p in previews)

    def test_color_scheme_applied(self):
        result = self.lp.render_preview(
            "ColorSite", color_scheme={"primary": "#ABCDEF"}
        )
        assert "#ABCDEF" in result["html"]


# ===========================================================================
# DeploymentEngine
# ===========================================================================


class TestDeploymentEngine:
    def setup_method(self):
        self.engine = DeploymentEngine()

    def test_deploy_vercel_returns_deploying(self):
        dep = self.engine.deploy("site1", "MySite", "vercel")
        assert dep["status"] == "DEPLOYING"
        assert "deployment_id" in dep

    def test_deploy_creates_endpoint_url(self):
        dep = self.engine.deploy("site1", "MySite", "vercel")
        assert "vercel.app" in dep["endpoint_url"]

    def test_deploy_netlify(self):
        dep = self.engine.deploy("site1", "MySite", "netlify")
        assert "netlify.app" in dep["endpoint_url"]

    def test_deploy_aws(self):
        dep = self.engine.deploy("site1", "MySite", "aws")
        assert "amazonaws.com" in dep["endpoint_url"]

    def test_deploy_local(self):
        dep = self.engine.deploy("site1", "MySite", "local")
        assert "localhost" in dep["endpoint_url"]
        assert dep["ssl_enabled"] is False

    def test_deploy_unknown_target_raises(self):
        with pytest.raises(DeploymentEngineError):
            self.engine.deploy("site1", "MySite", "unknown_platform")

    def test_simulate_live(self):
        dep = self.engine.deploy("site1", "MySite", "vercel")
        live = self.engine.simulate_live(dep["deployment_id"])
        assert live["status"] == "LIVE"
        assert live["live_at"] is not None

    def test_get_deployment(self):
        dep = self.engine.deploy("site1", "MySite", "netlify")
        record = self.engine.get_deployment(dep["deployment_id"])
        assert record["deployment_id"] == dep["deployment_id"]

    def test_list_deployments(self):
        self.engine.deploy("site42", "S1", "vercel")
        self.engine.deploy("site42", "S2", "netlify")
        deps = self.engine.list_deployments("site42")
        assert len(deps) == 2

    def test_rollback_live(self):
        dep = self.engine.deploy("site1", "MySite", "vercel")
        self.engine.simulate_live(dep["deployment_id"])
        rb = self.engine.rollback(dep["deployment_id"])
        assert rb["status"] == "ROLLED_BACK"

    def test_rollback_already_rolled_back_raises(self):
        dep = self.engine.deploy("site1", "MySite", "vercel")
        self.engine.simulate_live(dep["deployment_id"])
        self.engine.rollback(dep["deployment_id"])
        with pytest.raises(DeploymentEngineError):
            self.engine.rollback(dep["deployment_id"])

    def test_get_targets_info(self):
        targets = self.engine.get_targets_info()
        assert len(targets) > 0
        assert all("target" in t and "features" in t for t in targets)

    def test_all_deploy_targets_present(self):
        info = self.engine.get_targets_info()
        info_targets = {t["target"] for t in info}
        for dt in DEPLOY_TARGETS:
            assert dt in info_targets

    def test_custom_domain_stored(self):
        dep = self.engine.deploy(
            "site1", "MySite", "vercel", custom_domain="mysite.com"
        )
        record = self.engine.get_deployment(dep["deployment_id"])
        assert record["custom_domain"] == "mysite.com"


# ===========================================================================
# VibeCoder
# ===========================================================================


class TestVibeCoderComponents:
    def setup_method(self):
        self.vc = VibeCoder()

    def test_generate_react_component(self):
        result = self.vc.generate_component("react", "A hero section with CTA")
        assert result["framework"] == "react"
        assert "import React" in result["code"]
        assert result["extension"] == ".jsx"

    def test_generate_vue_component(self):
        result = self.vc.generate_component("vue", "A product card")
        assert "<template>" in result["code"]
        assert result["extension"] == ".vue"

    def test_generate_svelte_component(self):
        result = self.vc.generate_component("svelte", "A testimonial section")
        assert "<script>" in result["code"]
        assert result["extension"] == ".svelte"

    def test_generate_html_component(self):
        result = self.vc.generate_component("html", "A contact form")
        assert "<section" in result["code"]
        assert result["extension"] == ".html"

    def test_generate_angular_component(self):
        result = self.vc.generate_component("angular", "A navigation bar")
        assert "@Component" in result["code"]
        assert result["extension"] == ".ts"

    def test_generate_nextjs_component(self):
        result = self.vc.generate_component("nextjs", "A pricing table")
        assert "import React" in result["code"]
        assert result["extension"] == ".tsx"

    def test_generate_scss_component(self):
        result = self.vc.generate_component("scss", "Hero styles")
        assert "$primary" in result["code"]
        assert result["extension"] == ".scss"

    def test_generate_typescript_component(self):
        result = self.vc.generate_component("typescript", "Navigation module")
        assert ": void" in result["code"]
        assert result["extension"] == ".ts"

    def test_unknown_framework_raises(self):
        with pytest.raises(VibeCoderError):
            self.vc.generate_component("cobol", "Something")

    def test_empty_prompt_raises(self):
        with pytest.raises(VibeCoderError):
            self.vc.generate_component("react", "")

    def test_component_name_respected(self):
        result = self.vc.generate_component("react", "Desc", component_name="HeroSection")
        assert "HeroSection" in result["code"]

    def test_snippet_id_generated(self):
        result = self.vc.generate_component("vue", "A navbar")
        assert result["snippet_id"].startswith("snip_")

    def test_get_snippet(self):
        result = self.vc.generate_component("react", "A footer")
        retrieved = self.vc.get_snippet(result["snippet_id"])
        assert retrieved["snippet_id"] == result["snippet_id"]

    def test_get_unknown_snippet_raises(self):
        with pytest.raises(VibeCoderError):
            self.vc.get_snippet("bad-id")


class TestVibeCoderScaffold:
    def setup_method(self):
        self.vc = VibeCoder()

    def test_scaffold_nextjs(self):
        result = self.vc.scaffold_project("nextjs", "my-store")
        assert result["framework"] == "nextjs"
        assert "npx create-next-app" in result["install_cmd"]
        assert len(result["files"]) > 0
        assert len(result["directories"]) > 0

    def test_scaffold_react(self):
        result = self.vc.scaffold_project("react", "my-app")
        assert "npx create-react-app" in result["install_cmd"]

    def test_scaffold_invalid_framework_raises(self):
        with pytest.raises(VibeCoderError):
            self.vc.scaffold_project("cobol", "bad")

    def test_list_frameworks(self):
        frameworks = self.vc.list_frameworks()
        assert len(frameworks) > 0
        fw_values = {f["framework"] for f in frameworks}
        for fw in ("react", "vue", "svelte", "nextjs", "html"):
            assert fw in fw_values

    def test_convert_snippet(self):
        react_snip = self.vc.generate_component("react", "A hero section")
        vue_snip = self.vc.convert_snippet(react_snip["snippet_id"], "vue")
        assert vue_snip["framework"] == "vue"

    def test_list_snippets(self):
        self.vc.generate_component("react", "A")
        self.vc.generate_component("vue", "B")
        snippets = self.vc.list_snippets()
        assert len(snippets) >= 2


# ===========================================================================
# WebsiteBuilderBot (Integration)
# ===========================================================================


class TestWebsiteBuilderBotGeneration:
    def setup_method(self):
        self.bot = WebsiteBuilderBot()

    def test_generate_returns_site(self):
        site = self.bot.generate("Build a restaurant with food menu and dining", "Brew & Co")
        assert site.site_name == "Brew & Co"
        assert site.website_type == WebsiteType.RESTAURANT

    def test_detect_type(self):
        wtype = self.bot.detect_type("I want to sell shoes online")
        assert wtype == WebsiteType.ECOMMERCE

    def test_list_sites_after_generate(self):
        self.bot.generate("Blog site", "MyBlog")
        sites = self.bot.list_sites()
        assert len(sites) >= 1


class TestWebsiteBuilderBotEditor:
    def setup_method(self):
        self.bot = WebsiteBuilderBot()
        self.site = self.bot.generate("Online store for gadgets", "GadgetHub")

    def test_open_editor_returns_project(self):
        project = self.bot.open_editor(self.site.site_id, "user_001")
        assert "id" in project
        assert project["site_name"] == "GadgetHub"

    def test_open_editor_idempotent(self):
        p1 = self.bot.open_editor(self.site.site_id, "user_001")
        p2 = self.bot.open_editor(self.site.site_id, "user_001")
        assert p1["id"] == p2["id"]

    def test_open_editor_prepopulates_sections(self):
        project = self.bot.open_editor(self.site.site_id, "user_001")
        pid = project["id"]
        sections = self.bot._editor.list_sections(pid)
        assert len(sections) > 0

    def test_add_section(self):
        project = self.bot.open_editor(self.site.site_id, "user_002")
        pid = project["id"]
        initial = len(self.bot._editor.list_sections(pid))
        self.bot.add_section(pid, "contact")
        assert len(self.bot._editor.list_sections(pid)) == initial + 1

    def test_export_layout(self):
        project = self.bot.open_editor(self.site.site_id, "user_003")
        layout = self.bot.export_layout(project["id"])
        assert "sections" in layout


class TestWebsiteBuilderBotWidgets:
    def setup_method(self):
        self.bot = WebsiteBuilderBot()

    def test_add_widget(self):
        w = self.bot.add_widget("page_001", "seo_analyzer")
        assert w.widget_type == "seo_analyzer"

    def test_list_widgets(self):
        self.bot.add_widget("page_002", "seo_analyzer")
        self.bot.add_widget("page_002", "analytics_dashboard")
        widgets = self.bot.list_widgets("page_002")
        assert len(widgets) == 2

    def test_browse_widgets(self):
        catalogue = self.bot.browse_widgets()
        assert len(catalogue) > 10


class TestWebsiteBuilderBotPreview:
    def setup_method(self):
        self.bot = WebsiteBuilderBot()
        self.site = self.bot.generate("Portfolio for designers", "DesignHub")
        self.project = self.bot.open_editor(self.site.site_id, "u1")
        self.pid = self.project["id"]

    def test_preview_returns_html(self):
        result = self.bot.preview(self.pid)
        assert "html" in result
        assert "<!DOCTYPE html>" in result["html"]

    def test_preview_contains_site_name(self):
        result = self.bot.preview(self.pid)
        assert "DesignHub" in result["html"]


class TestWebsiteBuilderBotDeploy:
    def setup_method(self):
        self.bot = WebsiteBuilderBot()
        self.site = self.bot.generate("SaaS product site", "AppSuite")

    def test_deploy_vercel(self):
        dep = self.bot.deploy(self.site.site_id, self.site.site_name, "vercel")
        assert dep["status"] == "DEPLOYING"
        assert "vercel.app" in dep["endpoint_url"]

    def test_deploy_and_go_live(self):
        dep = self.bot.deploy(self.site.site_id, self.site.site_name, "netlify")
        live = self.bot.go_live(dep["deployment_id"])
        assert live["status"] == "LIVE"

    def test_rollback_deployment(self):
        dep = self.bot.deploy(self.site.site_id, self.site.site_name, "aws")
        self.bot.go_live(dep["deployment_id"])
        rb = self.bot.rollback_deployment(dep["deployment_id"])
        assert rb["status"] == "ROLLED_BACK"

    def test_list_deploy_targets(self):
        targets = self.bot.list_deploy_targets()
        assert len(targets) > 0


class TestWebsiteBuilderBotVibeCoding:
    def setup_method(self):
        self.bot = WebsiteBuilderBot()

    def test_vibe_code_react(self):
        result = self.bot.vibe_code("react", "A hero section with headline and CTA")
        assert result["framework"] == "react"
        assert len(result["code"]) > 0

    def test_scaffold_nextjs(self):
        result = self.bot.scaffold("nextjs", "my-store")
        assert "create-next-app" in result["install_cmd"]

    def test_convert_code(self):
        react = self.bot.vibe_code("react", "A footer component")
        vue = self.bot.convert_code(react["snippet_id"], "vue")
        assert vue["framework"] == "vue"

    def test_list_frameworks(self):
        frameworks = self.bot.list_frameworks()
        assert any(f["framework"] == "svelte" for f in frameworks)


class TestWebsiteBuilderBotProcess:
    def setup_method(self):
        self.bot = WebsiteBuilderBot()

    def test_process_generate(self):
        result = self.bot.process(
            {"action": "generate", "prompt": "An online bookstore", "site_name": "BookWorld"}
        )
        assert result["action"] == "generate"
        assert "site_id" in result
        assert "pages" in result

    def test_process_vibe_code(self):
        result = self.bot.process(
            {
                "action": "vibe_code",
                "framework": "svelte",
                "prompt": "A testimonials section",
            }
        )
        assert result["action"] == "vibe_code"
        assert result["framework"] == "svelte"

    def test_process_unknown_action(self):
        result = self.bot.process({"action": "fly_to_moon"})
        assert "error" in result
        assert "supported_actions" in result

    def test_process_deploy(self):
        site = self.bot.generate("Blog", "Blog")
        result = self.bot.process(
            {
                "action": "deploy",
                "site_id": site.site_id,
                "site_name": site.site_name,
                "target": "netlify",
            }
        )
        assert result["action"] == "deploy"
        assert result["status"] == "DEPLOYING"


class TestWebsiteBuilderBotChat:
    def setup_method(self):
        self.bot = WebsiteBuilderBot()

    def test_chat_build_intent(self):
        result = self.bot.chat("I want to build a website")
        assert "suggested_action" in result
        assert result["suggested_action"] == "generate"

    def test_chat_deploy_intent(self):
        result = self.bot.chat("How do I deploy my site?")
        assert result["suggested_action"] == "deploy"

    def test_chat_preview_intent(self):
        result = self.bot.chat("Can I see a preview?")
        assert result["suggested_action"] == "preview"

    def test_chat_code_intent(self):
        result = self.bot.chat("I want to use React to code my site")
        assert result["suggested_action"] == "vibe_code"

    def test_chat_generic_response(self):
        result = self.bot.chat("Hello!")
        assert "response" in result
