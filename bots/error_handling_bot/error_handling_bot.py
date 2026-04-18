"""
DreamCo Error Handling Bot — Beginner-Friendly Error Detection & Resolution.

Automatically detects, categorizes, and suggests fixes for common runtime
errors encountered by beginner bot developers. Every message is written in
plain English so that anyone — even on their first day — can understand what
went wrong and how to fix it.

Features
--------
* **Dynamic Error Detection** — inspects runtime exceptions and log text.
* **Error Categorization** — buckets errors into Syntax, Dependency,
  Environment, IO, and HTTP categories.
* **Fix Suggestions** — plain-English step-by-step remediation advice.
* **Learning Mode** — optional mini-tutorial attached to every error record
  that explains *why* the error happened and what concept to study.
* **Sandbox Simulation** — ``simulate_bot_run()`` replays a catalogue of
  common errors against a dummy bot so the whole pipeline can be exercised
  without a live system.

Usage example::

    bot = ErrorHandlingBot(learning_mode=True)
    bot.start()

    try:
        risky_operation()
    except Exception as exc:
        record = bot.capture_exception(exc, context="risky_operation")
        print(record.user_message)
        if record.tutorial:
            print(record.tutorial)

    report = bot.get_report()
    print(report)

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import re
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# GlobalAISourcesFlow is imported for framework compliance registration
# (required by all DreamCo bots — see tools/check_bot_framework.py).
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Error categories — simple buckets beginners can understand immediately
# ---------------------------------------------------------------------------

class ErrorCategory(str, Enum):
    """Top-level category buckets for all errors handled by this bot."""
    SYNTAX = "Syntax"
    DEPENDENCY = "Dependency"
    ENVIRONMENT = "Environment"
    IO = "IO"
    HTTP = "HTTP"
    UNKNOWN = "Unknown"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FixSuggestion:
    """A single remediation suggestion written for beginners."""
    step: int
    instruction: str
    command: Optional[str] = None  # shell command the user can copy-paste

    def __str__(self) -> str:
        line = f"  Step {self.step}: {self.instruction}"
        if self.command:
            line += f"\n    ▶  {self.command}"
        return line


@dataclass
class ErrorRecord:
    """Full structured record for a single captured error."""
    error_id: str
    category: ErrorCategory
    error_type: str
    raw_message: str
    user_message: str
    suggestions: List[FixSuggestion]
    context: str = ""
    traceback_text: str = ""
    tutorial: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def summary(self) -> str:
        """Return a compact one-line summary."""
        return (
            f"[{self.category.value}] {self.error_type}: {self.raw_message[:80]}"
        )

    def full_report(self) -> str:
        """Return the complete beginner-friendly report as a multi-line string."""
        lines = [
            "=" * 60,
            f"🚨  ERROR DETECTED  [{self.category.value.upper()}]",
            "=" * 60,
            f"What happened:  {self.user_message}",
            f"Error type:     {self.error_type}",
            f"Detected at:    {self.timestamp}",
        ]
        if self.context:
            lines.append(f"Location:       {self.context}")
        lines += [
            "",
            "🔧  How to fix it:",
        ]
        for suggestion in self.suggestions:
            lines.append(str(suggestion))
        if self.tutorial:
            lines += ["", "📚  Learn more:", self.tutorial]
        if self.traceback_text:
            lines += [
                "",
                "🔍  Technical details (for advanced users):",
                self.traceback_text,
            ]
        lines.append("=" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Categorization rules — pattern → (category, user_message, suggestions,
#                                   tutorial)
# ---------------------------------------------------------------------------

_SYNTAX_TUTORIAL = (
    "📖  SYNTAX ERRORS happen when Python cannot understand your code because\n"
    "    it does not follow the rules of the language.  Think of it like a\n"
    "    grammar mistake in a sentence.  Check the line number shown above,\n"
    "    look for missing colons (:), wrong indentation, unclosed brackets,\n"
    "    or misspelled keywords.  Resources:\n"
    "    • https://docs.python.org/3/reference/index.html\n"
    "    • https://realpython.com/invalid-syntax-python/"
)

_DEPENDENCY_TUTORIAL = (
    "📖  DEPENDENCY ERRORS mean a library your code needs is not installed.\n"
    "    Python packages are installed with the 'pip' tool.  Run the command\n"
    "    shown above in your terminal and then try again.  To avoid this in\n"
    "    future, add the package name to requirements.txt.  Resources:\n"
    "    • https://pip.pypa.io/en/stable/user_guide/\n"
    "    • https://realpython.com/what-is-pip/"
)

_ENVIRONMENT_TUTORIAL = (
    "📖  ENVIRONMENT ERRORS occur when the program cannot find a setting it\n"
    "    needs — like an API key or a file path stored as an environment\n"
    "    variable.  Create a '.env' file in the project root and add the\n"
    "    missing variable there (e.g. MY_KEY=abc123).  Never commit secrets\n"
    "    to Git!  Resources:\n"
    "    • https://12factor.net/config\n"
    "    • https://pypi.org/project/python-dotenv/"
)

_IO_TUTORIAL = (
    "📖  IO ERRORS happen when the program tries to open, read, or write a\n"
    "    file that does not exist or cannot be accessed.  Double-check the\n"
    "    file path (is the spelling correct?  Is it relative or absolute?).\n"
    "    Make sure the file exists and that you have permission to read it.\n"
    "    Resources:\n"
    "    • https://docs.python.org/3/tutorial/inputoutput.html\n"
    "    • https://realpython.com/read-write-files-python/"
)

_HTTP_TUTORIAL = (
    "📖  HTTP ERRORS come from web requests that did not succeed.  The\n"
    "    status code tells you what went wrong:\n"
    "    • 400  — you sent bad data (check your request body)\n"
    "    • 401  — you are not authenticated (check your API key)\n"
    "    • 403  — you do not have permission\n"
    "    • 404  — the URL does not exist\n"
    "    • 429  — too many requests (slow down / add a delay)\n"
    "    • 500  — the server crashed (try again later)\n"
    "    Resources:\n"
    "    • https://developer.mozilla.org/en-US/docs/Web/HTTP/Status\n"
    "    • https://realpython.com/python-requests/"
)

_UNKNOWN_TUTORIAL = (
    "📖  This error was not recognised automatically.  Here are general\n"
    "    debugging tips for beginners:\n"
    "    1. Read the error message carefully — it often tells you exactly\n"
    "       what is wrong and on which line.\n"
    "    2. Search the exact error message on Google or Stack Overflow.\n"
    "    3. Add print() statements before the failing line to inspect values.\n"
    "    4. Ask a friend or post in a beginner-friendly community like\n"
    "       https://www.reddit.com/r/learnpython/."
)


@dataclass
class _Rule:
    pattern: re.Pattern
    category: ErrorCategory
    user_message_template: str  # may contain {match} placeholder
    suggestions: List[FixSuggestion]
    tutorial: str


_RULES: List[_Rule] = [
    # ------------------------------------------------------------------
    # Syntax errors
    # ------------------------------------------------------------------
    _Rule(
        pattern=re.compile(r"SyntaxError|IndentationError|TabError", re.IGNORECASE),
        category=ErrorCategory.SYNTAX,
        user_message_template=(
            "Your code has a syntax mistake — Python cannot read it as-is. "
            "Look at the line number in the technical details below and fix the "
            "formatting (missing colon, wrong indentation, etc.)."
        ),
        suggestions=[
            FixSuggestion(1, "Open the file mentioned in the error message."),
            FixSuggestion(2, "Go to the line number shown in the error."),
            FixSuggestion(
                3,
                "Check for: missing colons after 'if'/'def'/'for', mismatched "
                "brackets (), [], or {}, and consistent 4-space indentation.",
            ),
            FixSuggestion(
                4,
                "Run the linter to auto-detect issues.",
                "flake8 your_file.py --max-line-length=120",
            ),
        ],
        tutorial=_SYNTAX_TUTORIAL,
    ),
    # ------------------------------------------------------------------
    # Dependency / import errors
    # ------------------------------------------------------------------
    _Rule(
        pattern=re.compile(
            r"ModuleNotFoundError|ImportError|No module named", re.IGNORECASE
        ),
        category=ErrorCategory.DEPENDENCY,
        user_message_template=(
            "A required Python package is missing. You need to install it "
            "before the bot can run."
        ),
        suggestions=[
            FixSuggestion(
                1,
                "Install the missing package using pip.",
                "pip install <package-name>",
            ),
            FixSuggestion(
                2,
                "If you see a requirements.txt file, install everything at once.",
                "pip install -r requirements.txt",
            ),
            FixSuggestion(
                3,
                "Add the package to requirements.txt so teammates can install "
                "it too.",
            ),
            FixSuggestion(
                4,
                "Restart your terminal / IDE after installing.",
            ),
        ],
        tutorial=_DEPENDENCY_TUTORIAL,
    ),
    # ------------------------------------------------------------------
    # Environment / config errors
    # ------------------------------------------------------------------
    _Rule(
        pattern=re.compile(
            r"KeyError|EnvironmentError|FileNotFoundError.*\.env|"
            r"Missing.*environment.*variable|MISSING_ENV",
            re.IGNORECASE,
        ),
        category=ErrorCategory.ENVIRONMENT,
        user_message_template=(
            "A required configuration setting (like an API key or file path) "
            "is missing from your environment."
        ),
        suggestions=[
            FixSuggestion(
                1,
                "Create a '.env' file in the root folder of the project if one "
                "does not exist.",
                "touch .env",
            ),
            FixSuggestion(
                2,
                "Add the missing variable to .env, for example: "
                "MY_API_KEY=your_value_here",
            ),
            FixSuggestion(
                3,
                "Load the .env file in your code using python-dotenv.",
                "pip install python-dotenv",
            ),
            FixSuggestion(
                4,
                "Never commit .env to Git — add it to .gitignore.",
                'echo ".env" >> .gitignore',
            ),
        ],
        tutorial=_ENVIRONMENT_TUTORIAL,
    ),
    # ------------------------------------------------------------------
    # IO / file errors
    # ------------------------------------------------------------------
    _Rule(
        pattern=re.compile(
            r"FileNotFoundError|PermissionError|IOError|OSError|"
            r"No such file or directory",
            re.IGNORECASE,
        ),
        category=ErrorCategory.IO,
        user_message_template=(
            "The program tried to open or write a file, but either it does not "
            "exist or there is a permissions problem."
        ),
        suggestions=[
            FixSuggestion(
                1,
                "Check that the file path in the error message is spelled "
                "correctly (including uppercase/lowercase letters).",
            ),
            FixSuggestion(
                2,
                "Make sure the file actually exists at that path.",
                "ls -la path/to/your/file",
            ),
            FixSuggestion(
                3,
                "If it is a permission error, try fixing file permissions.",
                "chmod 644 path/to/your/file",
            ),
            FixSuggestion(
                4,
                "If your code creates the file, make sure the parent directory "
                "exists first.",
                "mkdir -p path/to/directory",
            ),
        ],
        tutorial=_IO_TUTORIAL,
    ),
    # ------------------------------------------------------------------
    # HTTP / network errors
    # ------------------------------------------------------------------
    _Rule(
        pattern=re.compile(
            r"HTTPError|ConnectionError|Timeout|requests\.exceptions|"
            r"status.?code.?\b(4\d\d|5\d\d)\b|urllib\.error",
            re.IGNORECASE,
        ),
        category=ErrorCategory.HTTP,
        user_message_template=(
            "A web request failed. This could be a bad URL, missing API key, "
            "rate limit, or the remote server being down."
        ),
        suggestions=[
            FixSuggestion(
                1,
                "Check that the URL in your code is correct and starts with "
                "'https://'.",
            ),
            FixSuggestion(
                2,
                "Verify your API key or access token is set and not expired.",
            ),
            FixSuggestion(
                3,
                "If you got a 429 (Too Many Requests) error, add a short delay "
                "between calls.",
                "import time; time.sleep(1)",
            ),
            FixSuggestion(
                4,
                "If the error is a 5xx (server error), try again later — the "
                "remote server is having trouble.",
            ),
        ],
        tutorial=_HTTP_TUTORIAL,
    ),
]


# ---------------------------------------------------------------------------
# Main bot
# ---------------------------------------------------------------------------

class ErrorHandlingBot:
    """Beginner-friendly error detection, categorization, and fix-suggestion bot.

    Parameters
    ----------
    learning_mode:
        When ``True`` (default), every :class:`ErrorRecord` includes a
        mini-tutorial explaining *why* the error occurred and where to learn
        more.  Set to ``False`` in production for more compact output.
    log_dir:
        Directory where error logs are persisted.  Created automatically.
    """

    def __init__(
        self,
        learning_mode: bool = True,
        log_dir: str = "logs/error-handling-bot",
    ) -> None:
        self.learning_mode = learning_mode
        self._log_dir = log_dir
        self._records: List[ErrorRecord] = []
        self._running = False
        self._counter = 0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the bot (sets running flag, creates log directory)."""
        self._running = True
        os.makedirs(self._log_dir, exist_ok=True)

    def stop(self) -> None:
        """Stop the bot."""
        self._running = False

    @property
    def is_running(self) -> bool:
        """Return True when the bot is active."""
        return self._running

    # ------------------------------------------------------------------
    # Core detection
    # ------------------------------------------------------------------

    def categorize(self, error_text: str) -> ErrorCategory:
        """Return the :class:`ErrorCategory` that best matches *error_text*.

        Patterns are checked in priority order; the first match wins.
        Returns ``ErrorCategory.UNKNOWN`` when no pattern matches.
        """
        for rule in _RULES:
            if rule.pattern.search(error_text):
                return rule.category
        return ErrorCategory.UNKNOWN

    def capture_exception(
        self,
        exc: BaseException,
        context: str = "",
    ) -> ErrorRecord:
        """Convert a live Python exception into a structured :class:`ErrorRecord`.

        Parameters
        ----------
        exc:
            The exception instance to capture.
        context:
            Optional string describing where the error occurred (e.g. function
            name, file name).

        Returns
        -------
        ErrorRecord
            Fully populated record with user-friendly message and suggestions.
        """
        raw_message = str(exc)
        error_type = type(exc).__name__
        tb_text = traceback.format_exc()
        # Combine type name + message for pattern matching
        combined = f"{error_type}: {raw_message}\n{tb_text}"
        return self._build_record(combined, raw_message, error_type, context, tb_text)

    def capture_log(
        self,
        log_text: str,
        context: str = "",
    ) -> ErrorRecord:
        """Parse raw log text (e.g. from a CI run) and return an ErrorRecord.

        Parameters
        ----------
        log_text:
            Raw multi-line log string that may contain error indicators.
        context:
            Optional description of the log source.

        Returns
        -------
        ErrorRecord
        """
        # Try to extract a meaningful short message from the log
        short_message = self._extract_short_message(log_text)
        error_type = self._extract_error_type(log_text)
        return self._build_record(log_text, short_message, error_type, context, "")

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_records(self) -> List[ErrorRecord]:
        """Return all captured error records (newest first)."""
        return list(reversed(self._records))

    def get_report(self) -> str:
        """Return a full beginner-friendly report for all captured errors."""
        if not self._records:
            return "✅  No errors detected! Everything looks good."
        lines = [
            "=" * 60,
            f"📋  ERROR HANDLING BOT — FULL REPORT",
            f"    Total errors captured: {len(self._records)}",
            f"    Learning mode: {'ON' if self.learning_mode else 'OFF'}",
            "=" * 60,
        ]
        for record in reversed(self._records):
            lines.append(record.full_report())
        return "\n".join(lines)

    def get_summary(self) -> Dict[str, int]:
        """Return a count of errors by category."""
        summary: Dict[str, int] = {cat.value: 0 for cat in ErrorCategory}
        for record in self._records:
            summary[record.category.value] += 1
        return summary

    def clear(self) -> None:
        """Clear all captured records (useful between test runs)."""
        self._records.clear()

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def log_record(self, record: ErrorRecord) -> str:
        """Append *record* to the on-disk log and return the log file path."""
        os.makedirs(self._log_dir, exist_ok=True)
        log_path = os.path.join(self._log_dir, "errors.log")
        entry = (
            f"{record.timestamp} | {record.category.value} | "
            f"{record.error_type} | {record.raw_message[:120]}\n"
        )
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(entry)
        return log_path

    # ------------------------------------------------------------------
    # Sandbox simulation
    # ------------------------------------------------------------------

    def simulate_bot_run(self) -> List[ErrorRecord]:
        """Replay a catalogue of common errors and return the captured records.

        This is useful for demonstrating the system or running CI smoke tests
        without needing a live bot that actually fails.
        """
        self.start()
        self.clear()

        simulated_errors = [
            (SyntaxError("invalid syntax (<string>, line 5)"), "demo_bot.run()"),
            (
                ModuleNotFoundError("No module named 'openai'"),
                "ai_chatbot.load_model()",
            ),
            (
                FileNotFoundError("No such file or directory: 'config.json'"),
                "settings.load()",
            ),
            (
                EnvironmentError("Missing environment variable: STRIPE_API_KEY"),
                "payment_bot.charge()",
            ),
            (
                ConnectionError(
                    "HTTPError: 429 Too Many Requests — requests.exceptions.HTTPError"
                ),
                "api_client.fetch_data()",
            ),
        ]

        for exc, ctx in simulated_errors:
            record = self.capture_exception(exc, context=ctx)
            self.log_record(record)

        return self.get_records()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _next_id(self) -> str:
        self._counter += 1
        return f"ERR-{self._counter:04d}"

    def _build_record(
        self,
        full_text: str,
        raw_message: str,
        error_type: str,
        context: str,
        tb_text: str,
    ) -> ErrorRecord:
        category = self.categorize(full_text)
        rule = self._find_rule(category)

        if rule:
            user_message = rule.user_message_template
            suggestions = list(rule.suggestions)
            tutorial = rule.tutorial if self.learning_mode else ""
        else:
            user_message = (
                "An unexpected error occurred. The technical details are below. "
                "If you are stuck, try searching for the error type on Google "
                "or Stack Overflow — you are not alone!"
            )
            suggestions = [
                FixSuggestion(1, "Read the error message below carefully."),
                FixSuggestion(2, "Search the error type and message online."),
                FixSuggestion(
                    3,
                    "Add print() statements before the failing line to "
                    "inspect variable values.",
                ),
            ]
            tutorial = _UNKNOWN_TUTORIAL if self.learning_mode else ""

        record = ErrorRecord(
            error_id=self._next_id(),
            category=category,
            error_type=error_type,
            raw_message=raw_message,
            user_message=user_message,
            suggestions=suggestions,
            context=context,
            traceback_text=tb_text,
            tutorial=tutorial,
        )
        self._records.append(record)
        return record

    @staticmethod
    def _find_rule(category: ErrorCategory) -> Optional[_Rule]:
        for rule in _RULES:
            if rule.category == category:
                return rule
        return None

    @staticmethod
    def _extract_short_message(log_text: str) -> str:
        """Pull the first non-empty line that looks like an error message."""
        for line in log_text.splitlines():
            line = line.strip()
            if line and any(
                kw in line
                for kw in ("Error", "error", "Exception", "FAILED", "fatal", "Fatal")
            ):
                return line[:200]
        return log_text[:200]

    @staticmethod
    def _extract_error_type(log_text: str) -> str:
        """Attempt to extract the Python exception class name from log text."""
        match = re.search(r"(\w+(?:Error|Exception|Warning))", log_text)
        if match:
            return match.group(1)
        return "UnknownError"


# Backwards-compatible alias used by the test harness and control center.
Bot = ErrorHandlingBot
