from unittest.mock import MagicMock, patch

import pytest

from src.models.action import Action, ActionState
from src.models.profile import Profile
from src.services.action_runner import ActionRunner


class TestValidateAction:
    def test_sync_src_requires_sourcedir_and_wsl(self):
        p = Profile(name="test", wsl_dir="", wsl_distro="")
        missing = ActionRunner.validate_action(Action.SYNC_SRC, p)
        assert "sourcedir" in missing
        assert "wsl_dir" in missing
        assert "wsl_distro" in missing

    def test_sync_src_valid(self):
        p = Profile(
            name="test", sourcedir="/src", wsl_dir="/wsl", wsl_distro="Ubuntu"
        )
        missing = ActionRunner.validate_action(Action.SYNC_SRC, p)
        assert missing == []

    def test_clean_requires_wsl_dir(self):
        p = Profile(name="test", wsl_dir="", wsl_distro="")
        missing = ActionRunner.validate_action(Action.CLEAN, p)
        assert "wsl_dir" in missing
        assert "wsl_distro" in missing

    def test_clean_valid(self):
        p = Profile(name="test", wsl_dir="/wsl", wsl_distro="Ubuntu")
        missing = ActionRunner.validate_action(Action.CLEAN, p)
        assert missing == []

    def test_build_requires_sourcedir_and_wsl(self):
        p = Profile(name="test")
        missing = ActionRunner.validate_action(Action.BUILD, p)
        assert "sourcedir" in missing
        assert "wsl_dir" in missing
        assert "spec_path" not in missing

    def test_build_valid(self):
        p = Profile(
            name="test",
            sourcedir="/src",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        missing = ActionRunner.validate_action(Action.BUILD, p)
        assert missing == []

    def test_patch_requires_wsl(self):
        p = Profile(name="test", wsl_dir="", wsl_distro="")
        missing = ActionRunner.validate_action(Action.PATCH, p)
        assert "wsl_dir" in missing
        assert "wsl_distro" in missing
        assert "sourcedir" not in missing

    def test_pull_apk_requires_sourcedir_and_wsl(self):
        p = Profile(name="test")
        missing = ActionRunner.validate_action(Action.PULL_APK, p)
        assert "sourcedir" in missing
        assert "wsl_dir" in missing

    def test_pull_apk_valid(self):
        p = Profile(
            name="test",
            sourcedir="/src",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        missing = ActionRunner.validate_action(Action.PULL_APK, p)
        assert missing == []

    def test_run_requires_adb_path(self):
        p = Profile(
            name="test",
            sourcedir="/src",
            spec_path="/sp",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
            adb_path="",
        )
        missing = ActionRunner.validate_action(Action.RUN, p)
        assert "adb_path" in missing

    def test_run_valid(self):
        p = Profile(
            name="test",
            sourcedir="/src",
            spec_path="/sp",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
            adb_path="adb",
        )
        missing = ActionRunner.validate_action(Action.RUN, p)
        assert missing == []

    def test_unknown_action(self):
        p = Profile(name="test")
        missing = ActionRunner.validate_action(None, p)
        assert missing == []


class TestRunAction:
    @patch("src.services.action_runner.APKService")
    @patch("src.services.action_runner.ADBService")
    def test_run_launch_stops_when_no_spec(
        self, mock_adb_cls, mock_apk_cls
    ):
        runner = ActionRunner()
        profile = Profile(
            name="test",
            sourcedir="/src",
            spec_path="/sp",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
            adb_path="adb",
        )
        state = runner.run_action(Action.RUN, profile)
        assert state == ActionState.FAILED

    @patch("src.services.action_runner.APKService")
    @patch("src.services.action_runner.ADBService")
    def test_run_launch_stops_when_no_package_name(
        self, mock_adb_cls, mock_apk_cls
    ):
        mock_apk = mock_apk_cls.return_value
        mock_apk.get_package_name.return_value = ""

        runner = ActionRunner()
        profile = Profile(
            name="test",
            sourcedir="/src",
            spec_path="/sp",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
            adb_path="adb",
        )
        state = runner.run_action(Action.RUN, profile)
        assert state == ActionState.FAILED

    @patch("src.services.action_runner.APKService")
    @patch("src.services.action_runner.ADBService")
    def test_run_launch_stops_when_no_devices(
        self, mock_adb_cls, mock_apk_cls
    ):
        mock_apk = mock_apk_cls.return_value
        mock_apk.get_package_name.return_value = "com.example.app"
        mock_adb = mock_adb_cls.return_value
        mock_adb.list_devices.return_value = ([], "")

        runner = ActionRunner()
        profile = Profile(
            name="test",
            sourcedir="/src",
            spec_path="/sp",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
            adb_path="adb",
        )
        state = runner.run_action(Action.RUN, profile)
        assert state == ActionState.FAILED

    @patch("src.services.action_runner.APKService")
    @patch("src.services.action_runner.ADBService")
    def test_run_launch_stops_when_adb_not_found(
        self, mock_adb_cls, mock_apk_cls
    ):
        mock_apk = mock_apk_cls.return_value
        mock_apk.get_package_name.return_value = "com.example.app"
        mock_adb = mock_adb_cls.return_value
        mock_adb.list_devices.return_value = ([], "ADB not found at: badpath")

        runner = ActionRunner()
        profile = Profile(
            name="test",
            sourcedir="/src",
            spec_path="/sp",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
            adb_path="badpath",
        )
        state = runner.run_action(Action.RUN, profile)
        assert state == ActionState.FAILED

    @patch("src.services.action_runner.APKService")
    @patch("src.services.action_runner.ADBService")
    def test_run_launch_stops_when_no_apk_in_wsl(
        self, mock_adb_cls, mock_apk_cls
    ):
        mock_apk = mock_apk_cls.return_value
        mock_apk.get_package_name.return_value = "com.example.app"
        mock_apk.find_latest_apk.return_value = None
        mock_adb = mock_adb_cls.return_value
        mock_adb.list_devices.return_value = ([{"serial": "x", "state": "device"}], "")

        runner = ActionRunner()
        profile = Profile(
            name="test",
            sourcedir="/src",
            spec_path="/sp",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
            adb_path="adb",
        )
        state = runner.run_action(Action.RUN, profile)
        assert state == ActionState.FAILED

    @patch("src.services.action_runner.APKService")
    @patch("src.services.action_runner.ADBService")
    def test_pull_apk_stops_when_no_spec(
        self, mock_adb_cls, mock_apk_cls
    ):
        runner = ActionRunner()
        profile = Profile(
            name="test",
            sourcedir="/nonexistent",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.PULL_APK, profile)
        assert state == ActionState.FAILED
