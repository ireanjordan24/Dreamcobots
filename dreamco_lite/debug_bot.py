"""
DreamCo Lite — Debug Bot 🔧

Reads raw log/error text, explains errors in plain English, and suggests
concrete fixes.

Modes
-----
SIMULATION_MODE=true  (default, no API keys required)
    Returns a structured explanation generated from simple pattern matching so
    the end-to-end workflow can be exercised without OpenAI credentials.

SIMULATION_MODE=false
    Requires OPENAI_API_KEY.  Sends the log to GPT for a richer analysis.
"""

from __future__ import annotations

import os
import re
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_SIMULATION = os.getenv("SIMULATION_MODE", "true").lower() != "false"
_OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

# ---------------------------------------------------------------------------
# Pattern-based analysis used in simulation mode
# ---------------------------------------------------------------------------

_PATTERNS: list[tuple[re.Pattern[str], str, list[str]]] = [
    (
        re.compile(r"ImportError|ModuleNotFoundError", re.I),
        "A required Python module could not be found.",
        [
            "Run `pip install <missing-module>` to install the missing package.",
            "Check that your virtual environment is activated.",
            "Verify the module name is spelled correctly in your import statement.",
        ],
    ),
    (
        re.compile(r"KeyError", re.I),
        "The code tried to access a dictionary key that does not exist.",
        [
            "Use `.get('key', default)` instead of `dict['key']` to avoid the error.",
            "Print the dictionary contents before the failing line to see what keys are available.",
            "Add a check: `if 'key' in my_dict:` before accessing it.",
        ],
    ),
    (
        re.compile(r"AttributeError", re.I),
        "An object does not have the attribute or method being called.",
        [
            "Check that the variable is the type you expect (e.g., not None).",
            "Use `dir(obj)` or `type(obj)` to inspect what's available.",
            "Verify you're importing the correct class or module.",
        ],
    ),
    (
        re.compile(r"TypeError", re.I),
        "An operation was applied to the wrong type of value.",
        [
            "Check the types of all arguments passed to the failing function.",
            "Use `isinstance()` guards to validate types before operations.",
            "Review function signatures to confirm expected argument types.",
        ],
    ),
    (
        re.compile(r"ValueError", re.I),
        "A function received an argument with the right type but an invalid value.",
        [
            "Validate all inputs before passing them to the function.",
            "Add bounds checking or enum validation where appropriate.",
            "Inspect the traceback to identify which value was rejected.",
        ],
    ),
    (
        re.compile(r"FileNotFoundError|No such file", re.I),
        "The program tried to open a file that does not exist at the specified path.",
        [
            "Verify the file path is correct (absolute vs relative).",
            "Check that the file has been created before this code runs.",
            "Use `os.path.exists(path)` to guard file access.",
        ],
    ),
    (
        re.compile(r"ConnectionError|ConnectionRefused|ECONNREFUSED", re.I),
        "The application could not connect to a remote host or service.",
        [
            "Confirm the target service (database, API, Redis, etc.) is running.",
            "Check that the host and port in your configuration are correct.",
            "Review firewall rules or network settings that might be blocking the connection.",
        ],
    ),
    (
        re.compile(r"TimeoutError|ReadTimeout|ConnectTimeout", re.I),
        "A network operation took longer than the allowed time limit.",
        [
            "Increase the timeout value in your HTTP client or SDK configuration.",
            "Check the health of the downstream service you are connecting to.",
            "Add retry logic with exponential back-off for transient timeouts.",
        ],
    ),
    (
        re.compile(r"SyntaxError", re.I),
        "Python could not parse your code due to a syntax mistake.",
        [
            "Read the traceback carefully — it points to the exact line with the issue.",
            "Look for missing colons, mismatched brackets, or incorrect indentation.",
            "Use a linter (e.g., flake8 or ruff) to catch syntax errors automatically.",
        ],
    ),
    (
        re.compile(r"IndentationError", re.I),
        "Python detected inconsistent indentation in the source file.",
        [
            "Ensure you are using spaces consistently (PEP 8 recommends 4 spaces per level).",
            "Never mix tabs and spaces in the same file.",
            "Enable 'show whitespace' in your editor to spot invisible characters.",
        ],
    ),
    (
        re.compile(r"PermissionError|Permission denied", re.I),
        "The process does not have permission to access a file or resource.",
        [
            "Check file ownership and permissions with `ls -la`.",
            "Run the process as the correct user, or adjust file permissions with `chmod`.",
            "Avoid running application code as root unless absolutely necessary.",
        ],
    ),
    (
        re.compile(r"MemoryError|OOM|out of memory", re.I),
        "The process ran out of available memory.",
        [
            "Process large datasets in smaller chunks instead of loading everything at once.",
            "Profile memory usage with tools like `memory_profiler` or `tracemalloc`.",
            "Consider upgrading to a machine with more RAM or using streaming data pipelines.",
        ],
    ),
    (
        re.compile(r"ZeroDivisionError", re.I),
        "The code attempted to divide a number by zero.",
        [
            "Add a guard: `if denominator != 0:` before the division.",
            "Trace where the zero value originates and validate inputs upstream.",
        ],
    ),
    (
        re.compile(r"RecursionError|maximum recursion depth", re.I),
        "A function called itself too many times, exhausting Python's call stack.",
        [
            "Identify the base case in your recursive function and ensure it is always reachable.",
            "Consider refactoring to an iterative approach for deep recursions.",
            "Increase the limit with `sys.setrecursionlimit()` only as a last resort.",
        ],
    ),
    (
        re.compile(r"404|not found", re.I),
        "A requested resource (URL, file, or endpoint) could not be found.",
        [
            "Double-check the URL or file path for typos.",
            "Ensure the route or resource is registered and correctly mapped.",
            "Check server logs to see whether the request reached the application.",
        ],
    ),
    (
        re.compile(r"500|internal server error", re.I),
        "The server encountered an unexpected condition that prevented it from fulfilling the request.",  # noqa: E501
        [
            "Check the server error logs for the full traceback.",
            "Add try/except blocks around the failing handler to catch and log exceptions.",
            "Enable debug mode locally to get a detailed error page.",
        ],
    ),
    (
        re.compile(r"401|unauthorized|authentication", re.I),
        "The request was rejected because valid credentials were not provided.",
        [
            "Verify that your API key or token is set and has not expired.",
            "Confirm the Authorization header format matches what the API expects.",
            "Check that environment variables containing secrets are properly loaded.",
        ],
    ),
    (
        re.compile(r"403|forbidden", re.I),
        "The server understood the request but refused to authorise it.",
        [
            "Confirm the authenticated user or API key has the required permissions.",
            "Check CORS settings if this is a browser-based request.",
            "Review role-based access control (RBAC) rules on the server.",
        ],
    ),
]

_FALLBACK_EXPLANATION = "An unexpected error occurred in the application."
_FALLBACK_FIXES = [
    "Read the full traceback carefully to identify the failing line.",
    "Search for the error message online or in the library's documentation.",
    "Add logging around the failing code block to gather more context.",
    "Isolate the issue by writing a minimal reproducible example.",
]


def _pattern_analyze(log: str) -> dict[str, Any]:
    """Return a structured analysis using simple regex pattern matching."""
    matched_explanations: list[str] = []
    matched_fixes: list[str] = []

    for pattern, explanation, fixes in _PATTERNS:
        if pattern.search(log):
            matched_explanations.append(explanation)
            matched_fixes.extend(fixes)

    if not matched_explanations:
        return {
            "explanation": _FALLBACK_EXPLANATION,
            "fixes": _FALLBACK_FIXES,
            "source": "pattern_matching",
        }

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_fixes: list[str] = []
    for fix in matched_fixes:
        if fix not in seen:
            seen.add(fix)
            unique_fixes.append(fix)

    return {
        "explanation": " ".join(matched_explanations),
        "fixes": unique_fixes[:6],
        "source": "pattern_matching",
    }


# ---------------------------------------------------------------------------
# OpenAI-powered analysis
# ---------------------------------------------------------------------------

def _openai_analyze(log: str) -> dict[str, Any]:
    """Analyse the log with OpenAI and return a structured result."""
    if not _OPENAI_KEY:
        logger.warning("OPENAI_API_KEY not set; falling back to pattern matching.")
        return _pattern_analyze(log)

    prompt = (
        "You are a senior software engineer and debugging expert. "
        "A user has pasted the following error log or stack trace:\n\n"
        f"```\n{log[:3000]}\n```\n\n"
        "Please respond with a JSON object containing exactly two keys:\n"
        "1. \"explanation\": a 2-3 sentence plain-English description of what went wrong.\n"
        "2. \"fixes\": a JSON array of 3-5 concrete, actionable fix suggestions.\n"
        "Return only valid JSON, no markdown fences."
    )

    try:
        resp = httpx.post(
            _OPENAI_CHAT_URL,
            headers={"Authorization": f"Bearer {_OPENAI_KEY}"},
            json={
                "model": _OPENAI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.3,
            },
            timeout=30,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        parsed = _parse_ai_json(content)
        parsed["source"] = "openai"
        return parsed
    except Exception as exc:
        logger.warning("OpenAI debug analysis failed: %s; falling back to pattern matching.", exc)
        return _pattern_analyze(log)


def _parse_ai_json(text: str) -> dict[str, Any]:
    """Parse JSON from AI response, with a fallback for imperfect output."""
    import json

    # Strip any accidental markdown code fences
    cleaned = re.sub(r"^```[a-z]*\n?|```$", "", text.strip(), flags=re.MULTILINE)
    try:
        data = json.loads(cleaned)
        if "explanation" in data and "fixes" in data:
            return {"explanation": str(data["explanation"]), "fixes": list(data["fixes"])}
    except Exception:
        pass

    return {
        "explanation": text[:500],
        "fixes": ["Review the full error message above for more context."],
    }


# ---------------------------------------------------------------------------
# DebugBot
# ---------------------------------------------------------------------------

class DebugBot:
    """
    🔧 DreamCo Lite Debug Bot.

    Usage::

        bot = DebugBot()
        result = bot.analyze("Traceback ... KeyError: 'api_key'")
        # result = {"explanation": "...", "fixes": [...], "source": "..."}
    """

    def analyze(self, log: str) -> dict[str, Any]:
        """
        Analyse *log* (error message, stack trace, or any log text).

        Returns a dict with:
          explanation : plain-English description of the error
          fixes       : list of actionable fix suggestions
          source      : "openai" | "pattern_matching"
        """
        if not log or not log.strip():
            return {
                "explanation": "No error log was provided.",
                "fixes": ["Paste a stack trace or error message to get started."],
                "source": "none",
            }

        if _SIMULATION or not _OPENAI_KEY:
            return _pattern_analyze(log)

        return _openai_analyze(log)
