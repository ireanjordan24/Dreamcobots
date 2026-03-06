"""
tests/test_buddy_bot.py – Unit tests for BuddyAI residual income modules.
"""

import datetime
import sys
import os

# Ensure the repo root is on the path so BuddyAI is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from BuddyAI.config import load_config
from BuddyAI.event_bus import EventBus
from BuddyAI.income_tracker import (
    IncomeRecord,
    IncomeTracker,
    YouTubeAdapter,
    BlogAdapter,
    BooksAdapter,
    SaaSAdapter,
    AdsAdapter,
    AffiliatesAdapter,
    AppsAdapter,
)
from BuddyAI.dashboard import Dashboard
from BuddyAI.content_automation import ContentAutomation
from BuddyAI.market_analysis import MarketAnalysis, TrendScanner
from BuddyAI.ml_optimizer import (
    IncomePredictor,
    OptimizationEngine,
    _simple_linear_regression,
    _r_squared,
)
from BuddyAI.buddy_bot import BuddyBot


# ── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def cfg():
    return load_config()


@pytest.fixture
def bus():
    return EventBus()


@pytest.fixture
def tracker(cfg, bus):
    return IncomeTracker(cfg, bus)


@pytest.fixture
def dashboard(cfg, bus):
    return Dashboard(cfg, bus)


@pytest.fixture
def content_automation(cfg, bus):
    return ContentAutomation(cfg, bus)


@pytest.fixture
def market_analysis(cfg, bus):
    return MarketAnalysis(cfg, bus)


@pytest.fixture
def predictor(cfg):
    return IncomePredictor(cfg)


@pytest.fixture
def optimizer(cfg, bus):
    return OptimizationEngine(cfg, bus)


# ── config ─────────────────────────────────────────────────────────────────


class TestConfig:
    def test_load_config_returns_dict(self, cfg):
        assert isinstance(cfg, dict)

    def test_default_keys_present(self, cfg):
        for key in ("buddy_bot_name", "log_level", "report_format"):
            assert key in cfg

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("BUDDYAI_BUDDY_BOT_NAME", "TestBot")
        c = load_config()
        assert c["buddy_bot_name"] == "TestBot"


# ── event_bus ──────────────────────────────────────────────────────────────


class TestEventBus:
    def test_subscribe_and_publish(self, bus):
        received = []
        bus.subscribe("test.event", received.append)
        bus.publish("test.event", {"key": "value"})
        assert received == [{"key": "value"}]

    def test_multiple_subscribers(self, bus):
        log = []
        bus.subscribe("e", lambda d: log.append("a"))
        bus.subscribe("e", lambda d: log.append("b"))
        bus.publish("e", None)
        assert log == ["a", "b"]

    def test_unsubscribe(self, bus):
        log = []
        handler = log.append
        bus.subscribe("e", handler)
        bus.unsubscribe("e", handler)
        bus.publish("e", 1)
        assert log == []

    def test_unsubscribe_unknown_handler_does_not_raise(self, bus):
        bus.unsubscribe("nonexistent", lambda x: None)  # should not raise

    def test_handler_exception_does_not_propagate(self, bus):
        def bad_handler(data):
            raise RuntimeError("oops")

        bus.subscribe("boom", bad_handler)
        bus.publish("boom", None)  # should not raise

    def test_events_lists_subscribed(self, bus):
        bus.subscribe("alpha", lambda d: None)
        assert "alpha" in bus.events()

    def test_no_subscribers_publish_silently(self, bus):
        bus.publish("ghost.event", "data")  # should not raise


# ── income_tracker ─────────────────────────────────────────────────────────


class TestIncomeRecord:
    def test_to_dict_keys(self):
        r = IncomeRecord("YouTube", revenue=100.0, traffic=5000, engagement=3.5)
        d = r.to_dict()
        assert set(d.keys()) == {
            "source", "date", "revenue", "traffic", "engagement", "currency"
        }

    def test_default_date_is_today(self):
        r = IncomeRecord("Blog", revenue=50.0)
        assert r.date == datetime.date.today()

    def test_repr(self):
        r = IncomeRecord("SaaS", revenue=999.0, traffic=100)
        assert "SaaS" in repr(r)


class TestAdapters:
    @pytest.mark.parametrize("AdapterClass", [
        YouTubeAdapter, BlogAdapter, BooksAdapter,
        SaaSAdapter, AdsAdapter, AffiliatesAdapter, AppsAdapter,
    ])
    def test_fetch_returns_income_record(self, cfg, AdapterClass):
        adapter = AdapterClass(cfg)
        record = adapter.fetch()
        assert isinstance(record, IncomeRecord)
        assert record.revenue >= 0
        assert record.traffic >= 0
        assert record.source == adapter.name


class TestIncomeTracker:
    def test_collect_all_returns_records(self, tracker):
        records = tracker.collect_all()
        assert len(records) == 7  # one per default adapter

    def test_summarize_total_revenue(self, tracker):
        records = tracker.collect_all()
        summary = tracker.summarize(records)
        expected_total = sum(r.revenue for r in records)
        assert abs(summary["total_revenue"] - round(expected_total, 2)) < 0.01

    def test_summarize_keys(self, tracker):
        records = tracker.collect_all()
        summary = tracker.summarize(records)
        for key in ("total_revenue", "total_traffic", "source_count", "top_source"):
            assert key in summary

    def test_summarize_empty_returns_empty(self, tracker):
        assert tracker.summarize([]) == {}

    def test_history_accumulates(self, tracker):
        tracker.collect_all()
        tracker.collect_all()
        assert len(tracker.history()) == 14  # 2 × 7

    def test_event_published_on_collect(self, cfg):
        bus = EventBus()
        collected_events = []
        bus.subscribe("income.collected", collected_events.append)
        tracker = IncomeTracker(cfg, bus)
        tracker.collect_all()
        assert len(collected_events) == 1

    def test_event_published_on_summarize(self, cfg):
        bus = EventBus()
        summary_events = []
        bus.subscribe("income.summarized", summary_events.append)
        tracker = IncomeTracker(cfg, bus)
        records = tracker.collect_all()
        tracker.summarize(records)
        assert len(summary_events) == 1


# ── dashboard ──────────────────────────────────────────────────────────────


class TestDashboard:
    def test_render_returns_string(self, dashboard, tracker):
        records = tracker.collect_all()
        summary = tracker.summarize(records)
        report = dashboard.render(records, summary)
        assert isinstance(report, str)
        assert "Revenue" in report

    def test_save_report_creates_file(self, dashboard, tracker, tmp_path, cfg):
        dashboard.output_dir = str(tmp_path)
        records = tracker.collect_all()
        summary = tracker.summarize(records)
        path = dashboard.save_report(summary, filename="test_report.json")
        assert os.path.isfile(path)

    def test_print_summary_does_not_raise(self, dashboard, tracker, capsys):
        records = tracker.collect_all()
        summary = tracker.summarize(records)
        dashboard.print_summary(summary)
        captured = capsys.readouterr()
        assert "Revenue" in captured.out


# ── content_automation ─────────────────────────────────────────────────────


class TestContentAutomation:
    def test_generate_blog_post(self, content_automation):
        post = content_automation.generate_blog_post(niche="passive income")
        assert post.title
        assert post.niche == "passive income"
        assert post.word_count > 0
        assert len(post.outline) >= 3

    def test_generate_blog_post_random_niche(self, content_automation):
        post = content_automation.generate_blog_post()
        assert post.niche

    def test_generate_ebook(self, content_automation):
        ebook = content_automation.generate_ebook(niche="investing", chapter_count=5)
        assert ebook.title
        assert len(ebook.chapters) == 5
        assert ebook.estimated_pages > 0

    def test_suggest_saas_ideas(self, content_automation):
        ideas = content_automation.suggest_saas_ideas(count=2)
        assert len(ideas) == 2
        for idea in ideas:
            assert idea.viability_score >= 0
            assert idea.estimated_monthly_revenue >= 0

    def test_generate_video_outline(self, content_automation):
        video = content_automation.generate_video_outline(niche="AI tools")
        assert video.title
        assert video.platform == "YouTube"
        assert len(video.sections) >= 3

    def test_blog_post_event_published(self, cfg):
        bus = EventBus()
        events = []
        bus.subscribe("content.blog_post_created", events.append)
        ca = ContentAutomation(cfg, bus)
        ca.generate_blog_post()
        assert len(events) == 1


# ── market_analysis ────────────────────────────────────────────────────────


class TestTrendScanner:
    def test_scan_returns_signals(self, cfg):
        scanner = TrendScanner(cfg)
        signals = scanner.scan()
        assert len(signals) > 0

    def test_signals_are_sorted_by_score(self, cfg):
        scanner = TrendScanner(cfg)
        signals = scanner.scan()
        scores = [s.opportunity_score for s in signals]
        assert scores == sorted(scores, reverse=True)

    def test_opportunity_score_range(self, cfg):
        scanner = TrendScanner(cfg)
        for signal in scanner.scan():
            assert 0.0 <= signal.opportunity_score <= 10.0


class TestMarketAnalysis:
    def test_run_analysis_returns_report(self, market_analysis):
        report = market_analysis.run_analysis()
        assert report.date
        assert len(report.top_trends) > 0
        assert report.summary

    def test_suggest_new_streams(self, market_analysis):
        report = market_analysis.run_analysis()
        suggestions = market_analysis.suggest_new_streams(report, top_k=2)
        assert len(suggestions) == 2
        for s in suggestions:
            assert "topic" in s
            assert "opportunity_score" in s

    def test_event_published(self, cfg):
        bus = EventBus()
        events = []
        bus.subscribe("market.analysis_complete", events.append)
        ma = MarketAnalysis(cfg, bus)
        ma.run_analysis()
        assert len(events) == 1


# ── ml_optimizer ───────────────────────────────────────────────────────────


class TestSimpleLinearRegression:
    def test_perfect_fit(self):
        x = [0.0, 1.0, 2.0, 3.0]
        y = [1.0, 3.0, 5.0, 7.0]   # y = 2x + 1
        slope, intercept = _simple_linear_regression(x, y)
        assert abs(slope - 2.0) < 1e-9
        assert abs(intercept - 1.0) < 1e-9

    def test_r_squared_perfect(self):
        x = [0.0, 1.0, 2.0, 3.0]
        y = [1.0, 3.0, 5.0, 7.0]
        slope, intercept = _simple_linear_regression(x, y)
        r2 = _r_squared(x, y, slope, intercept)
        assert abs(r2 - 1.0) < 1e-9

    def test_single_point_no_crash(self):
        slope, intercept = _simple_linear_regression([0.0], [5.0])
        assert intercept == 5.0


class TestIncomePredictor:
    def _make_records(self, source: str, n: int = 10) -> list:
        import random
        records = []
        for i in range(n):
            records.append(
                IncomeRecord(
                    source=source,
                    revenue=100.0 + i * 10 + random.uniform(-5, 5),
                    date=datetime.date.today() - datetime.timedelta(days=n - i),
                )
            )
        return records

    def test_train_and_predict(self, predictor):
        records = self._make_records("YouTube", n=10)
        predictor.train(records)
        pred = predictor.predict("YouTube")
        assert pred.predicted_revenue >= 0
        assert 0.0 <= pred.confidence <= 1.0

    def test_predict_unknown_source_fallback(self, predictor):
        pred = predictor.predict("UnknownSource")
        assert pred.predicted_revenue >= 0

    def test_predict_all(self, predictor):
        records = (
            self._make_records("Blog", n=8)
            + self._make_records("SaaS", n=8)
        )
        predictor.train(records)
        preds = predictor.predict_all(["Blog", "SaaS"])
        assert len(preds) == 2


class TestOptimizationEngine:
    def test_optimize_returns_result(self, optimizer):
        result = optimizer.optimize("Test Blog", baseline_score=0.4)
        assert result.best_score >= 0
        assert result.iterations_run == optimizer.iterations
        assert result.status in ("scaled", "testing", "rejected")

    def test_scale_scaled_returns_next_steps(self, optimizer):
        result = optimizer.optimize("High-Score Idea", baseline_score=0.4)
        # Force a known-good result for deterministic test
        result.best_score = 0.8
        result.status = "scaled"
        plan = optimizer.scale(result)
        assert plan["action"] == "scale"
        assert "next_steps" in plan

    def test_scale_rejected(self, optimizer):
        result = optimizer.optimize("Low Idea", baseline_score=0.1)
        result.best_score = 0.2
        result.status = "rejected"
        plan = optimizer.scale(result)
        assert plan["action"] == "reject"


# ── buddy_bot (integration) ────────────────────────────────────────────────


class TestBuddyBot:
    def test_init(self):
        bot = BuddyBot()
        assert bot.income_tracker is not None
        assert bot.dashboard is not None
        assert bot.content_automation is not None
        assert bot.market_analysis is not None
        assert bot.predictor is not None
        assert bot.optimizer is not None

    def test_collect_income(self):
        bot = BuddyBot()
        summary = bot.collect_income()
        assert "total_revenue" in summary

    def test_generate_content_blog(self):
        bot = BuddyBot()
        result = bot.generate_content(content_type="blog")
        assert "blog_post" in result

    def test_generate_content_all(self):
        bot = BuddyBot()
        result = bot.generate_content(content_type="all")
        for key in ("blog_post", "ebook", "saas_ideas", "video_outline"):
            assert key in result

    def test_analyse_market(self):
        bot = BuddyBot()
        report = bot.analyse_market()
        assert "top_trends" in report

    def test_optimise(self):
        bot = BuddyBot()
        plan = bot.optimise("Newsletter Monetisation")
        assert "action" in plan

    def test_run_full_cycle(self):
        bot = BuddyBot()
        results = bot.run_full_cycle()
        for key in (
            "income_summary",
            "predictions",
            "market_report",
            "stream_suggestions",
            "content",
            "optimization",
        ):
            assert key in results
