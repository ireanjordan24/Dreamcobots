"""
BuddyBot - The main Buddy SaaS bot entry point.

Buddy understands and executes user commands dynamically—via text or
voice—eliminating the need for specialized apps.  It integrates:

  • Text-to-task parsing         (TextHandler)
  • Speech-to-task recognition   (SpeechHandler)
  • Dynamic library management   (LibraryManager)
  • Modular task execution       (TaskEngine + plugins)
  • Lightweight task scheduling  (Scheduler)
  • Performance benchmarking     (Benchmarks)
  • Event-driven architecture    (EventBus)
"""

import logging
import sys
from typing import Any, Dict, Optional

from BuddyAI.benchmarks import Benchmarks
from BuddyAI.event_bus import EventBus
from BuddyAI.library_manager import LibraryManager
from BuddyAI.scheduler import Scheduler
from BuddyAI.speech_handler import SpeechHandler
from BuddyAI.task_engine import TaskEngine
from BuddyAI.text_handler import TextHandler

logger = logging.getLogger(__name__)


class BuddyBot:
    """The central Buddy SaaS bot.

    Usage::

        buddy = BuddyBot()
        buddy.start()

        # Text command
        response = buddy.chat("Add todo buy milk")
        print(response["message"])

        # Voice command (requires microphone + SpeechRecognition)
        response = buddy.listen_and_respond()
        print(response["message"])

        buddy.stop()
    """

    def __init__(
        self,
        *,
        enable_scheduler: bool = True,
        log_level: int = logging.INFO,
    ) -> None:
        """
        Args:
            enable_scheduler: Whether to start the background task scheduler.
            log_level: Logging level (default ``logging.INFO``).
        """
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            stream=sys.stdout,
        )

        self.event_bus = EventBus()
        self.library_manager = LibraryManager()
        self.scheduler = Scheduler() if enable_scheduler else None
        self.task_engine = TaskEngine()
        self.text_handler = TextHandler()
        self.speech_handler = SpeechHandler()
        self.benchmarks = Benchmarks()

        self._running = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Initialize all subsystems and load built-in plugins."""
        if self._running:
            logger.warning("BuddyBot is already running.")
            return

        logger.info("Starting BuddyBot…")
        self._load_plugins()

        if self.scheduler is not None:
            self.scheduler.start()

        self._running = True
        self.event_bus.publish("buddy.started", {"version": "0.1.0"})
        logger.info("BuddyBot is ready.  Say or type a command.")

    def stop(self) -> None:
        """Gracefully shut down all subsystems."""
        if not self._running:
            return
        logger.info("Stopping BuddyBot…")
        if self.scheduler is not None:
            self.scheduler.stop()
        self._running = False
        self.event_bus.publish("buddy.stopped", {})
        logger.info("BuddyBot stopped.")

    # ------------------------------------------------------------------
    # Main interaction API
    # ------------------------------------------------------------------

    def chat(self, text: str) -> Dict[str, Any]:
        """Process a text command and return the response dict.

        Args:
            text: Free-form user command string.

        Returns:
            Dict with at least a ``"message"`` key and a ``"success"`` bool.
        """
        self.event_bus.publish("buddy.input.text", {"text": text})
        result = self.task_engine.process_text(text)
        self.event_bus.publish("buddy.output", result)
        return result

    def listen_and_respond(self) -> Dict[str, Any]:
        """Capture a voice command from the microphone and respond.

        Returns:
            Response dict (same structure as :meth:`chat`).
        """
        self.event_bus.publish("buddy.input.voice.start", {})
        try:
            text = self.speech_handler.listen()
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Voice capture failed: %s", exc)
            return {
                "success": False,
                "message": f"Voice capture failed: {exc}",
            }

        if not text:
            return {
                "success": False,
                "message": "I didn't catch that.  Could you repeat?",
            }

        self.event_bus.publish("buddy.input.voice.transcribed", {"text": text})
        logger.info("Transcribed voice command: %r", text)
        return self.chat(text)

    def install_capability(self, package: str) -> Dict[str, Any]:
        """Dynamically install a Python package to extend Buddy's capabilities.

        Args:
            package: PyPI package name to install.

        Returns:
            Status dict with ``"success"`` and ``"message"``.
        """
        try:
            self.library_manager.install_library(package)
            ok = self.library_manager.test_library(package)
            if ok:
                self.event_bus.publish("buddy.library.installed", {"package": package})
                return {
                    "success": True,
                    "message": f"Package '{package}' installed and verified.",
                }
            return {
                "success": False,
                "message": f"Package '{package}' installed but failed smoke-test.",
            }
        except Exception as exc:  # pylint: disable=broad-except
            return {"success": False, "message": str(exc)}

    def benchmark_task(
        self, text: str, iterations: int = 5
    ) -> Dict[str, Any]:
        """Benchmark how fast Buddy executes a given text command.

        Args:
            text: Command to benchmark.
            iterations: Number of executions.

        Returns:
            Dict with benchmark statistics and the last response.
        """
        result = self.benchmarks.benchmark(
            self.chat, text, iterations=iterations, name=f"chat({text!r})"
        )
        return {
            "success": True,
            "message": result.summary(),
            "benchmark": {
                "mean_ms": round(result.mean * 1000, 3),
                "median_ms": round(result.median * 1000, 3),
                "min_ms": round(result.min_time * 1000, 3),
                "max_ms": round(result.max_time * 1000, 3),
                "iterations": result.iterations,
            },
        }

    # ------------------------------------------------------------------
    # Plugin loading
    # ------------------------------------------------------------------

    def _load_plugins(self) -> None:
        """Load all built-in plugins and register their capabilities."""
        from BuddyAI.plugins import productivity, data_entry, api_integrator

        productivity.register(self.task_engine, scheduler=self.scheduler)
        data_entry.register(self.task_engine)
        api_integrator.register(self.task_engine)

        # Register the install_library capability via the task engine
        self.task_engine.register_capability(
            "install_library", self._handle_install_library
        )
        # Register benchmark capability
        self.task_engine.register_capability(
            "benchmark", self._handle_benchmark
        )
        # Register search via api (web search placeholder)
        self.task_engine.register_capability(
            "search", self._handle_search
        )

        logger.info(
            "Plugins loaded. Available capabilities: %s",
            self.task_engine.list_capabilities(),
        )

    def _handle_install_library(self, params: Dict[str, Any]) -> Dict[str, Any]:
        package = params.get("package", "").strip()
        if not package:
            return {"success": False, "message": "No package name provided."}
        return self.install_capability(package)

    def _handle_benchmark(self, params: Dict[str, Any]) -> Dict[str, Any]:
        target = params.get("target", "").strip()
        return self.benchmark_task(target) if target else {
            "success": False,
            "message": "No benchmark target provided.",
        }

    def _handle_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = params.get("query", "").strip()
        if not query:
            return {"success": False, "message": "No search query provided."}
        # Build a DuckDuckGo Instant Answer API call
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
        from BuddyAI.plugins.api_integrator import handle_fetch_api
        result = handle_fetch_api({"url": url})
        if result.get("success") and isinstance(result.get("data"), dict):
            abstract = result["data"].get("AbstractText", "")
            answer = result["data"].get("Answer", "")
            response_text = abstract or answer or "No instant answer found."
            return {"success": True, "message": response_text, "raw": result["data"]}
        return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Interactive CLI for Buddy."""
    buddy = BuddyBot()
    buddy.start()

    print("\n=== Buddy SaaS Bot ===")
    print("Type a command or 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if user_input.lower() in {"quit", "exit", "bye"}:
            print("Buddy: Goodbye!")
            break

        if not user_input:
            continue

        response = buddy.chat(user_input)
        print(f"Buddy: {response.get('message', response)}\n")

    buddy.stop()


if __name__ == "__main__":
    main()
