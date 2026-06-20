import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.adb_service import ADBService


@pytest.fixture
def service():
    return ADBService()


@pytest.fixture
def mock_log():
    return MagicMock()


class TestInstallApk:
    def test_install_apk_missing_file(self, service, mock_log):
        result = service.install_apk("adb", "/nonexistent/apk.apk", log_callback=mock_log)
        assert not result
        mock_log.assert_any_call("error", "APK not found: /nonexistent/apk.apk")

    @patch("src.services.adb_service.ADBService._run_adb")
    def test_install_apk_success(self, mock_run_adb, service, mock_log, tmp_path):
        apk_path = str(tmp_path / "test.apk")
        Path(apk_path).write_text("fake apk")
        mock_run_adb.return_value = subprocess.CompletedProcess([], 0, stdout="Success\n", stderr="")

        result = service.install_apk("adb", apk_path, log_callback=mock_log)
        assert result
        mock_run_adb.assert_called_once()
        assert mock_run_adb.call_args[0][1] == ["install", "-r", apk_path]

    @patch("src.services.adb_service.ADBService._run_adb")
    def test_install_apk_with_device_serial(self, mock_run_adb, service, mock_log, tmp_path):
        apk_path = str(tmp_path / "test.apk")
        Path(apk_path).write_text("fake apk")
        mock_run_adb.return_value = subprocess.CompletedProcess([], 0, stdout="Success\n", stderr="")

        result = service.install_apk("adb", apk_path, log_callback=mock_log, device_serial="123456")
        assert result
        assert mock_run_adb.call_args[0][1] == ["-s", "123456", "install", "-r", apk_path]

    @patch("src.services.adb_service.ADBService._run_adb")
    def test_install_apk_failure(self, mock_run_adb, service, mock_log, tmp_path):
        apk_path = str(tmp_path / "test.apk")
        Path(apk_path).write_text("fake apk")
        mock_run_adb.return_value = subprocess.CompletedProcess([], 0, stdout="Failure [INSTALL_FAILED]\n", stderr="")

        result = service.install_apk("adb", apk_path, log_callback=mock_log)
        assert not result


class TestListDevices:
    @patch("src.services.adb_service.ADBService._run_adb")
    def test_list_devices_returns_empty_when_no_devices(self, mock_run_adb, service):
        mock_run_adb.return_value = subprocess.CompletedProcess([], 0, stdout="List of devices attached\n\n", stderr="")
        devices, err = service.list_devices("adb")
        assert devices == []
        assert err == ""

    @patch("src.services.adb_service.ADBService._run_adb")
    def test_list_devices_parses_device_line(self, mock_run_adb, service):
        mock_run_adb.return_value = subprocess.CompletedProcess(
            [], 0, stdout="List of devices attached\n7c77d769\tdevice\n", stderr=""
        )
        devices, err = service.list_devices("adb")
        assert len(devices) == 1
        assert devices[0]["serial"] == "7c77d769"
        assert devices[0]["state"] == "device"
        assert err == ""

    @patch("src.services.adb_service.ADBService._run_adb")
    def test_list_devices_parses_space_separated(self, mock_run_adb, service):
        mock_run_adb.return_value = subprocess.CompletedProcess(
            [], 0, stdout="List of devices attached\n7c77d769 device\n", stderr=""
        )
        devices, err = service.list_devices("adb")
        assert len(devices) == 1
        assert devices[0]["serial"] == "7c77d769"

    @patch("src.services.adb_service.ADBService._run_adb")
    def test_list_devices_handles_file_not_found(self, mock_run_adb, service):
        mock_run_adb.side_effect = FileNotFoundError
        devices, err = service.list_devices("adb")
        assert devices == []
        assert "not found" in err

    @patch("src.services.adb_service.ADBService._run_adb")
    def test_list_devices_handles_nonzero_exit(self, mock_run_adb, service):
        mock_run_adb.return_value = subprocess.CompletedProcess([], 1, stdout="", stderr="error")
        devices, err = service.list_devices("adb")
        assert devices == []
        assert "exit code" in err

    @patch("src.services.adb_service.ADBService._run_adb")
    def test_list_devices_handles_timeout(self, mock_run_adb, service):
        mock_run_adb.side_effect = subprocess.TimeoutExpired("cmd", 10)
        devices, err = service.list_devices("adb")
        assert devices == []
        assert "timed out" in err


class TestLaunchApp:
    @patch("src.services.adb_service.ADBService._run_adb")
    def test_launch_app_monkey(self, mock_run_adb, service, mock_log):
        mock_run_adb.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        result = service.launch_app("adb", "com.example.app", log_callback=mock_log)
        assert result
        assert mock_run_adb.call_args[0][1] == [
            "shell", "monkey", "-p", "com.example.app",
            "-c", "android.intent.category.LAUNCHER", "1",
        ]

    @patch("src.services.adb_service.ADBService._run_adb")
    def test_launch_app_with_activity(self, mock_run_adb, service, mock_log):
        mock_run_adb.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        result = service.launch_app("adb", "com.example.app", activity=".MainActivity", log_callback=mock_log)
        assert result
        assert mock_run_adb.call_args[0][1] == [
            "shell", "am", "start", "-n", "com.example.app/.MainActivity",
        ]

    @patch("src.services.adb_service.ADBService._run_adb")
    def test_launch_app_with_device_serial(self, mock_run_adb, service, mock_log):
        mock_run_adb.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        result = service.launch_app("adb", "com.example.app", log_callback=mock_log, device_serial="123456")
        assert result
        assert mock_run_adb.call_args[0][1] == [
            "-s", "123456", "shell", "monkey", "-p", "com.example.app",
            "-c", "android.intent.category.LAUNCHER", "1",
        ]

    @patch("src.services.adb_service.ADBService._run_adb")
    def test_launch_app_failure(self, mock_run_adb, service, mock_log):
        mock_run_adb.side_effect = subprocess.TimeoutExpired("cmd", 30)
        result = service.launch_app("adb", "com.example.app", log_callback=mock_log)
        assert not result
