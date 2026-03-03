"""
bots/dataforge/packaging/wav_packager.py

WAVPackager – packages audio dataset samples as WAV files.

Since the voice generator produces lists of float amplitudes, this packager
writes those as 16-bit PCM WAV files using Python's built-in ``wave`` module.
No external audio library is required.
"""

import logging
import os
import struct
import wave
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

_MAX_INT16 = 32767


class WAVPackager:
    """
    Packages audio dataset samples into WAV files.

    Each sample that contains an ``audio_data`` field (list of floats in
    the range ``[-1, 1]``) is written as a separate 16-bit mono WAV file.
    A manifest JSON file is also created listing all written files.
    """

    def __init__(self) -> None:
        """Initialise the packager."""
        self._packages_created = 0
        self._files_written = 0
        logger.info("WAVPackager initialised")

    def _write_wav(
        self,
        audio_data: list[float],
        sample_rate: int,
        output_path: str,
    ) -> None:
        """
        Write a list of float amplitudes as a 16-bit mono WAV file.

        Args:
            audio_data: Audio samples in the range ``[-1.0, 1.0]``.
            sample_rate: Sampling rate in Hz.
            output_path: Destination file path.
        """
        pcm_samples = [
            max(-_MAX_INT16, min(_MAX_INT16, int(a * _MAX_INT16)))
            for a in audio_data
        ]
        with wave.open(output_path, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(struct.pack(f"<{len(pcm_samples)}h", *pcm_samples))

    def package(
        self,
        samples: list[dict[str, Any]],
        output_dir: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Write each sample's audio data as a WAV file and create a manifest.

        Args:
            samples: List of audio sample dicts (must contain ``audio_data``
                     and ``sample_rate`` fields).
            output_dir: Directory to write WAV files and the manifest into.
            metadata: Optional metadata to embed in the manifest.

        Returns:
            The absolute path to the manifest JSON file.
        """
        import json

        os.makedirs(output_dir, exist_ok=True)
        manifest: list[dict[str, Any]] = []

        for idx, sample in enumerate(samples):
            audio_data = sample.get("audio_data")
            if not isinstance(audio_data, list) or len(audio_data) == 0:
                logger.warning("Skipping sample %d – missing audio_data", idx)
                continue

            sample_rate = sample.get("sample_rate", 16000)
            sample_id = sample.get("sample_id", f"sample_{idx}")
            wav_path = os.path.join(output_dir, f"{sample_id}.wav")

            self._write_wav(audio_data, sample_rate, wav_path)
            self._files_written += 1

            manifest.append(
                {
                    "sample_id": sample_id,
                    "wav_file": os.path.basename(wav_path),
                    "sample_rate": sample_rate,
                    "duration_seconds": sample.get("duration_seconds"),
                    "transcript": sample.get("transcript"),
                    "language": sample.get("language"),
                }
            )

        manifest_path = os.path.join(output_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "total_files": len(manifest),
                    **(metadata or {}),
                    "files": manifest,
                },
                fh,
                indent=2,
            )

        self._packages_created += 1
        logger.info(
            "WAVPackager wrote %d WAV files to '%s'", len(manifest), output_dir
        )
        return os.path.abspath(manifest_path)

    def get_stats(self) -> dict[str, Any]:
        """Return packaging statistics."""
        return {
            "packager": "WAVPackager",
            "packages_created": self._packages_created,
            "wav_files_written": self._files_written,
        }
