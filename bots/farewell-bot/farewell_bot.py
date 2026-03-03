"""
bots/farewell-bot/farewell_bot.py

FarewellBot — offboarding, feedback collection, farewell messages, and data archival.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

_FAREWELL_TEMPLATES: dict[str, str] = {
    "retirement": (
        "Dear {name},\n\nOn behalf of the entire DreamCobots team, we congratulate you on your retirement "
        "and thank you for your outstanding contributions over the years. Your dedication and expertise "
        "have left a lasting impact on our organisation. We wish you all the best in this exciting new chapter.\n\n"
        "With warmest regards,\nThe DreamCobots Team"
    ),
    "resignation": (
        "Dear {name},\n\nThank you for your {tenure} with DreamCobots. We appreciate your "
        "contributions and wish you every success in your next endeavour. "
        "Please know that you are always welcome to stay in touch.\n\n"
        "Best wishes,\nThe DreamCobots Team"
    ),
    "termination": (
        "Dear {name},\n\nWe acknowledge the end of your employment with DreamCobots. "
        "We appreciate your service and wish you well in your future endeavours. "
        "Please ensure all company property and access credentials are returned promptly.\n\n"
        "Regards,\nHuman Resources"
    ),
    "contract_end": (
        "Dear {name},\n\nYour contract with DreamCobots has concluded. "
        "We thank you for your professional contributions during this engagement "
        "and hope to work with you again in the future.\n\n"
        "Kind regards,\nDreamCobots Partnerships"
    ),
}

_FEEDBACK_QUESTIONS: list[str] = [
    "How would you rate your overall experience at DreamCobots? (1-10)",
    "What aspects of your role did you find most fulfilling?",
    "What could DreamCobots improve for future employees?",
    "Would you recommend DreamCobots as a great place to work?",
    "Is there anything else you would like to share with leadership?",
]


class FarewellBot(BotBase):
    """
    Manages the offboarding lifecycle: farewell messages, feedback, and data archival.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="FarewellBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._offboarding_records: dict[str, dict[str, Any]] = {}
        self._feedback_records: dict[str, dict[str, Any]] = {}
        self._archived_data: dict[str, dict[str, Any]] = {}
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("FarewellBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("FarewellBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def initiate_offboarding(self, user_id: str) -> dict[str, Any]:
        """
        Initiate the offboarding process for *user_id*.

        Args:
            user_id: ID of the departing user.

        Returns:
            Offboarding checklist and process dict.
        """
        record_id = str(uuid.uuid4())
        checklist = [
            {"task": "Return company equipment", "status": "pending"},
            {"task": "Revoke system access", "status": "pending"},
            {"task": "Transfer knowledge and documentation", "status": "pending"},
            {"task": "Complete exit interview / feedback survey", "status": "pending"},
            {"task": "Process final paycheck and benefits", "status": "pending"},
            {"task": "Archive user data", "status": "pending"},
            {"task": "Send farewell message", "status": "pending"},
        ]
        record: dict[str, Any] = {
            "id": record_id,
            "user_id": user_id,
            "initiated_at": datetime.now(timezone.utc).isoformat(),
            "status": "in_progress",
            "checklist": checklist,
        }
        with self._lock_extra:
            self._offboarding_records[user_id] = record
        self.log_activity(f"Offboarding initiated for user '{user_id}'.")
        return dict(record)

    def collect_feedback(self, user_id: str) -> dict[str, Any]:
        """
        Record and return a feedback survey for *user_id*.

        Args:
            user_id: Departing user's ID.

        Returns:
            Feedback survey structure with questions.
        """
        survey: dict[str, Any] = {
            "user_id": user_id,
            "survey_id": str(uuid.uuid4()),
            "questions": _FEEDBACK_QUESTIONS,
            "responses": {},  # Filled in when user submits
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending_response",
        }
        with self._lock_extra:
            self._feedback_records[user_id] = survey
        self.log_activity(f"Feedback survey created for user '{user_id}'.")
        return dict(survey)

    def generate_farewell_message(self, user_id: str, reason: str) -> str:
        """
        Generate a personalised farewell message.

        Args:
            user_id: Departing user's ID.
            reason: Departure reason (``retirement``, ``resignation``,
                    ``termination``, ``contract_end``).

        Returns:
            Formatted farewell message string.
        """
        template = _FAREWELL_TEMPLATES.get(
            reason.lower().replace(" ", "_"),
            _FAREWELL_TEMPLATES["resignation"],
        )
        message = template.format(
            name=f"User {user_id}",
            tenure="time",
        )
        self.log_activity(f"Farewell message generated for user '{user_id}' (reason='{reason}').")
        return message

    def archive_user_data(self, user_id: str) -> bool:
        """
        Archive a user's data and mark them as offboarded.

        Args:
            user_id: User ID to archive.

        Returns:
            ``True`` if archival succeeded.
        """
        archive_id = str(uuid.uuid4())
        with self._lock_extra:
            offboarding = self._offboarding_records.get(user_id, {})
            feedback = self._feedback_records.get(user_id, {})
            self._archived_data[user_id] = {
                "archive_id": archive_id,
                "user_id": user_id,
                "archived_at": datetime.now(timezone.utc).isoformat(),
                "offboarding_record": offboarding,
                "feedback": feedback,
                "data_deleted": False,  # Kept for audit; set True after retention period
                "retention_until": None,
            }
            # Mark offboarding complete
            if user_id in self._offboarding_records:
                self._offboarding_records[user_id]["status"] = "completed"
                for item in self._offboarding_records[user_id].get("checklist", []):
                    if item["task"] == "Archive user data":
                        item["status"] = "done"
        self.log_activity(f"User data archived for '{user_id}' (archive_id={archive_id}).")
        return True
