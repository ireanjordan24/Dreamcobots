from framework.retraining_optimizer import RetrainingOptimizer


def test_should_retrain_when_drift_exceeds_threshold():
    optimizer = RetrainingOptimizer(threshold=0.05)
    assert optimizer.should_retrain(0.92, 0.84) is True


def test_select_retraining_method_levels():
    optimizer = RetrainingOptimizer(threshold=0.05)
    assert optimizer.select_retraining_method(0.92, 0.90) == "no_retraining"
    assert optimizer.select_retraining_method(0.92, 0.86) == "incremental_tuning"
    assert optimizer.select_retraining_method(0.92, 0.80) == "full_retraining"
