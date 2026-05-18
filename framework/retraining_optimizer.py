class RetrainingOptimizer:
    """Simple retraining policy helper for workflow health reports."""

    def __init__(self, threshold: float = 0.05) -> None:
        self.threshold = max(0.0, float(threshold))

    def _drift_ratio(self, baseline_score: float, current_score: float) -> float:
        baseline = float(baseline_score)
        current = float(current_score)
        if baseline <= 0:
            return 0.0
        return max(0.0, (baseline - current) / baseline)

    def should_retrain(self, baseline_score: float, current_score: float) -> bool:
        return self._drift_ratio(baseline_score, current_score) >= self.threshold

    def select_retraining_method(self, baseline_score: float, current_score: float) -> str:
        drift_ratio = self._drift_ratio(baseline_score, current_score)
        if drift_ratio < self.threshold:
            return "no_retraining"
        if drift_ratio >= self.threshold * 2:
            return "full_retraining"
        return "incremental_tuning"
