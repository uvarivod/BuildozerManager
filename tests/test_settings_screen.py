from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def screen():
    from src.screens.settings_screen import SettingsScreen
    s = SettingsScreen()
    s.log_dir_input = MagicMock()
    s.max_log_size_input = MagicMock()
    s.manager = MagicMock()
    return s


class TestSave:
    def test_empty_dir_shows_error(self, screen):
        screen.log_dir_input.text = ""
        screen.max_log_size_input.text = "100"
        with patch("src.screens.settings_screen.show_error_dialog") as mock_error:
            screen.save()
        mock_error.assert_called_once_with("Error", "Log directory path cannot be empty.")

    def test_invalid_max_size_shows_error(self, screen):
        screen.log_dir_input.text = "logs"
        screen.max_log_size_input.text = "not_a_number"
        with patch("src.screens.settings_screen.show_error_dialog") as mock_error:
            screen.save()
        mock_error.assert_called_once_with("Error", "Max log size must be a valid number.")

    def test_zero_max_size_shows_error(self, screen):
        screen.log_dir_input.text = "logs"
        screen.max_log_size_input.text = "0"
        with patch("src.screens.settings_screen.show_error_dialog") as mock_error:
            screen.save()
        mock_error.assert_called_once_with("Error", "Max log size must be a positive number.")

    def test_negative_max_size_shows_error(self, screen):
        screen.log_dir_input.text = "logs"
        screen.max_log_size_input.text = "-5"
        with patch("src.screens.settings_screen.show_error_dialog") as mock_error:
            screen.save()
        mock_error.assert_called_once_with("Error", "Max log size must be a positive number.")

    def test_oserror_on_mkdir_shows_error(self, screen):
        screen.log_dir_input.text = "/invalid/path"
        screen.max_log_size_input.text = "100"
        with patch("src.screens.settings_screen.Path") as mock_path:
            mock_path.return_value.mkdir.side_effect = OSError("Permission denied")
            with patch("src.screens.settings_screen.show_error_dialog") as mock_error:
                screen.save()
        mock_error.assert_called_once()
        assert "Permission denied" in mock_error.call_args[0][1]

    def test_valid_save_saves_settings(self, screen):
        screen.log_dir_input.text = "logs"
        screen.max_log_size_input.text = "200"
        with patch("src.screens.settings_screen.show_error_dialog") as mock_error:
            with patch("src.screens.settings_screen.SettingsStore") as mock_store:
                with patch("src.screens.settings_screen.show_toast") as mock_toast:
                    screen.save()
        mock_error.assert_not_called()
        mock_store.save.assert_called_once_with({"log_dir": "logs", "max_log_size_mb": 200})
        mock_toast.assert_called_once_with("Settings saved successfully.")

    def test_default_max_size_used_when_empty(self, screen):
        screen.log_dir_input.text = "logs"
        screen.max_log_size_input.text = ""
        with patch("src.screens.settings_screen.SettingsStore") as mock_store:
            with patch("src.screens.settings_screen.show_toast"):
                screen.save()
        saved = mock_store.save.call_args[0][0]
        assert saved["max_log_size_mb"] == 100

    def test_trims_input_values(self, screen):
        screen.log_dir_input.text = "  logs  "
        screen.max_log_size_input.text = "  50  "
        with patch("src.screens.settings_screen.SettingsStore") as mock_store:
            with patch("src.screens.settings_screen.show_toast"):
                screen.save()
        saved = mock_store.save.call_args[0][0]
        assert saved["log_dir"] == "logs"
        assert saved["max_log_size_mb"] == 50


class TestOnBack:
    def test_navigates_to_actions(self, screen):
        screen.on_back()
        assert screen.manager.current == "actions"

    def test_no_manager_no_error(self, screen):
        screen.manager = None
        screen.on_back()


class TestShowHelp:
    def test_shows_help_popup(self, screen):
        with patch("src.screens.settings_screen.show_help_popup") as mock_help:
            screen.show_help()
        mock_help.assert_called_once()
        assert mock_help.call_args[0][0] == "Settings Help"
