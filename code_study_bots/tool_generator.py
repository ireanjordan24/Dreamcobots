"""
Tool Generator — builds usable tools from every capability a library exposes,
including hidden capabilities beyond documented knowledge.

For each library symbol (documented *and* hidden) the generator produces a
``GeneratedTool``: a self-contained, callable Python class with a ``run()``
method, metadata, and a stub implementation.  Tools are returned as both
Python source strings (for file-system storage) and importable objects.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .library_scraper import LibraryRecord


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class GeneratedTool:
    """A tool generated from a single library symbol."""
    tool_id: str                    # "<language>__<library>__<symbol>"
    library_name: str
    language: str
    symbol: str
    purpose_category: str
    description: str
    is_hidden_capability: bool      # True if derived from a private/hidden symbol
    source_code: str                # Python stub source
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: list[str] = field(default_factory=list)
    marketplace_ready: bool = False

    def to_dict(self) -> dict:
        return {
            "tool_id": self.tool_id,
            "library_name": self.library_name,
            "language": self.language,
            "symbol": self.symbol,
            "purpose_category": self.purpose_category,
            "description": self.description,
            "is_hidden_capability": self.is_hidden_capability,
            "version": self.version,
            "created_at": self.created_at,
            "tags": self.tags,
            "marketplace_ready": self.marketplace_ready,
        }


# ---------------------------------------------------------------------------
# Tool Generator
# ---------------------------------------------------------------------------

class ToolGenerator:
    """
    Generates usable tools from every capability a library exposes.

    Usage
    -----
        scraper = LibraryScraper()
        rec = scraper.get_library("python", "pandas")
        generator = ToolGenerator()
        tools = generator.generate_all(rec, include_hidden=True)
    """

    # Template for generating a tool class source string
    _CLASS_TEMPLATE = '''\
"""Auto-generated DreamCobots tool — {tool_id}

Library : {library_name} ({language})
Symbol  : {symbol}
Category: {purpose_category}
Hidden  : {is_hidden}
Generated: {created_at}
"""

from __future__ import annotations
from typing import Any


class {class_name}:
    """
    DreamCobots tool wrapping ``{library_name}.{symbol}``.

    {description}
    """

    TOOL_ID = "{tool_id}"
    LIBRARY = "{library_name}"
    LANGUAGE = "{language}"
    SYMBOL = "{symbol}"
    VERSION = "{version}"
    IS_HIDDEN_CAPABILITY = {is_hidden}

    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = kwargs
        self._result: Any = None

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the tool.

        In production, this method invokes ``{library_name}.{symbol}`` with
        the supplied arguments, handles exceptions, and returns structured
        output.  The stub below documents the expected interface.
        """
        merged = {{**self._kwargs, **kwargs}}
        # --- stub implementation ---
        self._result = {{
            "tool": self.TOOL_ID,
            "args": args,
            "kwargs": merged,
            "status": "ok",
            "output": f"[{library_name}.{symbol}] executed successfully.",
        }}
        return self._result

    def result(self) -> Any:
        """Return the last execution result."""
        return self._result

    def describe(self) -> dict:
        """Return tool metadata."""
        return {{
            "tool_id": self.TOOL_ID,
            "library": self.LIBRARY,
            "language": self.LANGUAGE,
            "symbol": self.SYMBOL,
            "version": self.VERSION,
            "is_hidden_capability": self.IS_HIDDEN_CAPABILITY,
        }}
'''

    def __init__(self) -> None:
        self._generated: dict[str, GeneratedTool] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_all(self, record: LibraryRecord, include_hidden: bool = False) -> list[GeneratedTool]:
        """
        Generate tools for every symbol in *record*.

        Parameters
        ----------
        record : LibraryRecord
            The library to process.
        include_hidden : bool
            When True, also generate tools for hidden/private symbols.

        Returns
        -------
        list[GeneratedTool]
        """
        tools: list[GeneratedTool] = []
        for symbol in record.exported_symbols:
            tool = self._make_tool(record, symbol, hidden=False)
            self._generated[tool.tool_id] = tool
            tools.append(tool)
        if include_hidden:
            for symbol in record.hidden_symbols:
                tool = self._make_tool(record, symbol, hidden=True)
                self._generated[tool.tool_id] = tool
                tools.append(tool)
        return tools

    def generate_for_symbol(self, record: LibraryRecord, symbol: str,
                            hidden: bool = False) -> GeneratedTool:
        """Generate a single tool for one library symbol."""
        tool = self._make_tool(record, symbol, hidden=hidden)
        self._generated[tool.tool_id] = tool
        return tool

    def get_tool(self, tool_id: str) -> Optional[GeneratedTool]:
        """Retrieve a previously generated tool by ID."""
        return self._generated.get(tool_id)

    def list_tools(self, language: Optional[str] = None,
                   library: Optional[str] = None,
                   hidden_only: bool = False) -> list[GeneratedTool]:
        """Return generated tools, with optional filters."""
        results = list(self._generated.values())
        if language:
            results = [t for t in results if t.language == language.lower()]
        if library:
            results = [t for t in results if t.library_name == library.lower()]
        if hidden_only:
            results = [t for t in results if t.is_hidden_capability]
        return results

    def tools_summary(self) -> dict:
        """Return a high-level summary of all generated tools."""
        tools = list(self._generated.values())
        by_language: dict[str, int] = {}
        hidden_count = 0
        marketplace_count = 0
        for t in tools:
            by_language[t.language] = by_language.get(t.language, 0) + 1
            if t.is_hidden_capability:
                hidden_count += 1
            if t.marketplace_ready:
                marketplace_count += 1
        return {
            "total_tools": len(tools),
            "by_language": by_language,
            "hidden_capability_tools": hidden_count,
            "marketplace_ready": marketplace_count,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_tool(self, record: LibraryRecord, symbol: str, hidden: bool) -> GeneratedTool:
        """Build a GeneratedTool from a library record and symbol name."""
        safe_symbol = re.sub(r"[^a-zA-Z0-9_]", "_", symbol)
        tool_id = f"{record.language}__{record.name}__{safe_symbol}"
        class_name = self._to_class_name(f"{record.name}_{safe_symbol}")
        description = (
            f"Wraps the {'hidden/private' if hidden else 'public'} symbol "
            f"``{symbol}`` from the ``{record.name}`` {record.language} library. "
            f"{record.description}"
        )
        source = self._CLASS_TEMPLATE.format(
            tool_id=tool_id,
            library_name=record.name,
            language=record.language,
            symbol=symbol,
            purpose_category=record.purpose_category,
            description=description,
            is_hidden=hidden,
            class_name=class_name,
            version="1.0.0",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return GeneratedTool(
            tool_id=tool_id,
            library_name=record.name,
            language=record.language,
            symbol=symbol,
            purpose_category=record.purpose_category,
            description=description,
            is_hidden_capability=hidden,
            source_code=source,
            version="1.0.0",
            tags=list(record.tags),
            marketplace_ready=not hidden,
        )

    @staticmethod
    def _to_class_name(slug: str) -> str:
        """Convert snake_case or dotted slug to PascalCase class name."""
        parts = re.split(r"[^a-zA-Z0-9]+", slug)
        return "".join(p.capitalize() for p in parts if p)
