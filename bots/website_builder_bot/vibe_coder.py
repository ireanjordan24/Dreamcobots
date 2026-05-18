"""
Vibe Coder — full-spectrum code generation for every web framework.

Supports every way a human can create, design, or code a website:
  - Raw HTML/CSS/JavaScript
  - React, Vue, Svelte, Angular, Astro, SolidJS, Qwik
  - Next.js, Nuxt, SvelteKit, Remix, Gatsby
  - Tailwind CSS, SCSS/SASS, CSS Modules, Styled Components
  - TypeScript, JSX/TSX

Integrates with the DreamCo AI pipeline for prompt-driven code generation.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class Framework(Enum):
    """Supported front-end frameworks and languages."""

    # Vanilla
    HTML = "html"
    CSS = "css"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    # Component frameworks
    REACT = "react"
    REACT_TS = "react_ts"
    VUE = "vue"
    VUE_TS = "vue_ts"
    SVELTE = "svelte"
    ANGULAR = "angular"
    SOLID = "solid"
    QWIK = "qwik"
    ASTRO = "astro"
    # Meta-frameworks
    NEXTJS = "nextjs"
    NUXT = "nuxt"
    SVELTEKIT = "sveltekit"
    REMIX = "remix"
    GATSBY = "gatsby"
    # CSS frameworks
    TAILWIND = "tailwind"
    SCSS = "scss"
    CSS_MODULES = "css_modules"
    STYLED_COMPONENTS = "styled_components"


FRAMEWORKS: List[str] = [f.value for f in Framework]

# File extension per framework
_EXTENSIONS: dict = {
    Framework.HTML: ".html",
    Framework.CSS: ".css",
    Framework.JAVASCRIPT: ".js",
    Framework.TYPESCRIPT: ".ts",
    Framework.REACT: ".jsx",
    Framework.REACT_TS: ".tsx",
    Framework.VUE: ".vue",
    Framework.VUE_TS: ".vue",
    Framework.SVELTE: ".svelte",
    Framework.ANGULAR: ".ts",
    Framework.SOLID: ".jsx",
    Framework.QWIK: ".tsx",
    Framework.ASTRO: ".astro",
    Framework.NEXTJS: ".tsx",
    Framework.NUXT: ".vue",
    Framework.SVELTEKIT: ".svelte",
    Framework.REMIX: ".tsx",
    Framework.GATSBY: ".tsx",
    Framework.TAILWIND: ".css",
    Framework.SCSS: ".scss",
    Framework.CSS_MODULES: ".module.css",
    Framework.STYLED_COMPONENTS: ".tsx",
}

# Package manager install command per framework
_INSTALL_CMDS: dict = {
    Framework.REACT: "npx create-react-app my-app",
    Framework.REACT_TS: "npx create-react-app my-app --template typescript",
    Framework.VUE: "npm create vue@latest my-app",
    Framework.VUE_TS: "npm create vue@latest my-app -- --typescript",
    Framework.SVELTE: "npm create svelte@latest my-app",
    Framework.ANGULAR: "npx @angular/cli new my-app",
    Framework.SOLID: "npx degit solidjs/templates/js my-app",
    Framework.QWIK: "npm create qwik@latest my-app",
    Framework.ASTRO: "npm create astro@latest my-app",
    Framework.NEXTJS: "npx create-next-app@latest my-app",
    Framework.NUXT: "npx nuxi@latest init my-app",
    Framework.SVELTEKIT: "npm create svelte@latest my-app",
    Framework.REMIX: "npx create-remix@latest my-app",
    Framework.GATSBY: "npx gatsby new my-app",
    Framework.TAILWIND: "npm install -D tailwindcss postcss autoprefixer",
    Framework.SCSS: "npm install -D sass",
    Framework.STYLED_COMPONENTS: "npm install styled-components",
}


class VibeCoderError(Exception):
    """Raised for invalid vibe-coding operations."""


class VibeCoder:
    """Generate framework-specific code from natural-language prompts or templates.

    Supports every mainstream web framework and styling system. Generated
    snippets and full-project scaffolds are cached by ``snippet_id``.

    Usage::

        vc = VibeCoder()
        result = vc.generate_component("react", "A hero section with CTA button")
        scaffold = vc.scaffold_project("nextjs", "my-store")
    """

    def __init__(self) -> None:
        self._snippets: dict = {}  # snippet_id -> snippet dict

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_component(
        self,
        framework: str,
        prompt: str,
        component_name: Optional[str] = None,
    ) -> dict:
        """Generate a single component/snippet for *framework* from *prompt*.

        Parameters
        ----------
        framework:       One of ``FRAMEWORKS``.
        prompt:          Natural-language description of the component.
        component_name:  Optional name for the component (auto-generated if omitted).

        Returns
        -------
        dict  ``{snippet_id, framework, component_name, code, extension, created_at}``
        """
        if framework not in FRAMEWORKS:
            raise VibeCoderError(
                f"Unknown framework '{framework}'. Valid: {FRAMEWORKS}"
            )
        if not prompt or not prompt.strip():
            raise VibeCoderError("prompt must not be empty.")

        fw_enum = Framework(framework)
        name = component_name or self._name_from_prompt(prompt)
        code = self._generate_code(fw_enum, name, prompt)

        snippet_id = f"snip_{uuid.uuid4().hex[:10]}"
        record = {
            "snippet_id": snippet_id,
            "framework": framework,
            "component_name": name,
            "prompt": prompt.strip(),
            "code": code,
            "extension": _EXTENSIONS.get(fw_enum, ".txt"),
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        self._snippets[snippet_id] = record
        return record

    def scaffold_project(
        self,
        framework: str,
        project_name: str,
    ) -> dict:
        """Return a full project scaffold spec for *framework*.

        Parameters
        ----------
        framework:     One of ``FRAMEWORKS``.
        project_name:  Name of the project directory.

        Returns
        -------
        dict  ``{framework, project_name, install_cmd, files, directories}``
        """
        if framework not in FRAMEWORKS:
            raise VibeCoderError(
                f"Unknown framework '{framework}'. Valid: {FRAMEWORKS}"
            )
        fw_enum = Framework(framework)
        return {
            "framework": framework,
            "project_name": project_name,
            "install_cmd": _INSTALL_CMDS.get(fw_enum, f"npm init {project_name}"),
            "files": self._scaffold_files(fw_enum, project_name),
            "directories": self._scaffold_dirs(fw_enum),
        }

    def convert_snippet(
        self,
        snippet_id: str,
        target_framework: str,
    ) -> dict:
        """Convert a saved snippet to another framework.

        Parameters
        ----------
        snippet_id:        ID of the source snippet.
        target_framework:  Framework to convert the snippet into.

        Returns
        -------
        dict  New snippet record in *target_framework*.
        """
        if snippet_id not in self._snippets:
            raise VibeCoderError(f"Snippet '{snippet_id}' not found.")
        source = self._snippets[snippet_id]
        return self.generate_component(
            target_framework,
            source["prompt"],
            source["component_name"],
        )

    def get_snippet(self, snippet_id: str) -> dict:
        """Retrieve a previously generated snippet.

        Returns
        -------
        dict
        """
        if snippet_id not in self._snippets:
            raise VibeCoderError(f"Snippet '{snippet_id}' not found.")
        return self._snippets[snippet_id]

    def list_snippets(self) -> List[dict]:
        """Return all generated snippets.

        Returns
        -------
        list[dict]
        """
        return list(self._snippets.values())

    def list_frameworks(self) -> List[dict]:
        """Return metadata about all supported frameworks.

        Returns
        -------
        list[dict]
        """
        return [
            {
                "framework": f.value,
                "extension": _EXTENSIONS.get(f, ".txt"),
                "install_cmd": _INSTALL_CMDS.get(f, ""),
            }
            for f in Framework
        ]

    # ------------------------------------------------------------------
    # Internal code-generation helpers
    # ------------------------------------------------------------------

    def _name_from_prompt(self, prompt: str) -> str:
        """Derive a PascalCase component name from a short prompt."""
        words = prompt.strip().split()[:4]
        return (
            "".join(w.capitalize() for w in words if w.isalpha()) or "MyComponent"
        )

    def _generate_code(self, fw: Framework, name: str, prompt: str) -> str:
        """Return a framework-appropriate code scaffold for *name*."""
        if fw == Framework.HTML:
            return self._html_component(name, prompt)
        if fw in (Framework.CSS, Framework.TAILWIND):
            return self._css_component(name)
        if fw == Framework.SCSS:
            return self._scss_component(name)
        if fw in (Framework.JAVASCRIPT, Framework.TYPESCRIPT):
            return self._js_component(name, fw == Framework.TYPESCRIPT)
        if fw in (Framework.REACT, Framework.SOLID):
            return self._react_jsx(name, prompt, typescript=False)
        if fw in (
            Framework.REACT_TS, Framework.NEXTJS, Framework.REMIX,
            Framework.GATSBY, Framework.QWIK,
        ):
            return self._react_jsx(name, prompt, typescript=True)
        if fw in (Framework.VUE, Framework.NUXT):
            return self._vue_sfc(name, prompt, typescript=False)
        if fw == Framework.VUE_TS:
            return self._vue_sfc(name, prompt, typescript=True)
        if fw in (Framework.SVELTE, Framework.SVELTEKIT):
            return self._svelte_component(name, prompt)
        if fw == Framework.ANGULAR:
            return self._angular_component(name)
        if fw == Framework.ASTRO:
            return self._astro_component(name, prompt)
        if fw == Framework.STYLED_COMPONENTS:
            return self._styled_components(name, prompt)
        if fw == Framework.CSS_MODULES:
            return self._css_modules(name)
        return f"// {name} — {fw.value} component\n// Prompt: {prompt}\n"

    # ---- Per-framework templates ----------------------------------------

    def _html_component(self, name: str, prompt: str) -> str:
        return (
            f'<!-- {name} -->\n'
            f'<!-- {prompt} -->\n'
            f'<section class="{name.lower()}">\n'
            f'  <div class="container">\n'
            f'    <h2>{name}</h2>\n'
            f'    <p><!-- content here --></p>\n'
            f'  </div>\n'
            f'</section>\n'
        )

    def _css_component(self, name: str) -> str:
        cls = name.lower()
        return (
            f'.{cls} {{\n'
            f'  padding: 4rem 1.5rem;\n'
            f'  max-width: 1200px;\n'
            f'  margin: 0 auto;\n'
            f'}}\n\n'
            f'.{cls}__title {{\n'
            f'  font-size: 2rem;\n'
            f'  font-weight: 700;\n'
            f'  margin-bottom: 1rem;\n'
            f'}}\n'
        )

    def _scss_component(self, name: str) -> str:
        cls = name.lower()
        return (
            f'$primary: var(--color-primary);\n\n'
            f'.{cls} {{\n'
            f'  padding: 4rem 1.5rem;\n'
            f'  max-width: 1200px;\n'
            f'  margin: 0 auto;\n\n'
            f'  &__title {{\n'
            f'    font-size: 2rem;\n'
            f'    font-weight: 700;\n'
            f'    color: $primary;\n'
            f'  }}\n'
            f'}}\n'
        )

    def _js_component(self, name: str, typescript: bool) -> str:
        type_ann = ": void" if typescript else ""
        return (
            f'// {name}\n'
            f'export function init{name}(){type_ann} {{\n'
            f'  var sectionElement = document.querySelector(".{name.lower()}");\n'
            f'  if (!sectionElement) return;\n'
            f'  // TODO: implement {name} behaviour\n'
            f'}}\n'
        )

    def _react_jsx(self, name: str, prompt: str, typescript: bool) -> str:
        props_ann = ": React.FC" if typescript else ""
        return (
            f'import React from "react";\n\n'
            f'// {prompt}\n'
            f'const {name}{props_ann} = () => {{\n'
            f'  return (\n'
            f'    <section className="{name.lower()}">\n'
            f'      <div className="container">\n'
            f'        <h2>{name}</h2>\n'
            f'        {{/* TODO: add content */}}\n'
            f'      </div>\n'
            f'    </section>\n'
            f'  );\n'
            f'}};\n\n'
            f'export default {name};\n'
        )

    def _vue_sfc(self, name: str, prompt: str, typescript: bool) -> str:
        lang = ' lang="ts"' if typescript else ""
        return (
            f'<!-- {prompt} -->\n'
            f'<template>\n'
            f'  <section class="{name.lower()}">\n'
            f'    <div class="container">\n'
            f'      <h2>{{{{ title }}}}</h2>\n'
            f'    </div>\n'
            f'  </section>\n'
            f'</template>\n\n'
            f'<script{lang} setup>\n'
            f'const title = "{name}";\n'
            f'</script>\n\n'
            f'<style scoped>\n'
            f'.{name.lower()} {{ padding: 4rem 1.5rem; }}\n'
            f'</style>\n'
        )

    def _svelte_component(self, name: str, prompt: str) -> str:
        return (
            f'<!-- {prompt} -->\n'
            f'<script>\n'
            f'  let title = "{name}";\n'
            f'</script>\n\n'
            f'<section class="{name.lower()}">\n'
            f'  <div class="container">\n'
            f'    <h2>{{title}}</h2>\n'
            f'  </div>\n'
            f'</section>\n\n'
            f'<style>\n'
            f'  .{name.lower()} {{ padding: 4rem 1.5rem; }}\n'
            f'</style>\n'
        )

    def _angular_component(self, name: str) -> str:
        selector = name.lower().replace(" ", "-")
        return (
            f'import {{ Component }} from "@angular/core";\n\n'
            f'@Component({{\n'
            f'  selector: "app-{selector}",\n'
            f'  template: `\n'
            f'    <section class="{selector}">\n'
            f'      <div class="container">\n'
            f'        <h2>{name}</h2>\n'
            f'      </div>\n'
            f'    </section>\n'
            f'  `,\n'
            f'  styles: [`.{selector}{{padding:4rem 1.5rem}}`],\n'
            f'}})\n'
            f'export class {name}Component {{}}\n'
        )

    def _astro_component(self, name: str, prompt: str) -> str:
        return (
            f'---\n'
            f'// {prompt}\n'
            f'const title = "{name}";\n'
            f'---\n\n'
            f'<section class="{name.lower()}">\n'
            f'  <div class="container">\n'
            f'    <h2>{{title}}</h2>\n'
            f'  </div>\n'
            f'</section>\n\n'
            f'<style>\n'
            f'  .{name.lower()} {{ padding: 4rem 1.5rem; }}\n'
            f'</style>\n'
        )

    def _styled_components(self, name: str, prompt: str) -> str:
        return (
            f'import React from "react";\n'
            f'import styled from "styled-components";\n\n'
            f'// {prompt}\n'
            f'const Wrapper = styled.section`\n'
            f'  padding: 4rem 1.5rem;\n'
            f'  max-width: 1200px;\n'
            f'  margin: 0 auto;\n'
            f'`;\n\n'
            f'const {name}: React.FC = () => (\n'
            f'  <Wrapper>\n'
            f'    <h2>{name}</h2>\n'
            f'  </Wrapper>\n'
            f');\n\n'
            f'export default {name};\n'
        )

    def _css_modules(self, name: str) -> str:
        cls = name.lower()
        return (
            f'.{cls} {{\n'
            f'  padding: 4rem 1.5rem;\n'
            f'  max-width: 1200px;\n'
            f'  margin: 0 auto;\n'
            f'}}\n\n'
            f'.{cls}Title {{\n'
            f'  font-size: 2rem;\n'
            f'  font-weight: 700;\n'
            f'}}\n'
        )

    def _scaffold_files(self, fw: Framework, project_name: str) -> List[str]:
        base_map: dict = {
            Framework.REACT: [
                "src/App.jsx", "src/index.jsx", "public/index.html",
                "package.json", "README.md",
            ],
            Framework.REACT_TS: [
                "src/App.tsx", "src/index.tsx", "public/index.html",
                "package.json", "tsconfig.json", "README.md",
            ],
            Framework.VUE: [
                "src/App.vue", "src/main.js", "public/index.html",
                "package.json", "README.md",
            ],
            Framework.NEXTJS: [
                "app/page.tsx", "app/layout.tsx", "app/globals.css",
                "next.config.js", "package.json", "tsconfig.json",
            ],
            Framework.NUXT: ["app.vue", "nuxt.config.ts", "package.json"],
            Framework.SVELTE: [
                "src/App.svelte", "src/main.js", "package.json"
            ],
            Framework.SVELTEKIT: [
                "src/routes/+page.svelte", "src/app.html",
                "svelte.config.js", "package.json",
            ],
            Framework.ANGULAR: [
                "src/app/app.component.ts",
                "src/app/app.module.ts",
                "src/main.ts", "angular.json", "package.json",
            ],
            Framework.ASTRO: [
                "src/pages/index.astro", "astro.config.mjs", "package.json"
            ],
            Framework.REMIX: [
                "app/root.tsx", "app/routes/_index.tsx",
                "remix.config.js", "package.json",
            ],
        }
        return base_map.get(
            fw, ["index.html", "styles.css", "app.js", "README.md"]
        )

    def _scaffold_dirs(self, fw: Framework) -> List[str]:
        dirs_map: dict = {
            Framework.REACT: ["src/", "src/components/", "src/pages/", "public/"],
            Framework.NEXTJS: ["app/", "app/components/", "public/", "lib/"],
            Framework.VUE: ["src/", "src/components/", "src/views/", "public/"],
            Framework.SVELTE: ["src/", "src/lib/", "static/"],
            Framework.SVELTEKIT: [
                "src/", "src/routes/", "src/lib/", "static/"
            ],
            Framework.ANGULAR: [
                "src/", "src/app/", "src/assets/", "src/environments/"
            ],
        }
        return dirs_map.get(fw, ["src/", "public/", "assets/"])
