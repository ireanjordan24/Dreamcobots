"""
bots/dataforge/dataset_generators/facial_dataset.py

FacialDatasetGenerator – generates simulated facial image dataset samples
using numpy arrays.  No real camera or face-capture hardware is required.
"""

import logging
import os
import random
import uuid
from datetime import datetime, timezone
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

_EMOTIONS = ["neutral", "happy", "sad", "angry", "surprised", "fearful", "disgusted"]
_LIGHTING = ["natural", "studio", "low_light", "backlit", "side_lit"]
_ETHNICITIES = ["diverse_synthetic"]  # single synthetic label to avoid bias tagging


class FacialDatasetGenerator:
    """
    Generates simulated facial image dataset samples.

    Images are represented as numpy arrays of shape ``(H, W, 3)``
    containing random pixel values within a realistic skin-tone range.
    """

    def __init__(self) -> None:
        """Initialise the generator."""
        self._sample_count = 0
        self._batch_count = 0
        logger.info("FacialDatasetGenerator initialised")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_sample(
        self,
        image_size: tuple[int, int] = (128, 128),
    ) -> dict[str, Any]:
        """
        Generate a single simulated facial image sample.

        Args:
            image_size: ``(height, width)`` of the image in pixels.

        Returns:
            A dict containing the sample id, a flattened pixel list,
            shape information, and facial landmark positions.
        """
        h, w = image_size
        # Simulate a skin-tone base with random variation.
        base_color = np.array(
            [
                random.randint(100, 240),  # R
                random.randint(80, 200),   # G
                random.randint(60, 170),   # B
            ],
            dtype=np.uint8,
        )
        noise = np.random.randint(-30, 30, size=(h, w, 3), dtype=np.int16)
        image = np.clip(
            base_color.astype(np.int16) + noise, 0, 255
        ).astype(np.uint8)

        # Simulate facial landmarks (68 standard points, normalised 0-1).
        landmarks: list[dict[str, float]] = [
            {"x": round(random.uniform(0.1, 0.9), 4), "y": round(random.uniform(0.1, 0.9), 4)}
            for _ in range(68)
        ]

        self._sample_count += 1
        sample_id = str(uuid.uuid4())

        sample: dict[str, Any] = {
            "sample_id": sample_id,
            "image_height": h,
            "image_width": w,
            "channels": 3,
            "pixel_data": image.flatten().tolist(),
            "landmarks_68": landmarks,
            "emotion_label": random.choice(_EMOTIONS),
            "lighting_condition": random.choice(_LIGHTING),
            "age_range": random.choice(["18-25", "26-35", "36-50", "51-65", "65+"]),
            "bounding_box": {
                "x": round(random.uniform(0.05, 0.2), 4),
                "y": round(random.uniform(0.05, 0.2), 4),
                "w": round(random.uniform(0.5, 0.8), 4),
                "h": round(random.uniform(0.5, 0.8), 4),
            },
            "quality_score": round(random.uniform(0.6, 1.0), 4),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.debug(
            "Generated facial sample %s (%dx%d)", sample_id, h, w
        )
        return sample

    def generate_batch(
        self,
        num_samples: int,
        output_dir: str = "/tmp/facial_dataset",
    ) -> list[dict[str, Any]]:
        """
        Generate a batch of facial image samples.

        Args:
            num_samples: Number of samples to generate.
            output_dir: Directory path (created if necessary; no files written).

        Returns:
            A list of sample dicts.
        """
        os.makedirs(output_dir, exist_ok=True)
        sizes = [(64, 64), (128, 128), (256, 256)]
        batch = [
            self.generate_sample(image_size=random.choice(sizes))
            for _ in range(num_samples)
        ]
        self._batch_count += 1
        logger.info(
            "Facial batch %d complete: %d samples in %s",
            self._batch_count,
            num_samples,
            output_dir,
        )
        return batch

    def validate_sample(self, sample: dict) -> bool:
        """
        Validate a facial sample dict.

        Args:
            sample: Sample produced by :meth:`generate_sample`.

        Returns:
            ``True`` if valid, ``False`` otherwise.
        """
        required = {"sample_id", "image_height", "image_width", "channels", "pixel_data"}
        if not required.issubset(sample.keys()):
            logger.warning("Facial sample missing required keys")
            return False
        expected_pixels = sample["image_height"] * sample["image_width"] * sample["channels"]
        if len(sample["pixel_data"]) != expected_pixels:
            logger.warning(
                "Facial sample pixel_data length %d != expected %d",
                len(sample["pixel_data"]),
                expected_pixels,
            )
            return False
        return True

    def get_metadata(self) -> dict[str, Any]:
        """
        Return metadata describing this generator.

        Returns:
            A metadata dict.
        """
        return {
            "generator": "FacialDatasetGenerator",
            "version": "1.0.0",
            "supported_image_sizes": [(64, 64), (128, 128), (256, 256)],
            "landmark_count": 68,
            "emotion_labels": _EMOTIONS,
            "lighting_conditions": _LIGHTING,
            "samples_generated": self._sample_count,
            "batches_generated": self._batch_count,
            "description": "Simulated facial images with landmarks and emotion labels",
        }
