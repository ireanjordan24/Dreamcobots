"""
framework/dataset_manager.py

In-memory dataset manager for DreamCobots framework.
Supports add, get, list, export, merge, and stats operations.
"""

from __future__ import annotations

import csv
import json
import logging
import threading
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class DatasetManager:
    """
    Manages named datasets in memory with export, merge, and stats capabilities.

    Each dataset is stored as a list of records (arbitrary dicts/values)
    along with optional metadata.
    """

    _SUPPORTED_FORMATS: frozenset[str] = frozenset({"json", "jsonl", "csv"})

    def __init__(self) -> None:
        self._lock: threading.RLock = threading.RLock()
        # { name: {"data": list, "metadata": dict, "created_at": str, "updated_at": str} }
        self._datasets: dict[str, dict[str, Any]] = {}
        self.logger = logging.getLogger("DatasetManager")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def add_dataset(
        self,
        name: str,
        data: list[Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add or replace a dataset.

        Args:
            name: Unique dataset name.
            data: List of records.
            metadata: Optional dict of descriptive metadata.

        Raises:
            ValueError: If *name* is empty or *data* is not a list.
        """
        if not name or not name.strip():
            raise ValueError("Dataset name must be a non-empty string.")
        if not isinstance(data, list):
            raise ValueError(f"data must be a list, got {type(data).__name__}")

        now = datetime.now(timezone.utc).isoformat()
        entry: dict[str, Any] = {
            "data": list(data),
            "metadata": dict(metadata or {}),
            "created_at": now,
            "updated_at": now,
        }
        with self._lock:
            if name in self._datasets:
                entry["created_at"] = self._datasets[name]["created_at"]
            self._datasets[name] = entry
        self.logger.info(
            "Dataset '%s' added/updated: %d records.", name, len(data)
        )

    def get_dataset(self, name: str) -> list[Any]:
        """
        Retrieve a dataset by name.

        Args:
            name: Dataset name.

        Returns:
            A copy of the dataset's record list.

        Raises:
            KeyError: If the dataset does not exist.
        """
        with self._lock:
            entry = self._datasets.get(name)
        if entry is None:
            raise KeyError(f"Dataset '{name}' not found.")
        return list(entry["data"])

    def list_datasets(self) -> list[str]:
        """Return a sorted list of all dataset names."""
        with self._lock:
            return sorted(self._datasets.keys())

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_dataset(
        self,
        name: str,
        format: str,
        output_path: str,
    ) -> None:
        """
        Export a dataset to a file.

        Args:
            name: Dataset name.
            format: One of ``"json"``, ``"jsonl"``, ``"csv"``.
            output_path: File path to write to.

        Raises:
            KeyError: If the dataset does not exist.
            ValueError: If the format is unsupported.
        """
        fmt = format.lower().strip()
        if fmt not in self._SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format '{format}'. "
                f"Supported: {sorted(self._SUPPORTED_FORMATS)}"
            )
        data = self.get_dataset(name)

        if fmt == "json":
            with open(output_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, default=str)

        elif fmt == "jsonl":
            with open(output_path, "w", encoding="utf-8") as fh:
                for record in data:
                    fh.write(json.dumps(record, default=str) + "\n")

        elif fmt == "csv":
            if not data:
                with open(output_path, "w", encoding="utf-8", newline="") as fh:
                    fh.write("")
            else:
                # Flatten to dicts if possible
                rows = data if isinstance(data[0], dict) else [{"value": r} for r in data]
                fieldnames = list({k for row in rows for k in (row.keys() if isinstance(row, dict) else [])})
                with open(output_path, "w", encoding="utf-8", newline="") as fh:
                    writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(row if isinstance(row, dict) else {"value": row})

        self.logger.info("Dataset '%s' exported to %s (%s).", name, output_path, fmt)

    # ------------------------------------------------------------------
    # Merge
    # ------------------------------------------------------------------

    def merge_datasets(self, names: list[str], new_name: str) -> None:
        """
        Merge multiple datasets into a new combined dataset.

        Args:
            names: List of source dataset names.
            new_name: Name for the resulting merged dataset.

        Raises:
            KeyError: If any source dataset does not exist.
            ValueError: If *names* is empty.
        """
        if not names:
            raise ValueError("names list must not be empty.")
        merged: list[Any] = []
        metadata: dict[str, Any] = {"merged_from": names}
        for n in names:
            merged.extend(self.get_dataset(n))
        self.add_dataset(new_name, merged, metadata)
        self.logger.info(
            "Datasets %s merged into '%s' (%d total records).",
            names, new_name, len(merged),
        )

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_stats(self, name: str) -> dict[str, Any]:
        """
        Return statistics for a named dataset.

        Args:
            name: Dataset name.

        Returns:
            Dict with ``name``, ``record_count``, ``metadata``,
            ``created_at``, ``updated_at``, and ``field_names``
            (if records are dicts).

        Raises:
            KeyError: If the dataset does not exist.
        """
        with self._lock:
            entry = self._datasets.get(name)
        if entry is None:
            raise KeyError(f"Dataset '{name}' not found.")

        data = entry["data"]
        field_names: list[str] = []
        if data and isinstance(data[0], dict):
            field_names = sorted({k for rec in data for k in rec.keys()})

        return {
            "name": name,
            "record_count": len(data),
            "metadata": dict(entry["metadata"]),
            "created_at": entry["created_at"],
            "updated_at": entry["updated_at"],
            "field_names": field_names,
        }
