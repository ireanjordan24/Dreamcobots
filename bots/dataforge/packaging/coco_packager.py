"""
bots/dataforge/packaging/coco_packager.py

COCOPackager – packages image dataset samples in the COCO (Common Objects in
Context) JSON annotation format.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class COCOPackager:
    """
    Packages facial/image dataset samples into COCO annotation format.

    The COCO format JSON contains ``info``, ``licenses``, ``images``,
    ``annotations``, and ``categories`` sections as per the standard spec.
    """

    def __init__(self) -> None:
        """Initialise the packager."""
        self._packages_created = 0
        logger.info("COCOPackager initialised")

    def package(
        self,
        samples: list[dict[str, Any]],
        output_path: str,
        metadata: dict[str, Any] | None = None,
        categories: list[dict[str, Any]] | None = None,
    ) -> str:
        """
        Convert *samples* to a COCO-format JSON file.

        Args:
            samples: List of image/facial sample dicts.  Each sample should
                     have at minimum ``sample_id``, ``image_width``,
                     ``image_height``, and optionally ``bounding_box`` and
                     ``emotion_label``.
            output_path: Destination JSON file path.
            metadata: Optional extra fields added to the ``info`` block.
            categories: Optional list of COCO category dicts.  A default
                        emotion-label category set is used if not provided.

        Returns:
            The absolute path to the written file.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Default categories: one per emotion label.
        if categories is None:
            emotion_labels = [
                "neutral", "happy", "sad", "angry",
                "surprised", "fearful", "disgusted",
            ]
            categories = [
                {"id": i + 1, "name": label, "supercategory": "emotion"}
                for i, label in enumerate(emotion_labels)
            ]

        cat_name_to_id = {c["name"]: c["id"] for c in categories}

        images: list[dict[str, Any]] = []
        annotations: list[dict[str, Any]] = []
        annotation_id = 1

        for idx, sample in enumerate(samples):
            image_id = idx + 1
            images.append(
                {
                    "id": image_id,
                    "file_name": f"{sample.get('sample_id', f'img_{idx}')}.jpg",
                    "width": sample.get("image_width", 128),
                    "height": sample.get("image_height", 128),
                    "date_captured": sample.get(
                        "generated_at", datetime.now(timezone.utc).isoformat()
                    ),
                }
            )

            bb = sample.get("bounding_box")
            emotion = sample.get("emotion_label", "neutral")
            cat_id = cat_name_to_id.get(emotion, 1)

            if bb:
                w = sample.get("image_width", 128)
                h = sample.get("image_height", 128)
                x = round(bb.get("x", 0.0) * w, 1)
                y = round(bb.get("y", 0.0) * h, 1)
                bw = round(bb.get("w", 1.0) * w, 1)
                bh = round(bb.get("h", 1.0) * h, 1)
                annotations.append(
                    {
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": cat_id,
                        "bbox": [x, y, bw, bh],
                        "area": round(bw * bh, 2),
                        "iscrowd": 0,
                        "segmentation": [],
                    }
                )
                annotation_id += 1

        coco_json: dict[str, Any] = {
            "info": {
                "description": "DataForge COCO-format dataset",
                "version": "1.0",
                "year": datetime.now(timezone.utc).year,
                "date_created": datetime.now(timezone.utc).isoformat(),
                **(metadata or {}),
            },
            "licenses": [
                {"id": 1, "name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/"}
            ],
            "images": images,
            "annotations": annotations,
            "categories": categories,
        }

        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(coco_json, fh, indent=2)

        self._packages_created += 1
        logger.info(
            "COCOPackager wrote %d images / %d annotations to '%s'",
            len(images),
            len(annotations),
            output_path,
        )
        return os.path.abspath(output_path)

    def get_stats(self) -> dict[str, Any]:
        """Return packaging statistics."""
        return {
            "packager": "COCOPackager",
            "packages_created": self._packages_created,
        }
