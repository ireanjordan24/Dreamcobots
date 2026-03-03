"""
bots/dataforge/packaging/json_packager.py

JSONPackager – serialises dataset samples to JSON files.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class JSONPackager:
    """
    Packages dataset samples into JSON format.

    Each call to :meth:`package` writes a single JSON file containing
    the full list of samples plus a metadata header.
    """

    def __init__(self, indent: int = 2) -> None:
        """
        Initialise the packager.

        Args:
            indent: JSON indentation level (spaces).
        """
        self.indent = indent
        self._packages_created = 0
        logger.info("JSONPackager initialised (indent=%d)", indent)

    def package(
        self,
        samples: list[dict[str, Any]],
        output_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Write *samples* to a JSON file at *output_path*.

        Args:
            samples: List of dataset sample dicts.
            output_path: Destination file path (directories are created).
            metadata: Optional metadata dict to embed in the output envelope.

        Returns:
            The absolute path to the written file.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        envelope: dict[str, Any] = {
            "metadata": {
                "packager": "JSONPackager",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "sample_count": len(samples),
                **(metadata or {}),
            },
            "samples": samples,
        }
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(envelope, fh, indent=self.indent, default=str)

        self._packages_created += 1
        logger.info(
            "JSONPackager wrote %d samples to '%s'", len(samples), output_path
        )
        return os.path.abspath(output_path)

    def get_stats(self) -> dict[str, Any]:
        """Return packaging statistics."""
        return {
            "packager": "JSONPackager",
            "packages_created": self._packages_created,
        }
