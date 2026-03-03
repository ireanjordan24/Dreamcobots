"""BotBase: lifecycle management for all DreamCo bots."""
import logging
from abc import ABC, abstractmethod
from enum import Enum


class BotStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class BotBase(ABC):
    """Abstract base class providing lifecycle management for all bots."""

    def __init__(self, name: str):
        self.name = name
        self.status: BotStatus = BotStatus.IDLE
        self.logger = logging.getLogger(name)

    def start(self) -> None:
        """Transition the bot to RUNNING state and invoke on_start."""
        self.logger.info("[%s] Starting...", self.name)
        self.status = BotStatus.RUNNING
        self.on_start()

    def stop(self) -> None:
        """Transition the bot to STOPPED state and invoke on_stop."""
        self.logger.info("[%s] Stopping...", self.name)
        self.status = BotStatus.STOPPED
        self.on_stop()

    def run(self) -> None:
        """Full lifecycle: start -> execute -> stop with error handling."""
        self.start()
        try:
            self.execute()
        except Exception as exc:
            self.status = BotStatus.ERROR
            self.logger.error("[%s] Error during execution: %s", self.name, exc)
            raise
        finally:
            if self.status == BotStatus.RUNNING:
                self.stop()

    @abstractmethod
    def on_start(self) -> None:
        """Hook called after bot transitions to RUNNING."""

    @abstractmethod
    def on_stop(self) -> None:
        """Hook called after bot transitions to STOPPED."""

    @abstractmethod
    def execute(self) -> None:
        """Main bot logic."""
