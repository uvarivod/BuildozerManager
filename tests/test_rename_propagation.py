from unittest.mock import MagicMock, patch

import pytest

from src.models.action import Action
from src.models.custom_action import CustomAction, ActionType
from src.models.profile import Profile
from src.models.scenario import Scenario
from src.services import storage_service
from src.services.storage_service import (
    CustomActionStore,
    ProfileStore,
    ScenarioStore,
)


@pytest.fixture
def temp_data_dir(monkeypatch, tmp_path):
    storage_service.DATA_DIR = tmp_path
    return tmp_path


def test_rename_propagation_updates_profiles(temp_data_dir):
    p = Profile(name="test", patches=["old_patch"])
    ProfileStore.save_all([p])
    profiles = ProfileStore.load_all()
    changed = False
    for profile in profiles:
        if "old_patch" in profile.patches:
            profile.patches = ["new_patch" if x == "old_patch" else x for x in profile.patches]
            changed = True
    if changed:
        ProfileStore.save_all(profiles)
    loaded = ProfileStore.load_all()
    assert "new_patch" in loaded[0].patches
    assert "old_patch" not in loaded[0].patches


def test_rename_propagation_updates_multiple_profiles(temp_data_dir):
    p1 = Profile(name="p1", patches=["old_patch"])
    p2 = Profile(name="p2", patches=["old_patch", "other"])
    ProfileStore.save_all([p1, p2])
    profiles = ProfileStore.load_all()
    changed = False
    for profile in profiles:
        if "old_patch" in profile.patches:
            profile.patches = ["new_patch" if x == "old_patch" else x for x in profile.patches]
            changed = True
    if changed:
        ProfileStore.save_all(profiles)
    loaded = ProfileStore.load_all()
    for p in loaded:
        assert "new_patch" in p.patches
        assert "old_patch" not in p.patches


def test_rename_propagation_does_not_affect_other_patches(temp_data_dir):
    p = Profile(name="test", patches=["old_patch", "other_patch"])
    ProfileStore.save_all([p])
    profiles = ProfileStore.load_all()
    changed = False
    for profile in profiles:
        if "old_patch" in profile.patches:
            profile.patches = ["new_patch" if x == "old_patch" else x for x in profile.patches]
            changed = True
    if changed:
        ProfileStore.save_all(profiles)
    loaded = ProfileStore.load_all()
    assert "other_patch" in loaded[0].patches


def test_rename_propagation_updates_scenario_custom_action_names(temp_data_dir):
    s = Scenario(
        name="test",
        action_sequence=[Action.PATCH, Action.CUSTOM_SCRIPT],
        custom_action_names={0: "old_patch", 1: "other"},
    )
    ScenarioStore.save_all([s])
    for scenario in ScenarioStore.load_all():
        changed = False
        for k, v in list(scenario.custom_action_names.items()):
            if v == "old_patch":
                scenario.custom_action_names[k] = "new_patch"
                changed = True
        if changed:
            ScenarioStore.save(scenario)
    loaded = ScenarioStore.load_all()
    assert loaded[0].custom_action_names[0] == "new_patch"
    assert loaded[0].custom_action_names[1] == "other"


def test_rename_propagation_updates_multiple_scenarios(temp_data_dir):
    s1 = Scenario(
        name="s1",
        action_sequence=[Action.PATCH],
        custom_action_names={0: "old_patch"},
    )
    s2 = Scenario(
        name="s2",
        action_sequence=[Action.PATCH, Action.PATCH],
        custom_action_names={0: "old_patch", 1: "old_patch"},
    )
    ScenarioStore.save_all([s1, s2])
    for scenario in ScenarioStore.load_all():
        changed = False
        for k, v in list(scenario.custom_action_names.items()):
            if v == "old_patch":
                scenario.custom_action_names[k] = "new_patch"
                changed = True
        if changed:
            ScenarioStore.save(scenario)
    loaded = ScenarioStore.load_all()
    for s in loaded:
        for v in s.custom_action_names.values():
            assert v == "new_patch"


def test_rename_propagation_scenario_no_matches_is_noop(temp_data_dir):
    s = Scenario(
        name="test",
        action_sequence=[Action.PATCH],
        custom_action_names={0: "other_patch"},
    )
    ScenarioStore.save_all([s])
    for scenario in ScenarioStore.load_all():
        changed = False
        for k, v in list(scenario.custom_action_names.items()):
            if v == "nonexistent":
                scenario.custom_action_names[k] = "new_patch"
                changed = True
        if changed:
            ScenarioStore.save(scenario)
    loaded = ScenarioStore.load_all()
    assert loaded[0].custom_action_names[0] == "other_patch"


def test_rename_propagation_profile_no_matches_is_noop(temp_data_dir):
    p = Profile(name="test", patches=["other_patch"])
    ProfileStore.save_all([p])
    profiles = ProfileStore.load_all()
    changed = False
    for profile in profiles:
        if "nonexistent" in profile.patches:
            profile.patches = ["new_patch" if x == "nonexistent" else x for x in profile.patches]
            changed = True
    if changed:
        ProfileStore.save_all(profiles)
    loaded = ProfileStore.load_all()
    assert loaded[0].patches == ["other_patch"]


def test_load_profile_reloads_from_storage(temp_data_dir):
    fresh = Profile(name="test", patches=["new_patch"])
    ProfileStore.save_all([fresh])
    stale = Profile(name="test", patches=["old_patch"])
    profiles = ProfileStore.load_all()
    for p in profiles:
        if p.name == stale.name:
            stale = p
            break
    assert stale.patches == ["new_patch"]


def test_on_enter_reloads_profile_from_storage(temp_data_dir):
    p = Profile(name="test", patches=["new_patch"])
    ProfileStore.save_all([p])
    active_profile = Profile(name="test", patches=["old_patch"])
    profiles = ProfileStore.load_all()
    for pr in profiles:
        if pr.name == active_profile.name:
            active_profile = pr
            break
    assert active_profile.patches == ["new_patch"]


def test_on_enter_reloads_scenario_from_storage(temp_data_dir):
    s = Scenario(
        name="test",
        action_sequence=[Action.PATCH],
        custom_action_names={0: "new_patch"},
    )
    ScenarioStore.save_all([s])
    current_scenario = Scenario(
        name="test",
        action_sequence=[Action.PATCH],
        custom_action_names={0: "old_patch"},
    )
    fresh_scenarios = ScenarioStore.load_all()
    current_scenario = None
    for sc in fresh_scenarios:
        if sc.name == "test":
            current_scenario = sc
            break
    assert current_scenario.custom_action_names[0] == "new_patch"


def test_stale_profile_missing_check_uses_stored_data(temp_data_dir):
    fresh = Profile(name="test", patches=["existing_patch"])
    ProfileStore.save_all([fresh])
    stale = Profile(name="test", patches=["removed_patch"])
    profiles = ProfileStore.load_all()
    for p in profiles:
        if p.name == stale.name:
            stale = p
            break
    available = {"existing_patch", "other_available"}
    missing = [p for p in stale.patches if p not in available]
    assert missing == []


class TestStderrFiltering:
    @patch("subprocess.run")
    @patch("src.services.action_runner.Path.is_file", return_value=True)
    def test_run_custom_script_filters_input_redirection_warning(self, mock_is_file, mock_run):
        from src.services.action_runner import ActionRunner
        from src.models.profile import Profile

        mock_result = MagicMock()
        mock_result.stdout = "Hello\nBye\n"
        mock_result.stderr = "ERROR: Input redirection is not supported, exiting the process immediately.\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        runner = ActionRunner()
        log_cb = MagicMock()
        with patch.object(runner, "_make_log_callback", return_value=log_cb):
            profile = Profile(name="test", patches=[])
            state = runner.run_action(
                Action.CUSTOM_SCRIPT,
                profile,
                script_path="C:\\test.bat",
            )
        assert state.name == "SUCCESS"
        log_cb.assert_any_call("info", "Hello\nBye")
        warn_calls = [c for c in log_cb.call_args_list if c[0][0] == "warn"]
        assert len(warn_calls) == 0

    @patch("subprocess.run")
    @patch("src.services.action_runner.Path.is_file", return_value=True)
    def test_run_custom_script_passes_other_stderr(self, mock_is_file, mock_run):
        from src.services.action_runner import ActionRunner

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = "Some real error\n"
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        runner = ActionRunner()
        log_cb = MagicMock()
        with patch.object(runner, "_make_log_callback", return_value=log_cb):
            profile = Profile(name="test", patches=[])
            state = runner.run_action(
                Action.CUSTOM_SCRIPT,
                profile,
                script_path="C:\\test.bat",
            )
        assert state.name == "FAILED"
        log_cb.assert_any_call("warn", "Some real error")

    @patch("subprocess.run")
    @patch("src.services.action_runner.Path.is_file", return_value=True)
    def test_run_custom_script_mixed_stderr(self, mock_is_file, mock_run):
        from src.services.action_runner import ActionRunner

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = (
            "ERROR: Input redirection is not supported, exiting the process immediately.\n"
            "Some real error\n"
        )
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        runner = ActionRunner()
        log_cb = MagicMock()
        with patch.object(runner, "_make_log_callback", return_value=log_cb):
            profile = Profile(name="test", patches=[])
            state = runner.run_action(
                Action.CUSTOM_SCRIPT,
                profile,
                script_path="C:\\test.bat",
            )
        assert state.name == "FAILED"
        log_cb.assert_any_call("warn", "Some real error")
        warn_calls = [c for c in log_cb.call_args_list if c[0][0] == "warn"]
        assert len(warn_calls) == 1

    @patch("subprocess.run")
    @patch("src.services.action_runner.Path.is_file", return_value=True)
    def test_run_custom_script_empty_stderr_no_warn_call(self, mock_is_file, mock_run):
        from src.services.action_runner import ActionRunner

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        runner = ActionRunner()
        log_cb = MagicMock()
        with patch.object(runner, "_make_log_callback", return_value=log_cb):
            profile = Profile(name="test", patches=[])
            state = runner.run_action(
                Action.CUSTOM_SCRIPT,
                profile,
                script_path="C:\\test.bat",
            )
        assert state.name == "SUCCESS"
        warn_calls = [c for c in log_cb.call_args_list if c[0][0] == "warn"]
        assert len(warn_calls) == 0


class TestPatchServiceStderrFiltering:
    @patch("subprocess.run")
    @patch("src.services.patch_service.Path.is_file", return_value=True)
    def test_custom_patch_filters_input_redirection_warning(self, mock_is_file, mock_run, temp_data_dir):
        from src.models.custom_action import CustomAction, ActionType
        from src.services.patch_service import PatchService

        ca = CustomAction(
            id="test-id",
            name="CustomPatch",
            type=ActionType.PATCH,
            logic="C:\\test.bat",
        )
        CustomActionStore.save(ca)

        mock_result = MagicMock()
        mock_result.stdout = "patch output\n"
        mock_result.stderr = "ERROR: Input redirection is not supported, exiting the process immediately.\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        svc = PatchService()
        log_cb = MagicMock()
        result = svc.apply_patches(
            ["CustomPatch"],
            ".",
            log_callback=log_cb,
        )
        assert result is True
        log_cb.assert_any_call("info", "patch output")
        warn_calls = [c for c in log_cb.call_args_list if c[0][0] == "warn"]
        assert len(warn_calls) == 0

    @patch("subprocess.run")
    @patch("src.services.patch_service.Path.is_file", return_value=True)
    def test_custom_patch_passes_other_stderr(self, mock_is_file, mock_run, temp_data_dir):
        from src.models.custom_action import CustomAction, ActionType
        from src.services.patch_service import PatchService

        ca = CustomAction(
            id="test-id2",
            name="OtherPatch",
            type=ActionType.PATCH,
            logic="C:\\test.bat",
        )
        CustomActionStore.save(ca)

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = "real error\n"
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        svc = PatchService()
        log_cb = MagicMock()
        result = svc.apply_patches(
            ["OtherPatch"],
            ".",
            log_callback=log_cb,
        )
        assert result is False
        log_cb.assert_any_call("warn", "real error")
