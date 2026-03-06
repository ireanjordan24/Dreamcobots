"""
bots/dataforge/dataset_generators/voice_dataset.py

VoiceDatasetGenerator – generates simulated audio dataset samples.
No real microphone or audio library is required; audio data is
represented as lists of float amplitudes.
"""

import logging
import math
import os
import random
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Supported audio encodings for metadata.
_ENCODINGS = ["PCM_16", "PCM_32", "FLOAT_32"]
_LANGUAGES = ["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "zh-CN", "ja-JP"]


class VoiceDatasetGenerator:
    """
    Generates simulated voice/audio dataset samples.

    Each sample contains a list of amplitude values representing a
    mono audio signal generated via a synthetic sine-wave mix.
    """

    def __init__(self) -> None:
        """Initialise the generator with internal counters."""
        self._sample_count = 0
        self._batch_count = 0
        logger.info("VoiceDatasetGenerator initialised")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_sample(
        self,
        duration_seconds: float = 1.0,
        sample_rate: int = 16000,
    ) -> dict[str, Any]:
        """
        Generate a single simulated audio sample.

        The audio signal is a mixture of two sine waves with random
        frequencies to simulate a spoken utterance.

        Args:
            duration_seconds: Duration of the audio clip in seconds.
            sample_rate: Sampling rate in Hz.

        Returns:
            A dict containing the sample id, audio amplitudes, metadata,
            and quality indicators.
        """
        num_frames = int(duration_seconds * sample_rate)
        freq1 = random.uniform(100.0, 800.0)
        freq2 = random.uniform(800.0, 3400.0)
        amplitude = random.uniform(0.3, 1.0)

        audio_data: list[float] = [
            round(
                amplitude
                * (
                    0.7 * math.sin(2 * math.pi * freq1 * t / sample_rate)
                    + 0.3 * math.sin(2 * math.pi * freq2 * t / sample_rate)
                )
                + random.gauss(0, 0.01),  # add slight noise
                6,
            )
            for t in range(num_frames)
        ]

        self._sample_count += 1
        sample_id = str(uuid.uuid4())

        sample: dict[str, Any] = {
            "sample_id": sample_id,
            "duration_seconds": duration_seconds,
            "sample_rate": sample_rate,
            "num_frames": num_frames,
            "channels": 1,
            "encoding": random.choice(_ENCODINGS),
            "language": random.choice(_LANGUAGES),
            "audio_data": audio_data,
            "snr_db": round(random.uniform(15.0, 40.0), 2),
            "has_transcript": random.choice([True, False]),
            "transcript": "simulated transcript text" if random.random() > 0.5 else None,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.debug("Generated voice sample %s (%d frames)", sample_id, num_frames)
        return sample

    def generate_batch(
        self,
        num_samples: int,
        output_dir: str = "/tmp/voice_dataset",
    ) -> list[dict[str, Any]]:
        """
        Generate a batch of voice samples.

        Args:
            num_samples: Number of samples to generate.
            output_dir: Directory path where samples would be saved
                        (simulated – directory is created but files are not
                        written to disk).

        Returns:
            A list of sample dicts.
        """
        os.makedirs(output_dir, exist_ok=True)
        batch: list[dict[str, Any]] = []
        for _ in range(num_samples):
            duration = random.uniform(0.5, 5.0)
            sample = self.generate_sample(
                duration_seconds=duration,
                sample_rate=random.choice([8000, 16000, 22050, 44100]),
            )
            batch.append(sample)

        self._batch_count += 1
        logger.info(
            "Voice batch %d complete: %d samples in %s",
            self._batch_count,
            num_samples,
            output_dir,
        )
        return batch

    def validate_sample(self, sample: dict) -> bool:
        """
        Validate that a sample dict has the required structure and value ranges.

        Args:
            sample: A sample dict as produced by :meth:`generate_sample`.

        Returns:
            ``True`` if the sample is valid, otherwise ``False``.
        """
        required_keys = {
            "sample_id",
            "duration_seconds",
            "sample_rate",
            "num_frames",
            "audio_data",
        }
        if not required_keys.issubset(sample.keys()):
            logger.warning("Voice sample missing required keys")
            return False
        if not isinstance(sample["audio_data"], list) or len(sample["audio_data"]) == 0:
            logger.warning("Voice sample has empty or invalid audio_data")
            return False
        if sample["duration_seconds"] <= 0 or sample["sample_rate"] <= 0:
            logger.warning("Voice sample has non-positive duration or sample_rate")
            return False
        return True

    def get_metadata(self) -> dict[str, Any]:
        """
        Return metadata describing this generator's configuration and statistics.

        Returns:
            A dict of metadata key-value pairs.
        """
        return {
            "generator": "VoiceDatasetGenerator",
            "version": "1.0.0",
            "supported_sample_rates": [8000, 16000, 22050, 44100],
            "supported_encodings": _ENCODINGS,
            "supported_languages": _LANGUAGES,
            "samples_generated": self._sample_count,
            "batches_generated": self._batch_count,
            "description": "Simulated mono audio samples using synthetic sine-wave mixtures",
        }
