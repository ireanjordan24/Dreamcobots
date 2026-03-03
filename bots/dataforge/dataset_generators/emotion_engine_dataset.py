"""
bots/dataforge/dataset_generators/emotion_engine_dataset.py

EmotionEngineDatasetGenerator – generates simulated emotion/sentiment
dataset samples suitable for training affective-computing models.
"""

import logging
import os
import random
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

_EMOTIONS = [
    "joy",
    "sadness",
    "anger",
    "fear",
    "surprise",
    "disgust",
    "trust",
    "anticipation",
    "neutral",
]

_CONTEXTS = [
    "customer_support",
    "social_media",
    "product_review",
    "news_article",
    "conversation",
    "neutral",
    "gaming",
    "music_listening",
    "exercise",
]

_MODALITIES = ["text", "audio", "facial", "physiological", "multimodal"]


class EmotionEngineDatasetGenerator:
    """
    Generates simulated emotion and sentiment dataset samples.

    Each sample contains a context, a dominant emotion label, a valence–
    arousal–dominance (VAD) vector, per-emotion probability scores, and
    optional multimodal signals.
    """

    def __init__(self) -> None:
        """Initialise the generator."""
        self._sample_count = 0
        self._batch_count = 0
        logger.info("EmotionEngineDatasetGenerator initialised")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _random_emotion_scores(self) -> dict[str, float]:
        """Return random probability scores for all emotions that sum to 1."""
        raw = {em: random.random() for em in _EMOTIONS}
        total = sum(raw.values())
        return {em: round(v / total, 4) for em, v in raw.items()}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_sample(self, context: str | None = None) -> dict[str, Any]:
        """
        Generate a single emotion/sentiment sample.

        Args:
            context: Optional context label (e.g. ``"social_media"``).
                     A random context is chosen if not provided.

        Returns:
            A dict with emotion labels, VAD scores, and modality signals.
        """
        ctx = context if context in _CONTEXTS else random.choice(_CONTEXTS)
        emotion_scores = self._random_emotion_scores()
        dominant_emotion = max(emotion_scores, key=emotion_scores.__getitem__)
        sentiment_polarity = round(random.uniform(-1.0, 1.0), 4)
        sentiment_label = (
            "positive"
            if sentiment_polarity > 0.1
            else ("negative" if sentiment_polarity < -0.1 else "neutral")
        )

        self._sample_count += 1
        sample_id = str(uuid.uuid4())

        sample: dict[str, Any] = {
            "sample_id": sample_id,
            "context": ctx,
            "modality": random.choice(_MODALITIES),
            "dominant_emotion": dominant_emotion,
            "emotion_scores": emotion_scores,
            "sentiment_polarity": sentiment_polarity,
            "sentiment_label": sentiment_label,
            "subjectivity": round(random.uniform(0.0, 1.0), 4),
            "vad_vector": {
                "valence": round(random.uniform(-1.0, 1.0), 4),
                "arousal": round(random.uniform(0.0, 1.0), 4),
                "dominance": round(random.uniform(0.0, 1.0), 4),
            },
            "text_snippet": (
                f"Simulated {ctx} text conveying {dominant_emotion}. "
                "This is a synthetically generated sample."
            ),
            "confidence": round(random.uniform(0.5, 1.0), 4),
            "intensity": round(random.uniform(0.1, 1.0), 4),
            "is_sarcastic": random.random() < 0.1,
            "language": random.choice(["en", "es", "fr", "de", "zh", "ja"]),
            "annotator_agreement": round(random.uniform(0.5, 1.0), 4),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.debug(
            "Generated emotion sample %s (dominant=%s, context=%s)",
            sample_id,
            dominant_emotion,
            ctx,
        )
        return sample

    def generate_batch(
        self,
        num_samples: int,
        output_dir: str = "/tmp/emotion_dataset",
    ) -> list[dict[str, Any]]:
        """
        Generate a batch of emotion samples.

        Args:
            num_samples: Number of samples to generate.
            output_dir: Directory path (created if necessary; no files written).

        Returns:
            A list of sample dicts.
        """
        os.makedirs(output_dir, exist_ok=True)
        batch = [
            self.generate_sample(context=random.choice(_CONTEXTS))
            for _ in range(num_samples)
        ]
        self._batch_count += 1
        logger.info(
            "Emotion batch %d complete: %d samples in %s",
            self._batch_count,
            num_samples,
            output_dir,
        )
        return batch

    def validate_sample(self, sample: dict) -> bool:
        """
        Validate an emotion sample dict.

        Args:
            sample: Sample produced by :meth:`generate_sample`.

        Returns:
            ``True`` if valid, ``False`` otherwise.
        """
        required = {
            "sample_id",
            "dominant_emotion",
            "emotion_scores",
            "sentiment_label",
            "vad_vector",
        }
        if not required.issubset(sample.keys()):
            logger.warning("Emotion sample missing required keys")
            return False
        if sample["dominant_emotion"] not in _EMOTIONS:
            logger.warning(
                "Unknown dominant_emotion: %s", sample["dominant_emotion"]
            )
            return False
        vad = sample["vad_vector"]
        if not isinstance(vad, dict) or not {"valence", "arousal", "dominance"}.issubset(vad):
            logger.warning("Emotion sample has invalid vad_vector")
            return False
        return True

    def get_metadata(self) -> dict[str, Any]:
        """
        Return metadata describing this generator.

        Returns:
            A metadata dict.
        """
        return {
            "generator": "EmotionEngineDatasetGenerator",
            "version": "1.0.0",
            "emotion_labels": _EMOTIONS,
            "contexts": _CONTEXTS,
            "modalities": _MODALITIES,
            "vad_dimensions": ["valence", "arousal", "dominance"],
            "samples_generated": self._sample_count,
            "batches_generated": self._batch_count,
            "description": "Simulated emotion/sentiment samples with VAD vectors and per-emotion scores",
        }
