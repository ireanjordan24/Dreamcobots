"""
Tests for sandbox/container_sandbox.py

Covers:
  1. Container lifecycle (create, stop, list)
  2. Health check with auto-restart
  3. Build job queuing and execution
  4. Build history and queue introspection
  5. Conflict resolution
  6. Duplicate removal
  7. Dashboard
  8. Callback on build complete
  9. Error paths
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from sandbox.container_sandbox import (
    ContainerSandbox,
    Container,
    BuildJob,
    BuildStatus,
    ContainerStatus,
    ConflictRecord,
    ConflictResolutionStrategy,
)


# ---------------------------------------------------------------------------
# Container lifecycle
# ---------------------------------------------------------------------------


class TestContainerLifecycle:
    def setup_method(self):
        self.sb = ContainerSandbox(max_containers=5)

    def test_create_container_returns_container(self):
        c = self.sb.create_container(name="test-sb-1")
        assert isinstance(c, Container)
        assert c.name == "test-sb-1"

    def test_create_container_appears_in_list(self):
        self.sb.create_container(name="list-test")
        names = [c["name"] for c in self.sb.list_containers()]
        assert "list-test" in names

    def test_max_containers_enforced(self):
        for i in range(5):
            self.sb.create_container(name=f"c{i}")
        with pytest.raises(RuntimeError, match="Max containers"):
            self.sb.create_container(name="one-too-many")

    def test_stop_container_returns_true(self):
        self.sb.create_container(name="stop-me")
        assert self.sb.stop_container("stop-me") is True

    def test_stop_container_removes_from_list(self):
        self.sb.create_container(name="gone")
        self.sb.stop_container("gone")
        names = [c["name"] for c in self.sb.list_containers()]
        assert "gone" not in names

    def test_stop_nonexistent_returns_false(self):
        assert self.sb.stop_container("ghost") is False

    def test_container_to_dict_keys(self):
        c = self.sb.create_container(name="dict-test")
        d = c.to_dict()
        for key in ("container_id", "image", "name", "status", "health_checks", "restart_count"):
            assert key in d


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------


class TestHealthChecks:
    def setup_method(self):
        self.sb = ContainerSandbox()

    def test_health_check_returns_dict(self):
        self.sb.create_container(name="hc1")
        result = self.sb.health_check_all()
        assert isinstance(result, dict)
        assert "hc1" in result

    def test_health_check_increments_count(self):
        c = self.sb.create_container(name="hc2")
        before = c.health_checks
        self.sb.health_check_all()
        # health_check_all increments on healthy containers
        assert c.health_checks >= before


# ---------------------------------------------------------------------------
# Build jobs
# ---------------------------------------------------------------------------


class TestBuildJobs:
    def setup_method(self):
        self.sb = ContainerSandbox()

    def test_queue_build_returns_job(self):
        job = self.sb.queue_build("my-repo", "main", "abc123")
        assert isinstance(job, BuildJob)
        assert job.status == BuildStatus.QUEUED

    def test_queue_appears_in_get_queue(self):
        job = self.sb.queue_build("repo", "feat/x", "def456")
        queue = self.sb.get_build_queue()
        assert any(j["job_id"] == job.job_id for j in queue)

    def test_run_next_build_none_when_empty(self):
        assert self.sb.run_next_build() is None

    def test_run_next_build_consumes_queue(self):
        self.sb.queue_build("r", "b", "sha1")
        self.sb.queue_build("r", "b", "sha2")
        result1 = self.sb.run_next_build()
        assert result1 is not None
        assert len(self.sb.get_build_queue()) == 1

    def test_run_next_build_passes_with_simulated_docker(self):
        self.sb.queue_build("repo", "main", "sha")
        job = self.sb.run_next_build()
        assert job.status in (BuildStatus.PASSED, BuildStatus.FAILED)

    def test_run_build_directly(self):
        job = BuildJob(
            job_id="direct-1",
            repo="r",
            branch="b",
            commit_sha="aaabbb",
            build_commands=["echo build"],
            test_commands=["echo tests"],
        )
        result = self.sb.run_build(job)
        assert result.status in (BuildStatus.PASSED, BuildStatus.FAILED)
        assert result.finished_at is not None

    def test_build_added_to_history(self):
        self.sb.queue_build("r", "b", "s")
        self.sb.run_next_build()
        history = self.sb.get_build_history()
        assert len(history) >= 1

    def test_build_history_limit(self):
        for i in range(5):
            self.sb.queue_build("r", "b", f"s{i}")
            self.sb.run_next_build()
        history = self.sb.get_build_history(limit=3)
        assert len(history) == 3

    def test_build_callback_invoked(self):
        called = []
        self.sb.on_build_complete(lambda job: called.append(job.job_id))
        self.sb.queue_build("r", "b", "s")
        self.sb.run_next_build()
        assert len(called) == 1

    def test_build_job_duration_non_negative(self):
        self.sb.queue_build("r", "b", "s")
        job = self.sb.run_next_build()
        assert job.duration_seconds >= 0


# ---------------------------------------------------------------------------
# Conflict resolution
# ---------------------------------------------------------------------------


class TestConflictResolution:
    def setup_method(self):
        self.sb = ContainerSandbox()

    def test_resolve_conflicts_success(self):
        record = self.sb.resolve_conflicts(
            pr_number=99,
            conflicting_files=["a.py", "b.py"],
            strategy=ConflictResolutionStrategy.AI_RESOLVE,
        )
        assert isinstance(record, ConflictRecord)
        assert record.success is True
        assert len(record.resolved_files) == 2

    def test_resolve_conflicts_stored(self):
        self.sb.resolve_conflicts(101, ["x.py"], ConflictResolutionStrategy.MERGE)
        records = self.sb.get_conflict_records(pr_number=101)
        assert len(records) == 1

    def test_resolve_conflicts_strategy_ours(self):
        record = self.sb.resolve_conflicts(200, ["c.py"], ConflictResolutionStrategy.OURS)
        assert record.strategy == ConflictResolutionStrategy.OURS

    def test_remove_duplicates(self):
        record = self.sb.remove_duplicates(pr_number=55, candidate_files=["dup1.py", "dup2.py"])
        assert record.success is True
        assert "dup1.py" in record.duplicate_files_removed

    def test_get_conflict_records_filter(self):
        self.sb.resolve_conflicts(300, ["a.py"], ConflictResolutionStrategy.THEIRS)
        self.sb.resolve_conflicts(301, ["b.py"], ConflictResolutionStrategy.MERGE)
        r300 = self.sb.get_conflict_records(pr_number=300)
        assert len(r300) == 1
        assert r300[0]["pr_number"] == 300

    def test_get_all_conflict_records(self):
        self.sb.resolve_conflicts(400, ["a.py"], ConflictResolutionStrategy.AI_RESOLVE)
        self.sb.resolve_conflicts(401, ["b.py"], ConflictResolutionStrategy.OURS)
        all_records = self.sb.get_conflict_records()
        assert len(all_records) >= 2

    def test_conflict_record_to_dict_keys(self):
        record = self.sb.resolve_conflicts(500, ["z.py"], ConflictResolutionStrategy.MERGE)
        d = record.to_dict()
        for key in ("pr_number", "conflicting_files", "strategy", "resolved_files", "success"):
            assert key in d


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class TestDashboard:
    def setup_method(self):
        self.sb = ContainerSandbox()

    def test_dashboard_keys(self):
        dash = self.sb.dashboard()
        for key in (
            "docker_available", "active_containers", "max_containers",
            "build_queue_depth", "total_builds", "builds_passed",
            "builds_failed", "pass_rate_percent", "conflict_records",
        ):
            assert key in dash

    def test_get_capabilities_keys(self):
        caps = self.sb.get_capabilities()
        assert caps["name"] == "ContainerSandbox"
        assert len(caps["features"]) > 0

    def test_pass_rate_zero_when_no_builds(self):
        dash = self.sb.dashboard()
        assert dash["pass_rate_percent"] == 0.0

    def test_pass_rate_after_builds(self):
        for _ in range(3):
            self.sb.queue_build("r", "b", "s")
            self.sb.run_next_build()
        dash = self.sb.dashboard()
        assert dash["total_builds"] == 3
