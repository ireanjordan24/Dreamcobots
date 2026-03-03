"""Base class for all DreamCobots bots."""
from datetime import datetime


class BaseBot:
    """Base class for all Dreamcobots bots.

    Provides crash protection, resource monitoring hooks, revenue tracking,
    compliance package management, and training data collection.
    """

    def __init__(self, name: str, description: str = "", version: str = "1.0.0"):
        """Initialize the bot with a name, description, and version string."""
        self.name = name
        self.description = description
        self.version = version
        self.running = False
        self.priority = "medium"
        self.revenue = 0.0
        self.session_revenue = 0.0
        self._status = "stopped"
        self._log = []
        self._compliance_packages = []
        self._training_data = []
        self._improvement_suggestions = []

    def start(self):
        """Start the bot and set its status to running."""
        self.running = True
        self._status = "running"
        self.session_revenue = 0.0
        self.log(f"{self.name} started")

    def stop(self):
        """Stop the bot and set its status to stopped."""
        self.running = False
        self._status = "stopped"
        self.log(f"{self.name} stopped")

    def run(self):
        """Override in subclasses to implement bot-specific logic."""
        raise NotImplementedError(f"{self.name}.run() must be implemented by subclass")

    def train(self, data):
        """Add training data to improve bot responses."""
        if isinstance(data, dict):
            self._training_data.append(data)
        elif isinstance(data, list):
            self._training_data.extend(data)
        else:
            self._training_data.append({"data": str(data)})
        self.log(f"Training data added ({len(self._training_data)} total records)")

    def get_status(self) -> dict:
        """Return a status dictionary with bot health and revenue information."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "status": self._status,
            "running": self.running,
            "priority": self.priority,
            "revenue": self.revenue,
            "session_revenue": self.session_revenue,
            "training_records": len(self._training_data),
            "log_entries": len(self._log),
            "compliance_packages": len(self._compliance_packages),
            "improvement_suggestions": len(self._improvement_suggestions),
        }

    def log(self, message: str):
        """Append a timestamped message to the bot's internal log."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "bot": self.name,
            "message": message,
        }
        self._log.append(entry)
        if len(self._log) > 1000:
            self._log = self._log[-1000:]

    def add_revenue(self, amount: float):
        """Record revenue earned by this bot."""
        if amount > 0:
            self.revenue += amount
            self.session_revenue += amount
            self.log(f"Revenue added: ${amount:.2f} (total: ${self.revenue:.2f})")

    def suggest_improvements(self) -> list:
        """Return a list of improvement suggestions for this bot."""
        base_suggestions = [
            f"Integrate real-time data APIs for {self.name}",
            f"Add machine learning model to improve {self.name} accuracy",
            f"Implement webhook notifications for {self.name} events",
            f"Add multi-language support to {self.name}",
            f"Build dedicated mobile interface for {self.name}",
        ]
        return base_suggestions + self._improvement_suggestions

    def get_compliance(self) -> list:
        """Return list of compliance packages associated with this bot."""
        return list(self._compliance_packages)

    def throttle(self):
        """Reduce bot activity when system resources are constrained."""
        self.log(f"{self.name} throttled due to resource pressure")

    def _safe_run(self, func, *args, **kwargs):
        """Execute a function with exception handling, returning None on failure."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self._status = "error"
            self.log(f"Error in {self.name}: {e}")
            return None
