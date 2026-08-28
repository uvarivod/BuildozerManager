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

    def test_build_aab_requires_sourcedir_and_wsl(self):
        p = Profile(name="test", wsl_distro="")
        missing = ActionRunner.validate_action(Action.BUILD_AAB, p)
        assert "sourcedir" in missing
        assert "wsl_dir" in missing
        assert "wsl_distro" in missing

    def test_build_aab_valid(self):
        p = Profile(
            name="test",
            sourcedir="/src",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        missing = ActionRunner.validate_action(Action.BUILD_AAB, p)
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

    def test_pull_aab_requires_sourcedir_and_wsl(self):
        p = Profile(name="test", wsl_distro="")
        missing = ActionRunner.validate_action(Action.PULL_AAB, p)
        assert "sourcedir" in missing
        assert "wsl_dir" in missing
        assert "wsl_distro" in missing

    def test_pull_aab_valid(self):
        p = Profile(
            name="test",
            sourcedir="/src",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        missing = ActionRunner.validate_action(Action.PULL_AAB, p)
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

    def test_sign_apk_requires_cert_and_wsl(self):
        p = Profile(name="test", wsl_distro="")
        missing = ActionRunner.validate_action(Action.SIGN_APK, p)
        assert "cert_path" in missing
        assert "cert_password" in missing
        assert "wsl_dir" in missing
        assert "wsl_distro" in missing

    def test_sign_apk_valid(self):
        p = Profile(
            name="test",
            cert_path="/certs/release.keystore",
            cert_password="pass",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        missing = ActionRunner.validate_action(Action.SIGN_APK, p)
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

    def test_sign_apk_missing_fields_fails(self):
        runner = ActionRunner()
        profile = Profile(name="test", wsl_dir="/wsl", wsl_distro="Ubuntu")
        state = runner.run_action(Action.SIGN_APK, profile)
        assert state == ActionState.FAILED

    def test_sign_apk_stops_when_wsl_not_running(self):
        runner = ActionRunner()
        runner._wsl.check_wsl_running = MagicMock(return_value=False)
        profile = Profile(
            name="test",
            cert_path="/certs/release.keystore",
            cert_password="pass",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.SIGN_APK, profile)
        assert state == ActionState.FAILED

    def test_sign_apk_success(self):
        runner = ActionRunner()
        runner._wsl.check_wsl_running = MagicMock(return_value=True)
        runner._wsl.sign_apk = MagicMock(return_value=True)
        profile = Profile(
            name="test",
            cert_path="/certs/release.keystore",
            cert_password="pass",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.SIGN_APK, profile)
        assert state == ActionState.SUCCESS

    def test_sign_apk_failure(self):
        runner = ActionRunner()
        runner._wsl.check_wsl_running = MagicMock(return_value=True)
        runner._wsl.sign_apk = MagicMock(return_value=False)
        profile = Profile(
            name="test",
            cert_path="/certs/release.keystore",
            cert_password="pass",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.SIGN_APK, profile)
        assert state == ActionState.FAILED

    def test_sign_apk_cancelled(self):
        runner = ActionRunner()
        runner._wsl.check_wsl_running = MagicMock(return_value=True)
        def sign_apk(profile, log_cb, cancel_check):
            runner.cancel()
            return True
        runner._wsl.sign_apk = MagicMock(side_effect=sign_apk)
        profile = Profile(
            name="test",
            cert_path="/certs/release.keystore",
            cert_password="pass",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.SIGN_APK, profile)
        assert state == ActionState.CANCELLED

    def test_build_aab_stops_when_wsl_not_running(self):
        runner = ActionRunner()
        runner._wsl.check_wsl_running = MagicMock(return_value=False)
        profile = Profile(
            name="test",
            sourcedir="/src",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.BUILD_AAB, profile)
        assert state == ActionState.FAILED

    def test_build_aab_success_runs_release_command(self):
        runner = ActionRunner()
        runner._wsl.check_wsl_running = MagicMock(return_value=True)
        runner._wsl.find_spec_in_wsl = MagicMock(return_value=True)
        runner._wsl.exec_buildozer = MagicMock(return_value=True)
        profile = Profile(
            name="test",
            sourcedir="/src",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.BUILD_AAB, profile)
        runner._wsl.exec_buildozer.assert_called_once()
        _, kwargs = runner._wsl.exec_buildozer.call_args
        assert kwargs["command"] == "buildozer android release"
        assert state == ActionState.SUCCESS

    def test_build_aab_failure(self):
        runner = ActionRunner()
        runner._wsl.check_wsl_running = MagicMock(return_value=True)
        runner._wsl.find_spec_in_wsl = MagicMock(return_value=True)
        runner._wsl.exec_buildozer = MagicMock(return_value=False)
        profile = Profile(
            name="test",
            sourcedir="/src",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.BUILD_AAB, profile)
        assert state == ActionState.FAILED

    def test_build_aab_cancelled(self):
        runner = ActionRunner()
        runner._wsl.check_wsl_running = MagicMock(return_value=True)

        def exec_buildozer(profile, command, log_callback, cancel_check):
            runner.cancel()
            return True

        runner._wsl.exec_buildozer = MagicMock(side_effect=exec_buildozer)
        profile = Profile(
            name="test",
            sourcedir="/src",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.BUILD_AAB, profile)
        assert state == ActionState.CANCELLED

    def test_pull_aab_stops_when_no_spec(self):
        runner = ActionRunner()
        profile = Profile(
            name="test",
            sourcedir="/nonexistent",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.PULL_AAB, profile)
        assert state == ActionState.FAILED

    def test_pull_aab_stops_when_no_aab_found(self, tmp_path):
        runner = ActionRunner()
        runner._apk.find_latest_aab = MagicMock(return_value=None)
        spec = tmp_path / "buildozer.spec"
        spec.write_text("package.name = myapp\npackage.domain = com.example\n")
        profile = Profile(
            name="test",
            sourcedir=str(tmp_path),
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.PULL_AAB, profile)
        assert state == ActionState.FAILED
        runner._apk.find_latest_aab.assert_called_once()

    def test_pull_aab_success(self, tmp_path):
        runner = ActionRunner()
        wsl_fake = tmp_path / "wsl_aab"
        wsl_fake.mkdir()
        aab_file = wsl_fake / "myapp-1.0-release.aab"
        aab_file.write_text("fake aab")
        runner._apk.find_latest_aab = MagicMock(return_value=aab_file)
        spec = tmp_path / "buildozer.spec"
        spec.write_text("package.name = myapp\npackage.domain = com.example\n")
        profile = Profile(
            name="test",
            sourcedir=str(tmp_path),
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        state = runner.run_action(Action.PULL_AAB, profile)
        assert state == ActionState.SUCCESS
        assert (tmp_path / "bin" / "myapp-1.0-release.aab").is_file()

    def test_pull_aab_handles_copy_exception(self, tmp_path, monkeypatch):
        runner = ActionRunner()
        wsl_fake = tmp_path / "wsl_aab2"
        wsl_fake.mkdir()
        aab_file = wsl_fake / "myapp-1.0-release.aab"
        aab_file.write_text("fake aab")
        runner._apk.find_latest_aab = MagicMock(return_value=aab_file)
        spec = tmp_path / "buildozer.spec"
        spec.write_text("package.name = myapp\npackage.domain = com.example\n")
        profile = Profile(
            name="test",
            sourcedir=str(tmp_path),
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        import shutil
        monkeypatch.setattr(shutil, "copy2", MagicMock(side_effect=OSError("copy failed")))
        state = runner.run_action(Action.PULL_AAB, profile)
        assert state == ActionState.FAILED
