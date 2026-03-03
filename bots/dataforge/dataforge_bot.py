"""
bots/dataforge/dataforge_bot.py

DataForgeBot – the central orchestration bot for the DataForge module.

Collects structured data from peer bots, runs the dataset generation
pipeline, and coordinates compliance, user marketplace, and sales-channel
publishing.
"""

import logging
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase
from bots.dataforge.compliance import ComplianceManager
from bots.dataforge.user_marketplace import UserMarketplace
from bots.dataforge.sales_channels import SalesChannelManager
from bots.dataforge.dataset_generators import (
    VoiceDatasetGenerator,
    FacialDatasetGenerator,
    ItemDatasetGenerator,
    BehavioralDatasetGenerator,
    EmotionEngineDatasetGenerator,
)

logger = logging.getLogger(__name__)

# How long the collection loop sleeps between cycles (seconds).
_COLLECTION_INTERVAL: float = 5.0


class DataForgeBot(BotBase):
    """
    Orchestrates the DataForge data-collection and dataset-generation pipeline.

    Responsibilities
    ----------------
    * Collect structured data from registered peer bots via
      ``export_structured_data()``.
    * Validate collected data against compliance rules.
    * Generate synthetic dataset batches using the dataset generators.
    * Coordinate payouts through the user marketplace.
    * Publish finished datasets via the sales-channel manager.
    """

    def __init__(
        self,
        bot_id: str | None = None,
        collection_interval: float = _COLLECTION_INTERVAL,
    ) -> None:
        """
        Initialise DataForgeBot and its sub-components.

        Args:
            bot_id: Optional unique identifier.  A UUID is generated if omitted.
            collection_interval: Seconds to sleep between data-collection cycles.
        """
        super().__init__(
            bot_name="DataForgeBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._collection_interval = collection_interval
        self._registered_bots: dict[str, BotBase] = {}
        self._collected_data: list[dict[str, Any]] = []
        self._generated_datasets: list[dict[str, Any]] = []

        self.compliance = ComplianceManager()
        self.marketplace = UserMarketplace()
        self.sales_channels = SalesChannelManager()

        self._generators: dict[str, Any] = {
            "voice": VoiceDatasetGenerator(),
            "facial": FacialDatasetGenerator(),
            "item": ItemDatasetGenerator(),
            "behavioral": BehavioralDatasetGenerator(),
            "emotion": EmotionEngineDatasetGenerator(),
        }

        self._thread: threading.Thread | None = None
        logger.info("DataForgeBot '%s' created", self.bot_id)

    # ------------------------------------------------------------------
    # Bot registration
    # ------------------------------------------------------------------

    def register_bot(self, bot: BotBase) -> None:
        """
        Register a peer bot whose data will be collected each cycle.

        Args:
            bot: Any :class:`~bots.bot_base.BotBase` subclass instance.
        """
        self._registered_bots[bot.bot_id] = bot
        logger.info("Registered peer bot '%s' (%s)", bot.bot_name, bot.bot_id)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def run(self) -> None:
        """
        Start the data-collection loop in the current thread.

        The loop runs until :meth:`stop` is called.  Each iteration:

        1. Collects structured data from all registered peer bots.
        2. Validates data with :class:`~bots.dataforge.compliance.ComplianceManager`.
        3. Generates one synthetic sample per configured generator type.
        4. Records the cycle in the activity log.
        """
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("DataForgeBot started")
        logger.info("DataForgeBot '%s' entering collection loop", self.bot_id)

        while self.is_running:
            try:
                self._run_collection_cycle()
            except Exception as exc:  # pragma: no cover
                self.handle_error(exc)
            time.sleep(self._collection_interval)

        logger.info("DataForgeBot '%s' collection loop exited", self.bot_id)

    def start_async(self) -> None:
        """
        Start the collection loop in a background daemon thread.

        Use :meth:`stop` to request a graceful shutdown.
        """
        self._thread = threading.Thread(
            target=self.run,
            name=f"DataForgeBot-{self.bot_id}",
            daemon=True,
        )
        self._thread.start()
        logger.info("DataForgeBot '%s' started async", self.bot_id)

    def stop(self) -> None:
        """
        Signal the collection loop to stop and wait for the thread to join.

        If the bot was started synchronously (via :meth:`run`) the caller
        must ensure the loop iteration completes before calling ``stop``.
        """
        self._set_running(False)
        self.log_activity("DataForgeBot stop requested")
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self._collection_interval + 2)
        logger.info("DataForgeBot '%s' stopped", self.bot_id)

    # ------------------------------------------------------------------
    # Collection cycle
    # ------------------------------------------------------------------

    def _run_collection_cycle(self) -> None:
        """Execute a single data-collection and generation cycle."""
        cycle_id = str(uuid.uuid4())[:8]
        logger.debug("Starting collection cycle %s", cycle_id)

        # 1. Collect from peer bots.
        for bot_id, bot in list(self._registered_bots.items()):
            try:
                data = bot.export_structured_data()
                self._collected_data.append(
                    {
                        "cycle_id": cycle_id,
                        "source_bot_id": bot_id,
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                        "payload": data,
                    }
                )
                logger.debug("Collected data from bot '%s'", bot_id)
            except Exception as exc:
                logger.warning("Failed to collect from bot '%s': %s", bot_id, exc)

        # 2. Generate synthetic samples for each dataset type.
        for gen_name, generator in self._generators.items():
            try:
                sample = self._generate_sample(gen_name, generator)
                self._generated_datasets.append(
                    {
                        "cycle_id": cycle_id,
                        "generator": gen_name,
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "sample": sample,
                    }
                )
            except Exception as exc:
                logger.warning(
                    "Generator '%s' failed in cycle %s: %s", gen_name, cycle_id, exc
                )

        self.log_activity(f"Completed collection cycle {cycle_id}")

    def _generate_sample(self, gen_name: str, generator: Any) -> dict:
        """Dispatch sample generation to the appropriate generator."""
        if gen_name == "voice":
            return generator.generate_sample(duration_seconds=2, sample_rate=16000)
        if gen_name == "facial":
            return generator.generate_sample(image_size=(64, 64))
        if gen_name == "behavioral":
            return generator.generate_sample(user_id=str(uuid.uuid4()))
        if gen_name == "emotion":
            return generator.generate_sample(context="neutral")
        # item / default
        return generator.generate_sample(categories=["electronics", "clothing"])

    # ------------------------------------------------------------------
    # Data export
    # ------------------------------------------------------------------

    def export_structured_data(self) -> dict[str, Any]:
        """
        Export comprehensive statistics and collected data for external ingestion.

        Returns:
            A dict containing bot status, compliance info, marketplace stats,
            sales stats, collection counts, and generator metadata.
        """
        base = super().export_structured_data()
        base.update(
            {
                "registered_bots": list(self._registered_bots.keys()),
                "collected_records": len(self._collected_data),
                "generated_dataset_samples": len(self._generated_datasets),
                "compliance_audit_entries": len(self.compliance.audit_log()),
                "marketplace_stats": self.marketplace.get_marketplace_stats(),
                "sales_stats": self.sales_channels.get_sales_stats(),
                "generator_metadata": {
                    name: gen.get_metadata()
                    for name, gen in self._generators.items()
                },
            }
        )
        return base
