"""Auto-Scaler Bot — automatically clones profitable bots into new niches."""

from .auto_scaler_bot import AutoScalerBot, AutoScalerError, BotMetrics, CloneRecord

__all__ = ["AutoScalerBot", "BotMetrics", "CloneRecord", "AutoScalerError"]
