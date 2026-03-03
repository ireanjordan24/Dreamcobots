"""
bots/dataforge/packaging/jsonl_packager.py

JSONLPackager – serialises dataset samples to JSONL (JSON Lines) format.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class JSONLPackager:
    """
    Packages dataset samples into JSONL (JSON Lines) format.

    Each sample is written as a separate JSON object on its own line,
    making the format well-suited for streaming and large-scale ML training.
    """

    def __init__(self) -> None:
        """Initialise the packager."""
        self._packages_created = 0
        self._lines_written = 0
        logger.info("JSONLPackager initialised")

    def package(
        self,
        samples: list[dict[str, Any]],
        output_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Write *samples* to a JSONL file at *output_path*.

        A metadata comment line is prepended as the first record with a
        ``__metadata__`` key so downstream readers can skip it if desired.

        Args:
            samples: List of dataset sample dicts.
            output_path: Destination ``.jsonl`` file path.
            metadata: Optional metadata to embed as the first record.

        Returns:
            The absolute path to the written file.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as fh:
            # Write metadata record first.
            meta_record: dict[str, Any] = {
                "__metadata__": True,
                "packager": "JSONLPackager",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "sample_count": len(samples),
                **(metadata or {}),
            }
            fh.write(json.dumps(meta_record, default=str) + "\n")

            for sample in samples:
                fh.write(json.dumps(sample, default=str) + "\n")
                self._lines_written += 1

        self._packages_created += 1
        logger.info(
            "JSONLPackager wrote %d samples to '%s'", len(samples), output_path
        )
        return os.path.abspath(output_path)

    def get_stats(self) -> dict[str, Any]:
        """Return packaging statistics."""
        return {
            "packager": "JSONLPackager",
            "packages_created": self._packages_created,
            "total_lines_written": self._lines_written,
        }
