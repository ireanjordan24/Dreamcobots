"""Tests for the state-of-the-art ScienceBot.

Covers all six core research capabilities introduced in
Occupational_bots/science_bot.py:

1. Literature review automation
2. Experiment planning, data analysis, hypothesis validation
3. Collaborative features and version control
4. ML-based pattern recognition
5. Ethical AI (reproducibility and transparency)
6. Modular architecture helpers
"""
from __future__ import annotations

import pytest
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

from Occupational_bots.science_bot import ScienceBot

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def bot():
    return ScienceBot()


@pytest.fixture()
def bot_with_publications(bot):
    """ScienceBot pre-loaded with three publications."""
    pubs = [
        {
            'title': 'Neural correlates of consciousness',
            'authors': ['Smith, A.', 'Jones, B.'],
            'year': 2021,
            'domain': 'Neuroscience',
            'abstract': 'This study examines neural correlates of consciousness.',
            'citation_count': 42,
            'methodology': 'fMRI + EEG',
            'findings': ['Gamma oscillations linked to awareness'],
        },
        {
            'title': 'Deep learning for protein folding',
            'authors': ['Lee, C.'],
            'year': 2022,
            'domain': 'Biology',
            'abstract': 'Deep learning models predict protein folding accurately.',
            'citation_count': 150,
            'methodology': 'Transformer-based neural network',
            'findings': ['AlphaFold-like accuracy achieved'],
        },
        {
            'title': 'Quantum entanglement experiments',
            'authors': ['Park, D.'],
            'year': 2020,
            'domain': 'Physics',
            'abstract': 'Quantum entanglement demonstrated over 100 km fibre.',
            'citation_count': 88,
            'methodology': 'Bell test experiment',
            'findings': ['Non-local correlations verified'],
        },
    ]
    for pub in pubs:
        bot.add_publication(pub)
    return bot


@pytest.fixture()
def bot_with_experiment(bot):
    """ScienceBot with one planned experiment."""
    bot.plan_experiment(
        hypothesis='Increased light exposure improves plant growth.',
        independent_vars=['light_hours'],
        dependent_vars=['plant_height_cm'],
        control_vars=['temperature', 'water'],
        domain='Biology',
    )
    return bot


@pytest.fixture()
def sample_dataset():
    """Twenty numeric observations for analysis tests."""
    return [{'x': float(i), 'y': float(i ** 2), 'label': 'A' if i < 10 else 'B'}
            for i in range(1, 21)]


# ===========================================================================
# 1. LITERATURE REVIEW AUTOMATION
# ===========================================================================

class TestAddPublication:
    def test_returns_pub_id_string(self, bot):
        pid = bot.add_publication({
            'title': 'Test Paper',
            'authors': ['A'],
            'year': 2023,
            'domain': 'Physics',
            'abstract': 'An abstract.',
        })
        assert isinstance(pid, str)
        assert pid.startswith('PUB-')

    def test_missing_field_raises_value_error(self, bot):
        with pytest.raises(ValueError):
            bot.add_publication({'title': 'No authors'})

    def test_duplicate_title_returns_same_id(self, bot):
        data = {
            'title': 'Same Title',
            'authors': ['X'],
            'year': 2020,
            'domain': 'Chemistry',
            'abstract': 'Abstract here.',
        }
        pid1 = bot.add_publication(data)
        pid2 = bot.add_publication(data)
        assert pid1 == pid2


class TestScanPublications:
    def test_returns_list(self, bot_with_publications):
        results = bot_with_publications.scan_publications('neural')
        assert isinstance(results, list)

    def test_relevant_paper_returned(self, bot_with_publications):
        results = bot_with_publications.scan_publications('neural consciousness')
        titles = [r['title'] for r in results]
        assert 'Neural correlates of consciousness' in titles

    def test_domain_filter(self, bot_with_publications):
        results = bot_with_publications.scan_publications('deep learning', domain='Biology')
        assert all(r['domain'] == 'Biology' for r in results)

    def test_invalid_domain_raises(self, bot_with_publications):
        with pytest.raises(ValueError):
            bot_with_publications.scan_publications('test', domain='Astrology')

    def test_max_results_respected(self, bot_with_publications):
        results = bot_with_publications.scan_publications('the', max_results=2)
        assert len(results) <= 2

    def test_results_sorted_by_relevance(self, bot_with_publications):
        results = bot_with_publications.scan_publications('protein folding deep learning')
        if len(results) >= 2:
            assert results[0]['relevance_score'] >= results[1]['relevance_score']

    def test_result_keys(self, bot_with_publications):
        results = bot_with_publications.scan_publications('quantum')
        for r in results:
            assert 'pub_id' in r
            assert 'title' in r
            assert 'relevance_score' in r

    def test_no_match_returns_empty_list(self, bot_with_publications):
        results = bot_with_publications.scan_publications('xyzzy_nonexistent_term_42')
        assert results == []


class TestAnalyzePublication:
    def test_returns_dict(self, bot_with_publications):
        pid = list(bot_with_publications._publications.keys())[0]
        result = bot_with_publications.analyze_publication(pid)
        assert isinstance(result, dict)

    def test_result_has_required_keys(self, bot_with_publications):
        pid = list(bot_with_publications._publications.keys())[0]
        result = bot_with_publications.analyze_publication(pid)
        for key in ('pub_id', 'title', 'methodology', 'key_findings',
                    'citation_count', 'reproducibility_flag'):
            assert key in result

    def test_invalid_id_raises(self, bot):
        with pytest.raises(KeyError):
            bot.analyze_publication('PUB-NONEXISTENT')

    def test_reproducibility_flag_when_methodology_present(self, bot_with_publications):
        pid = list(bot_with_publications._publications.keys())[0]
        result = bot_with_publications.analyze_publication(pid)
        assert result['reproducibility_flag'] is True


class TestSummarizeLiterature:
    def test_returns_dict(self, bot_with_publications):
        result = bot_with_publications.summarize_literature('neural')
        assert isinstance(result, dict)

    def test_required_keys(self, bot_with_publications):
        result = bot_with_publications.summarize_literature('quantum')
        for key in ('topic', 'total_papers', 'date_range',
                    'dominant_domains', 'top_cited', 'consensus_summary'):
            assert key in result

    def test_empty_result_for_no_match(self, bot_with_publications):
        result = bot_with_publications.summarize_literature('xyzzy_42')
        assert result['total_papers'] == 0

    def test_accepts_precomputed_publications(self, bot_with_publications):
        pubs = bot_with_publications.scan_publications('deep learning')
        result = bot_with_publications.summarize_literature('deep learning', publications=pubs)
        assert result['total_papers'] == len(pubs)


# ===========================================================================
# 2. EXPERIMENT PLANNING, DATA ANALYSIS, HYPOTHESIS VALIDATION
# ===========================================================================

class TestPlanExperiment:
    def test_returns_dict(self, bot):
        plan = bot.plan_experiment(
            'H2O freezes at 0°C.',
            independent_vars=['temperature'],
            dependent_vars=['state'],
        )
        assert isinstance(plan, dict)

    def test_experiment_id_assigned(self, bot):
        plan = bot.plan_experiment(
            'Test hypothesis',
            independent_vars=['A'],
            dependent_vars=['B'],
        )
        assert plan['experiment_id'].startswith('EXP-')

    def test_methodology_steps_present(self, bot):
        plan = bot.plan_experiment(
            'Hypothesis',
            independent_vars=['x'],
            dependent_vars=['y'],
        )
        assert isinstance(plan['methodology_steps'], list)
        assert len(plan['methodology_steps']) >= 5

    def test_invalid_domain_raises(self, bot):
        with pytest.raises(ValueError):
            bot.plan_experiment(
                'H', independent_vars=['x'], dependent_vars=['y'], domain='Alchemy'
            )

    def test_empty_independent_vars_raises(self, bot):
        with pytest.raises(ValueError):
            bot.plan_experiment('H', independent_vars=[], dependent_vars=['y'])

    def test_experiment_stored_in_history(self, bot):
        plan = bot.plan_experiment(
            'Stored hypothesis',
            independent_vars=['a'],
            dependent_vars=['b'],
        )
        exp_id = plan['experiment_id']
        assert exp_id in bot._experiments

    def test_ethical_notes_present(self, bot):
        plan = bot.plan_experiment(
            'Ethics check', independent_vars=['x'], dependent_vars=['y']
        )
        assert 'ethical_notes' in plan
        assert plan['ethical_notes']


class TestAnalyzeExperimentalData:
    def test_returns_dict(self, bot, sample_dataset):
        result = bot.analyze_experimental_data(sample_dataset, 'x')
        assert isinstance(result, dict)

    def test_required_keys(self, bot, sample_dataset):
        result = bot.analyze_experimental_data(sample_dataset, 'x')
        for key in ('n', 'mean', 'median', 'stdev', 'min', 'max',
                    'variance', 'outliers', 'summary'):
            assert key in result

    def test_n_equals_dataset_length(self, bot, sample_dataset):
        result = bot.analyze_experimental_data(sample_dataset, 'x')
        assert result['n'] == len(sample_dataset)

    def test_empty_dataset_raises(self, bot):
        with pytest.raises(ValueError):
            bot.analyze_experimental_data([], 'x')

    def test_missing_key_raises(self, bot, sample_dataset):
        with pytest.raises(KeyError):
            bot.analyze_experimental_data(sample_dataset, 'nonexistent_key')

    def test_mean_is_numeric(self, bot, sample_dataset):
        result = bot.analyze_experimental_data(sample_dataset, 'x')
        assert isinstance(result['mean'], float)

    def test_outliers_is_list(self, bot, sample_dataset):
        result = bot.analyze_experimental_data(sample_dataset, 'x')
        assert isinstance(result['outliers'], list)


class TestValidateHypothesis:
    def test_returns_dict(self, bot, sample_dataset):
        analysis = bot.analyze_experimental_data(sample_dataset, 'x')
        result = bot.validate_hypothesis('x is uniformly distributed', analysis)
        assert isinstance(result, dict)

    def test_required_keys(self, bot, sample_dataset):
        analysis = bot.analyze_experimental_data(sample_dataset, 'x')
        result = bot.validate_hypothesis('test', analysis)
        for key in ('hypothesis', 'decision', 'confidence', 'reasoning',
                    'reproducibility_score'):
            assert key in result

    def test_decision_is_valid_string(self, bot, sample_dataset):
        analysis = bot.analyze_experimental_data(sample_dataset, 'x')
        result = bot.validate_hypothesis('test', analysis)
        assert result['decision'] in ('supported', 'not supported')

    def test_confidence_between_0_and_1(self, bot, sample_dataset):
        analysis = bot.analyze_experimental_data(sample_dataset, 'x')
        result = bot.validate_hypothesis('test', analysis)
        assert 0.0 <= result['confidence'] <= 1.0

    def test_reproducibility_score_between_0_and_1(self, bot, sample_dataset):
        analysis = bot.analyze_experimental_data(sample_dataset, 'x')
        result = bot.validate_hypothesis('test', analysis)
        assert 0.0 <= result['reproducibility_score'] <= 1.0


# ===========================================================================
# 3. COLLABORATIVE FEATURES & VERSION CONTROL
# ===========================================================================

class TestCreateResearchTeam:
    def test_returns_dict(self, bot):
        team = bot.create_research_team('Neuro Lab', ['Neuroscience', 'Biology'])
        assert isinstance(team, dict)

    def test_team_id_starts_with_team(self, bot):
        team = bot.create_research_team('Quantum Group', ['Physics'])
        assert team['team_id'].startswith('TEAM-')

    def test_collaborators_empty_initially(self, bot):
        team = bot.create_research_team('Team A', ['Chemistry'])
        assert team['collaborators'] == []

    def test_empty_name_raises(self, bot):
        with pytest.raises(ValueError):
            bot.create_research_team('', ['Biology'])

    def test_empty_disciplines_raises(self, bot):
        with pytest.raises(ValueError):
            bot.create_research_team('Team X', [])

    def test_team_stored_in_bot(self, bot):
        team = bot.create_research_team('Storage Test', ['Ecology'])
        assert team['team_id'] in bot._teams


class TestAddCollaborator:
    def test_returns_updated_team(self, bot):
        team = bot.create_research_team('Lab', ['Physics'])
        updated = bot.add_collaborator(
            team['team_id'], {'name': 'Dr. Smith', 'role': 'Principal Investigator'}
        )
        assert len(updated['collaborators']) == 1

    def test_collaborator_has_joined_at(self, bot):
        team = bot.create_research_team('Lab', ['Chemistry'])
        updated = bot.add_collaborator(
            team['team_id'], {'name': 'Dr. Lee', 'role': 'Analyst'}
        )
        assert 'joined_at' in updated['collaborators'][0]

    def test_invalid_team_raises(self, bot):
        with pytest.raises(KeyError):
            bot.add_collaborator('TEAM-INVALID', {'name': 'X', 'role': 'Y'})

    def test_missing_user_fields_raises(self, bot):
        team = bot.create_research_team('Lab', ['Biology'])
        with pytest.raises(ValueError):
            bot.add_collaborator(team['team_id'], {'name': 'X'})

    def test_multiple_collaborators(self, bot):
        team = bot.create_research_team('Multi', ['Ecology'])
        tid = team['team_id']
        bot.add_collaborator(tid, {'name': 'Alice', 'role': 'Lead'})
        updated = bot.add_collaborator(tid, {'name': 'Bob', 'role': 'Analyst'})
        assert len(updated['collaborators']) == 2


class TestExperimentVersionControl:
    def test_commit_returns_version_record(self, bot_with_experiment):
        exp_id = list(bot_with_experiment._experiments.keys())[0]
        record = bot_with_experiment.commit_experiment_version(
            exp_id,
            {'status': 'running', 'notes': 'Day 3 update'},
            notes='Updated status',
        )
        assert isinstance(record, dict)
        assert record['version'] == 2

    def test_get_experiment_history_returns_list(self, bot_with_experiment):
        exp_id = list(bot_with_experiment._experiments.keys())[0]
        history = bot_with_experiment.get_experiment_history(exp_id)
        assert isinstance(history, list)
        assert len(history) >= 1

    def test_version_increments_on_commit(self, bot_with_experiment):
        exp_id = list(bot_with_experiment._experiments.keys())[0]
        bot_with_experiment.commit_experiment_version(exp_id, {'phase': 2})
        bot_with_experiment.commit_experiment_version(exp_id, {'phase': 3})
        history = bot_with_experiment.get_experiment_history(exp_id)
        versions = [v['version'] for v in history if 'version' in v]
        assert sorted(versions) == versions

    def test_commit_stores_checksum(self, bot_with_experiment):
        exp_id = list(bot_with_experiment._experiments.keys())[0]
        record = bot_with_experiment.commit_experiment_version(exp_id, {'data': 1})
        assert 'checksum' in record
        assert isinstance(record['checksum'], str)

    def test_invalid_experiment_raises_on_commit(self, bot):
        with pytest.raises(KeyError):
            bot.commit_experiment_version('EXP-NONE', {})

    def test_invalid_experiment_raises_on_history(self, bot):
        with pytest.raises(KeyError):
            bot.get_experiment_history('EXP-NONE')

    def test_rollback_returns_data(self, bot_with_experiment):
        exp_id = list(bot_with_experiment._experiments.keys())[0]
        initial = bot_with_experiment.get_experiment_history(exp_id)[0]['data']
        bot_with_experiment.commit_experiment_version(exp_id, {'phase': 'updated'})
        rolled_back = bot_with_experiment.rollback_experiment(exp_id, 1)
        assert rolled_back == initial

    def test_rollback_invalid_version_raises(self, bot_with_experiment):
        exp_id = list(bot_with_experiment._experiments.keys())[0]
        with pytest.raises(ValueError):
            bot_with_experiment.rollback_experiment(exp_id, 999)


# ===========================================================================
# 4. ML-BASED PATTERN RECOGNITION
# ===========================================================================

class TestDetectPatterns:
    def test_returns_dict(self, bot, sample_dataset):
        result = bot.detect_patterns(sample_dataset, ['x', 'y'])
        assert isinstance(result, dict)

    def test_required_keys(self, bot, sample_dataset):
        result = bot.detect_patterns(sample_dataset, ['x', 'y'])
        for key in ('n', 'feature_variances', 'correlations',
                    'high_variance_features', 'pattern_summary'):
            assert key in result

    def test_n_matches_dataset(self, bot, sample_dataset):
        result = bot.detect_patterns(sample_dataset, ['x'])
        assert result['n'] == len(sample_dataset)

    def test_feature_variances_has_all_keys(self, bot, sample_dataset):
        result = bot.detect_patterns(sample_dataset, ['x', 'y'])
        assert 'x' in result['feature_variances']
        assert 'y' in result['feature_variances']

    def test_correlations_present_for_pairs(self, bot, sample_dataset):
        result = bot.detect_patterns(sample_dataset, ['x', 'y'])
        assert 'x_vs_y' in result['correlations']

    def test_empty_dataset_raises(self, bot):
        with pytest.raises(ValueError):
            bot.detect_patterns([], ['x'])

    def test_empty_features_raises(self, bot, sample_dataset):
        with pytest.raises(ValueError):
            bot.detect_patterns(sample_dataset, [])

    def test_missing_feature_key_raises(self, bot, sample_dataset):
        with pytest.raises(KeyError):
            bot.detect_patterns(sample_dataset, ['nonexistent'])


class TestTrainSimpleClassifier:
    def test_returns_dict(self, bot, sample_dataset):
        model = bot.train_simple_classifier(sample_dataset, ['x', 'y'], 'label')
        assert isinstance(model, dict)

    def test_model_id_assigned(self, bot, sample_dataset):
        model = bot.train_simple_classifier(sample_dataset, ['x'], 'label')
        assert model['model_id'].startswith('MODEL-')

    def test_classes_correct(self, bot, sample_dataset):
        model = bot.train_simple_classifier(sample_dataset, ['x'], 'label')
        assert set(model['classes']) == {'A', 'B'}

    def test_training_accuracy_is_float_in_range(self, bot, sample_dataset):
        model = bot.train_simple_classifier(sample_dataset, ['x'], 'label')
        assert 0.0 <= model['training_accuracy'] <= 1.0

    def test_centroids_have_correct_dimensions(self, bot, sample_dataset):
        model = bot.train_simple_classifier(sample_dataset, ['x', 'y'], 'label')
        for label, centroid in model['centroids'].items():
            assert len(centroid) == 2  # 2 feature keys

    def test_empty_training_data_raises(self, bot):
        with pytest.raises(ValueError):
            bot.train_simple_classifier([], ['x'], 'label')


# ===========================================================================
# 5. ETHICAL AI — REPRODUCIBILITY & TRANSPARENCY
# ===========================================================================

class TestGenerateReproducibilityReport:
    def test_returns_dict(self, bot_with_experiment):
        exp_id = list(bot_with_experiment._experiments.keys())[0]
        report = bot_with_experiment.generate_reproducibility_report(exp_id)
        assert isinstance(report, dict)

    def test_required_keys(self, bot_with_experiment):
        exp_id = list(bot_with_experiment._experiments.keys())[0]
        report = bot_with_experiment.generate_reproducibility_report(exp_id)
        for key in ('experiment_id', 'versions', 'checksum_verified',
                    'methodology_documented', 'reproducibility_score',
                    'recommendations'):
            assert key in report

    def test_score_between_0_and_1(self, bot_with_experiment):
        exp_id = list(bot_with_experiment._experiments.keys())[0]
        report = bot_with_experiment.generate_reproducibility_report(exp_id)
        assert 0.0 <= report['reproducibility_score'] <= 1.0

    def test_recommendations_is_list(self, bot_with_experiment):
        exp_id = list(bot_with_experiment._experiments.keys())[0]
        report = bot_with_experiment.generate_reproducibility_report(exp_id)
        assert isinstance(report['recommendations'], list)
        assert len(report['recommendations']) >= 1

    def test_invalid_experiment_raises(self, bot):
        with pytest.raises(KeyError):
            bot.generate_reproducibility_report('EXP-NONE')

    def test_methodology_documented_after_plan(self, bot_with_experiment):
        exp_id = list(bot_with_experiment._experiments.keys())[0]
        report = bot_with_experiment.generate_reproducibility_report(exp_id)
        assert report['methodology_documented'] is True


class TestAuditTransparency:
    def test_returns_dict(self, bot):
        result = bot.audit_transparency()
        assert isinstance(result, dict)

    def test_required_keys(self, bot):
        result = bot.audit_transparency()
        for key in ('total_events', 'event_types', 'recent_events',
                    'principles_covered', 'compliance_summary'):
            assert key in result

    def test_events_increase_after_operations(self, bot):
        initial = bot.audit_transparency()['total_events']
        bot.plan_experiment('H', independent_vars=['x'], dependent_vars=['y'])
        after = bot.audit_transparency()['total_events']
        assert after > initial

    def test_principles_covered_is_list(self, bot):
        result = bot.audit_transparency()
        assert isinstance(result['principles_covered'], list)

    def test_compliance_summary_is_string(self, bot):
        result = bot.audit_transparency()
        assert isinstance(result['compliance_summary'], str)


# ===========================================================================
# 6. MODULAR ARCHITECTURE HELPERS
# ===========================================================================

class TestModularHelpers:
    def test_list_supported_domains_returns_list(self, bot):
        domains = bot.list_supported_domains()
        assert isinstance(domains, list)
        assert len(domains) >= 5

    def test_known_domains_present(self, bot):
        domains = bot.list_supported_domains()
        assert 'Biology' in domains
        assert 'Physics' in domains

    def test_get_ethical_principles_returns_list(self, bot):
        principles = bot.get_ethical_principles()
        assert isinstance(principles, list)
        assert 'transparency' in principles
        assert 'reproducibility' in principles

    def test_get_research_summary_returns_dict(self, bot_with_publications, bot_with_experiment):
        summary = bot_with_publications.get_research_summary()
        assert isinstance(summary, dict)
        for key in ('publications', 'experiments', 'teams', 'audit_events', 'supported_domains'):
            assert key in summary

    def test_research_summary_publication_count(self, bot_with_publications):
        summary = bot_with_publications.get_research_summary()
        assert summary['publications'] == 3

    def test_capabilities_summary_from_base(self, bot):
        caps = bot.capabilities_summary()
        assert caps['features'] == 100
        assert caps['functions'] == 100
        assert caps['tools'] == 100

    def test_list_features_returns_100_items(self, bot):
        assert len(bot.list_features()) == 100

    def test_list_functions_returns_100_items(self, bot):
        assert len(bot.list_functions()) == 100

    def test_list_tools_returns_100_items(self, bot):
        assert len(bot.list_tools()) == 100
