"""
bots/dataforge/dataset_generators/item_dataset.py

ItemDatasetGenerator – generates simulated product/item catalog dataset samples.
"""

import logging
import os
import random
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_CATEGORIES = [
    "electronics",
    "clothing",
    "furniture",
    "books",
    "toys",
    "sports",
    "food",
    "beauty",
    "automotive",
    "tools",
]

_CONDITIONS = ["new", "like_new", "good", "fair", "poor"]
_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD"]


class ItemDatasetGenerator:
    """
    Generates simulated product/item catalog dataset samples.

    Each sample represents a single product listing with attributes
    such as name, category, price, description, and availability.
    """

    def __init__(self) -> None:
        """Initialise the generator."""
        self._sample_count = 0
        self._batch_count = 0
        logger.info("ItemDatasetGenerator initialised")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_sample(
        self,
        categories: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Generate a single simulated product/item sample.

        Args:
            categories: Optional list of category strings to choose from.
                        Falls back to the built-in category list if not provided.

        Returns:
            A dict representing a product listing.
        """
        cats = categories if categories else _DEFAULT_CATEGORIES
        category = random.choice(cats)
        price = round(random.uniform(0.99, 9999.99), 2)
        rating = round(random.uniform(1.0, 5.0), 1)
        review_count = random.randint(0, 5000)

        self._sample_count += 1
        sample_id = str(uuid.uuid4())

        sample: dict[str, Any] = {
            "item_id": sample_id,
            "name": f"Simulated {category.title()} Item {sample_id[:8]}",
            "category": category,
            "subcategory": f"{category}_sub_{random.randint(1, 10)}",
            "price": price,
            "currency": random.choice(_CURRENCIES),
            "condition": random.choice(_CONDITIONS),
            "in_stock": random.choice([True, False]),
            "stock_quantity": random.randint(0, 1000),
            "rating": rating,
            "review_count": review_count,
            "brand": f"Brand_{random.randint(1, 50)}",
            "sku": f"SKU-{uuid.uuid4().hex[:10].upper()}",
            "weight_kg": round(random.uniform(0.1, 50.0), 3),
            "dimensions_cm": {
                "length": round(random.uniform(1.0, 200.0), 1),
                "width": round(random.uniform(1.0, 100.0), 1),
                "height": round(random.uniform(0.5, 50.0), 1),
            },
            "tags": random.sample(
                ["sale", "new_arrival", "bestseller", "clearance", "featured", "eco"],
                k=random.randint(0, 3),
            ),
            "description": (
                f"A high-quality {category} item with excellent features. "
                "Suitable for everyday use. Comes with a 1-year warranty."
            ),
            "image_urls": [
                f"https://cdn.example.com/items/{sample_id}/{i}.jpg"
                for i in range(random.randint(1, 5))
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        logger.debug("Generated item sample %s (category=%s)", sample_id, category)
        return sample

    def generate_batch(
        self,
        num_samples: int,
        output_dir: str = "/tmp/item_dataset",
    ) -> list[dict[str, Any]]:
        """
        Generate a batch of item samples.

        Args:
            num_samples: Number of samples to generate.
            output_dir: Directory path (created if necessary; no files written).

        Returns:
            A list of sample dicts.
        """
        os.makedirs(output_dir, exist_ok=True)
        batch = [
            self.generate_sample(categories=_DEFAULT_CATEGORIES)
            for _ in range(num_samples)
        ]
        self._batch_count += 1
        logger.info(
            "Item batch %d complete: %d samples in %s",
            self._batch_count,
            num_samples,
            output_dir,
        )
        return batch

    def validate_sample(self, sample: dict) -> bool:
        """
        Validate an item sample dict.

        Args:
            sample: Sample produced by :meth:`generate_sample`.

        Returns:
            ``True`` if valid, ``False`` otherwise.
        """
        required = {"item_id", "name", "category", "price", "currency"}
        if not required.issubset(sample.keys()):
            logger.warning("Item sample missing required keys")
            return False
        if not isinstance(sample["price"], (int, float)) or sample["price"] < 0:
            logger.warning("Item sample has invalid price: %s", sample["price"])
            return False
        return True

    def get_metadata(self) -> dict[str, Any]:
        """
        Return metadata describing this generator.

        Returns:
            A metadata dict.
        """
        return {
            "generator": "ItemDatasetGenerator",
            "version": "1.0.0",
            "default_categories": _DEFAULT_CATEGORIES,
            "conditions": _CONDITIONS,
            "currencies": _CURRENCIES,
            "samples_generated": self._sample_count,
            "batches_generated": self._batch_count,
            "description": "Simulated product/item catalog entries",
        }
