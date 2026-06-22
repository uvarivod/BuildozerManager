from unittest.mock import MagicMock, patch

import pytest

from src.models.action import Action, ActionState
from src.models.scenario import Scenario
from src.services.scenario_service import ScenarioService


def _make_scenario(name="test", actions=None, stop_on_failure=True):
    return Scenario(
        name=name,
        action_sequence=actions or [Action.SYNC_SRC, Action.BUILD],
        stop_on_failure=stop_on_failure,
    )


class TestGetPredefinedScenarios:
    def test_returns_two_scenarios(self):
        svc = ScenarioService()
        scenarios = svc.get_predefined_scenarios()
        assert len(scenarios) == 2
        assert scenarios[0].name == "Full Clean build"
        assert scenarios[1].name == "Rebuild"

    def test_full_clean_build_has_correct_actions(self):
        svc = ScenarioService()
        full = svc.get_predefined_scenarios()[0]
        expected = [
            Action.CLEAN,
            Action.SYNC_SRC,
            Action.BUILD,
            Action.PATCH,
            Action.BUILD,
            Action.PULL_APK,
            Action.RUN,
        ]
        assert full.action_sequence == expected
        assert full.stop_on_failure is True

    def test_rebuild_has_correct_actions(self):
        svc = ScenarioService()
        rebuild = svc.get_predefined_scenarios()[1]
        expected = [
            Action.SYNC_SRC,
            Action.BUILD,
            Action.PULL_APK,
            Action.RUN,
        ]
        assert rebuild.action_sequence == expected
        assert rebuild.stop_on_failure is True


class TestRunScenario:
    def test_run_single_action(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        scenario = _make_scenario(actions=[Action.SYNC_SRC])
        result = svc.run_scenario(scenario, None)

        assert result.overall_status == ActionState.SUCCESS
        assert result.per_action_status["SYNC_SRC"] == ActionState.SUCCESS

    def test_run_multiple_actions(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD, Action.PULL_APK])
        result = svc.run_scenario(scenario, None)

        assert result.overall_status == ActionState.SUCCESS
        assert result.per_action_status["SYNC_SRC"] == ActionState.SUCCESS
        assert result.per_action_status["BUILD"] == ActionState.SUCCESS
        assert result.per_action_status["PULL_APK"] == ActionState.SUCCESS

    def test_run_scenario_fails_on_action_failure(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.side_effect = [ActionState.SUCCESS, ActionState.FAILED]

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD], stop_on_failure=True)
        result = svc.run_scenario(scenario, None)

        assert result.overall_status == ActionState.FAILED
        assert result.per_action_status["SYNC_SRC"] == ActionState.SUCCESS
        assert result.per_action_status["BUILD"] == ActionState.FAILED


class TestSkipIndices:
    def test_skip_single_index(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD, Action.PULL_APK])
        result = svc.run_scenario(scenario, None, skip_indices={1})

        assert result.overall_status == ActionState.SUCCESS
        assert result.per_action_status["SYNC_SRC"] == ActionState.SUCCESS
        assert result.per_action_status["BUILD"] == ActionState.SKIPPED
        assert result.per_action_status["PULL_APK"] == ActionState.SUCCESS
        # runner.run_action should only be called for non-skipped actions
        assert svc._runner.run_action.call_count == 2

    def test_skip_multiple_indices(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        scenario = _make_scenario(actions=[Action.CLEAN, Action.SYNC_SRC, Action.BUILD])
        result = svc.run_scenario(scenario, None, skip_indices={0, 2})

        assert result.per_action_status["CLEAN"] == ActionState.SKIPPED
        assert result.per_action_status["SYNC_SRC"] == ActionState.SUCCESS
        assert result.per_action_status["BUILD"] == ActionState.SKIPPED
        assert svc._runner.run_action.call_count == 1

    def test_skip_duplicate_actions_by_index_only(self):
        """With duplicate BUILD actions, skip only the one at specified index."""
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        scenario = _make_scenario(
            actions=[Action.CLEAN, Action.BUILD, Action.PATCH, Action.BUILD, Action.PULL_APK],
        )
        # skip only the second BUILD at index 3
        result = svc.run_scenario(scenario, None, skip_indices={3})

        # per_action_status uses action names as keys, so duplicate BUILD
        # entries collide — the runner call count proves correctness
        assert result.per_action_status["CLEAN"] == ActionState.SUCCESS
        assert result.per_action_status["PATCH"] == ActionState.SUCCESS
        assert result.per_action_status["PULL_APK"] == ActionState.SUCCESS
        # runner.run_action should be called 4 times (indices 0, 1, 2, 4)
        # skipped index 3 is NOT passed to the runner
        assert svc._runner.run_action.call_count == 4

    def test_empty_skip_indices_runs_all(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD])
        result = svc.run_scenario(scenario, None, skip_indices=set())

        assert result.overall_status == ActionState.SUCCESS
        assert svc._runner.run_action.call_count == 2


class TestOnActionStateChange:
    def test_emits_running_before_action(self):
        """on_action_state_change should be called with RUNNING before each action."""
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        calls = []
        def tracker(idx, state):
            calls.append((idx, state))

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD])
        svc.run_scenario(scenario, None, on_action_state_change=tracker)

        # Expect: (0, RUNNING), (0, SUCCESS), (1, RUNNING), (1, SUCCESS)
        assert len(calls) == 4
        assert calls[0] == (0, ActionState.RUNNING)
        assert calls[1] == (0, ActionState.SUCCESS)
        assert calls[2] == (1, ActionState.RUNNING)
        assert calls[3] == (1, ActionState.SUCCESS)

    def test_running_state_before_each_non_skipped_action(self):
        """RUNNING should be emitted before each action that actually runs."""
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        running_indices = []
        def tracker(idx, state):
            if state == ActionState.RUNNING:
                running_indices.append(idx)

        scenario = _make_scenario(
            actions=[Action.CLEAN, Action.BUILD, Action.PATCH, Action.BUILD],
        )
        # skip index 1 (first BUILD) - only 0, 2, 3 should run
        svc.run_scenario(scenario, None, skip_indices={1}, on_action_state_change=tracker)

        assert running_indices == [0, 2, 3]

    def test_skipped_action_emits_skipped_not_running(self):
        """Skipped actions should emit SKIPPED, not RUNNING."""
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        states_for_idx_1 = []
        def tracker(idx, state):
            if idx == 1:
                states_for_idx_1.append(state)

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD, Action.PULL_APK])
        svc.run_scenario(scenario, None, skip_indices={1}, on_action_state_change=tracker)

        assert states_for_idx_1 == [ActionState.SKIPPED]

    def test_cancelled_emits_cancelled(self):
        """Cancel check should emit CANCELLED."""
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        calls = []
        def tracker(idx, state):
            calls.append((idx, state))

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD])
        # cancel before any action starts
        svc.run_scenario(scenario, None, cancel_check=lambda: True, on_action_state_change=tracker)

        assert len(calls) >= 1
        # first call should be CANCELLED with the first action index
        assert any(state == ActionState.CANCELLED for _, state in calls)

    def test_failed_action_does_not_emit_running_for_later_actions(self):
        """On failure with stop_on_failure, should not emit RUNNING for remaining."""
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.side_effect = [ActionState.SUCCESS, ActionState.FAILED]

        running_indices = []
        def tracker(idx, state):
            if state == ActionState.RUNNING:
                running_indices.append(idx)

        scenario = _make_scenario(
            actions=[Action.SYNC_SRC, Action.BUILD, Action.PULL_APK],
            stop_on_failure=True,
        )
        svc.run_scenario(scenario, None, on_action_state_change=tracker)

        # Only index 0 and 1 should have RUNNING (2 never runs)
        assert running_indices == [0, 1]


class TestCancelCheck:
    def test_cancel_before_first_action(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD])
        result = svc.run_scenario(scenario, None, cancel_check=lambda: True)

        assert result.overall_status == ActionState.CANCELLED
        # no actions should have been run
        svc._runner.run_action.assert_not_called()

    def test_cancel_after_some_actions(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        cancel_count = [0]
        def cancel_check():
            cancel_count[0] += 1
            return cancel_count[0] >= 2  # cancel after first action

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD, Action.PULL_APK])
        result = svc.run_scenario(scenario, None, cancel_check=cancel_check)

        # First action should have succeeded, then cancellation stops further runs
        assert result.per_action_status.get("SYNC_SRC") == ActionState.SUCCESS
        assert result.overall_status == ActionState.CANCELLED
        assert svc._runner.run_action.call_count == 1


class TestStopOnFailure:
    def test_stops_on_failure_when_enabled(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.side_effect = [ActionState.SUCCESS, ActionState.FAILED]

        scenario = _make_scenario(
            actions=[Action.SYNC_SRC, Action.BUILD, Action.PULL_APK],
            stop_on_failure=True,
        )
        result = svc.run_scenario(scenario, None)

        assert result.overall_status == ActionState.FAILED
        # Only first 2 actions should have been attempted
        assert svc._runner.run_action.call_count == 2

    def test_continues_on_failure_when_disabled(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.side_effect = [
            ActionState.SUCCESS,
            ActionState.FAILED,
            ActionState.SUCCESS,
        ]

        scenario = _make_scenario(
            actions=[Action.SYNC_SRC, Action.BUILD, Action.PULL_APK],
            stop_on_failure=False,
        )
        result = svc.run_scenario(scenario, None)

        # With stop_on_failure=False, overall_status should reflect mixed results
        assert result.overall_status == ActionState.FAILED
        assert svc._runner.run_action.call_count == 3
        assert result.per_action_status["SYNC_SRC"] == ActionState.SUCCESS
        assert result.per_action_status["BUILD"] == ActionState.FAILED
        assert result.per_action_status["PULL_APK"] == ActionState.SUCCESS


class TestPerActionStatus:
    def test_contains_all_action_names(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        scenario = _make_scenario(
            actions=[Action.CLEAN, Action.SYNC_SRC, Action.BUILD],
        )
        result = svc.run_scenario(scenario, None, skip_indices={0})

        expected_keys = {"CLEAN", "SYNC_SRC", "BUILD"}
        assert set(result.per_action_status.keys()) == expected_keys
        assert result.per_action_status["CLEAN"] == ActionState.SKIPPED
        assert result.per_action_status["SYNC_SRC"] == ActionState.SUCCESS
        assert result.per_action_status["BUILD"] == ActionState.SUCCESS

    def test_overall_success_requires_all_success_or_skipped(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD])
        result = svc.run_scenario(scenario, None, skip_indices={0})

        assert result.overall_status == ActionState.SUCCESS

    def test_overall_failure_if_any_action_fails(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.side_effect = [ActionState.SUCCESS, ActionState.FAILED]

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD])
        result = svc.run_scenario(scenario, None)

        assert result.overall_status == ActionState.FAILED


class TestDuration:
    def test_duration_is_set(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        scenario = _make_scenario(actions=[Action.SYNC_SRC])
        result = svc.run_scenario(scenario, None)

        assert result.duration > 0

    def test_duration_is_tracked_per_scenario(self):
        svc = ScenarioService()
        svc._runner = MagicMock()
        svc._runner.run_action.return_value = ActionState.SUCCESS

        scenario = _make_scenario(actions=[Action.SYNC_SRC, Action.BUILD])
        result = svc.run_scenario(scenario, None)

        assert result.duration >= 0
        assert isinstance(result.duration, float)
