"""
bots/dataforge/packaging/csv_packager.py

CSVPackager – serialises dataset samples to CSV files using pandas.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class CSVPackager:
    """
    Packages dataset samples into CSV format using pandas.

    Nested dicts/lists within samples are JSON-serialised into their
    respective columns so the CSV remains flat.
    """

    def __init__(self, sep: str = ",") -> None:
        """
        Initialise the packager.

        Args:
            sep: Column delimiter character.
        """
        self.sep = sep
        self._packages_created = 0
        logger.info("CSVPackager initialised (sep='%s')", sep)

    def package(
        self,
        samples: list[dict[str, Any]],
        output_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Write *samples* to a CSV file at *output_path*.

        Args:
            samples: List of dataset sample dicts.
            output_path: Destination file path (directories are created).
            metadata: Optional metadata (written to a sidecar ``<name>.meta.json``).

        Returns:
            The absolute path to the written CSV file.
        """
        import json

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Flatten nested values to strings for CSV compatibility.
        flat_samples = []
        for s in samples:
            flat = {}
            for k, v in s.items():
                flat[k] = json.dumps(v, default=str) if isinstance(v, (dict, list)) else v
            flat_samples.append(flat)

        df = pd.DataFrame(flat_samples)
        df.to_csv(output_path, index=False, sep=self.sep)

        # Write sidecar metadata file if provided.
        if metadata:
            meta_path = output_path.rsplit(".", 1)[0] + ".meta.json"
            with open(meta_path, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "sample_count": len(samples),
                        **metadata,
                    },
                    fh,
                    indent=2,
                )

        self._packages_created += 1
        logger.info(
            "CSVPackager wrote %d rows to '%s'", len(samples), output_path
        )
        return os.path.abspath(output_path)

    def get_stats(self) -> dict[str, Any]:
        """Return packaging statistics."""
        return {
            "packager": "CSVPackager",
            "packages_created": self._packages_created,
        }
