"""
framework/adaptive_learning.py

Simple in-memory adaptive learning engine for DreamCobots.
Uses pattern-matching and lightweight statistical updates —
no external ML runtime required.
"""

from __future__ import annotations

import json
import logging
import math
import threading
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class AdaptiveLearning:
    """
    Lightweight adaptive learning engine backed by an in-memory dictionary.

    The model stores ``(input_key -> output_value)`` mappings together with
    confidence scores that are updated with each training pass.  Prediction
    performs nearest-neighbour lookup by string-token overlap.
    """

    def __init__(self) -> None:
        self._lock: threading.RLock = threading.RLock()
        # model: { input_key: {"output": Any, "confidence": float, "hits": int} }
        self._model: dict[str, dict[str, Any]] = {}
        self._training_samples: list[tuple[Any, Any]] = []
        self._loss_history: list[float] = []
        self._trained_at: str | None = None
        self.logger = logging.getLogger("AdaptiveLearning")

    # ------------------------------------------------------------------
    # Training data management
    # ------------------------------------------------------------------

    def add_training_sample(self, input_data: Any, output_data: Any) -> None:
        """
        Add a single training sample.

        Args:
            input_data: The input (ideally a str or dict).
            output_data: The expected output.
        """
        with self._lock:
            self._training_samples.append((input_data, output_data))
        self.logger.debug(
            "Training sample added. Total samples: %d", len(self._training_samples)
        )

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self, epochs: int = 10) -> dict[str, Any]:
        """
        Train the model on all accumulated samples.

        Each epoch re-scans every sample and updates confidence scores.
        A simple mean-squared-error proxy (``1 - confidence``) is computed
        as the loss.

        Args:
            epochs: Number of training epochs.

        Returns:
            A dict with ``epochs``, ``final_loss``, and ``loss_history``.
        """
        if epochs < 1:
            raise ValueError("epochs must be >= 1")

        with self._lock:
            samples = list(self._training_samples)

        if not samples:
            self.logger.warning("No training samples — skipping training.")
            return {"epochs": 0, "final_loss": 0.0, "loss_history": []}

        loss_history: list[float] = []
        learning_rate = 0.1

        for epoch in range(epochs):
            epoch_loss = 0.0
            for input_data, output_data in samples:
                key = self._to_key(input_data)
                with self._lock:
                    entry = self._model.get(key)
                    if entry is None:
                        # First encounter — initialise with low confidence
                        self._model[key] = {
                            "output": output_data,
                            "confidence": 0.5,
                            "hits": 1,
                        }
                        epoch_loss += 0.5
                    else:
                        # Update confidence towards 1.0 with LR decay
                        old_conf = entry["confidence"]
                        new_conf = min(1.0, old_conf + learning_rate * (1.0 - old_conf))
                        entry["confidence"] = new_conf
                        entry["hits"] += 1
                        # If output changed, reset confidence
                        if entry["output"] != output_data:
                            entry["output"] = output_data
                            entry["confidence"] = 0.5
                        epoch_loss += 1.0 - new_conf

            avg_loss = epoch_loss / len(samples) if samples else 0.0
            loss_history.append(round(avg_loss, 6))
            self.logger.debug("Epoch %d/%d — loss: %.6f", epoch + 1, epochs, avg_loss)

        with self._lock:
            self._loss_history.extend(loss_history)
            self._trained_at = datetime.now(timezone.utc).isoformat()

        return {
            "epochs": epochs,
            "final_loss": loss_history[-1] if loss_history else 0.0,
            "loss_history": loss_history,
        }

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(self, input_data: Any) -> dict[str, Any]:
        """
        Predict the output for *input_data* using the trained model.

        Performs exact lookup first; falls back to best-token-overlap match.

        Args:
            input_data: Query input.

        Returns:
            Dict with ``output``, ``confidence``, and ``match_type`` keys.
        """
        key = self._to_key(input_data)
        with self._lock:
            # Exact match
            entry = self._model.get(key)
            if entry:
                return {
                    "output": entry["output"],
                    "confidence": entry["confidence"],
                    "match_type": "exact",
                }
            # Fuzzy token-overlap match
            if not self._model:
                return {"output": None, "confidence": 0.0, "match_type": "no_model"}

            query_tokens = set(key.lower().split())
            best_score = -1.0
            best_entry: dict[str, Any] | None = None
            for model_key, model_entry in self._model.items():
                model_tokens = set(model_key.lower().split())
                if not query_tokens and not model_tokens:
                    score = 1.0
                elif not query_tokens or not model_tokens:
                    score = 0.0
                else:
                    intersection = query_tokens & model_tokens
                    union = query_tokens | model_tokens
                    score = len(intersection) / len(union)  # Jaccard similarity
                if score > best_score:
                    best_score = score
                    best_entry = model_entry

        if best_entry and best_score > 0:
            adjusted_confidence = round(best_entry["confidence"] * best_score, 4)
            return {
                "output": best_entry["output"],
                "confidence": adjusted_confidence,
                "match_type": "fuzzy",
                "similarity": round(best_score, 4),
            }
        return {"output": None, "confidence": 0.0, "match_type": "no_match"}

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_model(self, path: str) -> None:
        """
        Save the model to a JSON file at *path*.

        Args:
            path: File system path (will be created/overwritten).
        """
        with self._lock:
            payload = {
                "model": self._model,
                "loss_history": self._loss_history,
                "trained_at": self._trained_at,
                "sample_count": len(self._training_samples),
            }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, default=str)
        self.logger.info("Model saved to %s", path)

    def load_model(self, path: str) -> None:
        """
        Load a previously saved model from *path*.

        Args:
            path: File system path of the JSON model file.

        Raises:
            FileNotFoundError: If *path* does not exist.
            ValueError: If the file content is malformed.
        """
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        if "model" not in payload:
            raise ValueError(f"Invalid model file: 'model' key missing in {path}")
        with self._lock:
            self._model = payload["model"]
            self._loss_history = payload.get("loss_history", [])
            self._trained_at = payload.get("trained_at")
        self.logger.info(
            "Model loaded from %s (%d entries)", path, len(self._model)
        )

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def get_performance_metrics(self) -> dict[str, Any]:
        """
        Return performance metrics for the current model state.

        Returns:
            Dict with ``model_size``, ``sample_count``, ``average_confidence``,
            ``trained_at``, ``loss_history_tail``, and ``final_loss``.
        """
        with self._lock:
            model_size = len(self._model)
            sample_count = len(self._training_samples)
            confidences = [e["confidence"] for e in self._model.values()]
            avg_conf = (
                round(sum(confidences) / len(confidences), 4)
                if confidences else 0.0
            )
            loss_tail = self._loss_history[-10:]
            final_loss = self._loss_history[-1] if self._loss_history else None
            trained_at = self._trained_at

        return {
            "model_size": model_size,
            "sample_count": sample_count,
            "average_confidence": avg_conf,
            "trained_at": trained_at,
            "loss_history_tail": loss_tail,
            "final_loss": final_loss,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_key(data: Any) -> str:
        """Convert arbitrary input to a stable string key."""
        if isinstance(data, str):
            return data.strip()
        if isinstance(data, dict):
            return json.dumps(data, sort_keys=True, default=str)
        return str(data)
