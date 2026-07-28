from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def panel():
    from src.screens.log_panel import LogPanel
    p = LogPanel()
    return p


class TestSaveLog:
    def test_empty_content_returns_early(self, panel):
        with patch.object(panel._log_service, "get_plain_text", return_value="") as mock_get:
            with patch("src.screens.log_panel.show_form_dialog") as mock_form:
                panel.save_log()
        mock_get.assert_called_once()
        mock_form.assert_not_called()

    def test_shows_form_dialog_with_content(self, panel):
        panel._log_service = MagicMock()
        panel._log_service.get_plain_text.return_value = "some log content"

        with patch("src.screens.log_panel.show_form_dialog") as mock_form:
            panel.save_log()

        mock_form.assert_called_once()
        _, kwargs = mock_form.call_args
        assert kwargs["title"] == "Save Log"
        assert kwargs["fields"] == ["Filename"]
        assert kwargs["save_text"] == "Save"
        assert kwargs["cancel_text"] == "Cancel"

    def test_on_save_creates_file(self, panel, tmp_path):
        panel._log_service = MagicMock()
        panel._log_service.get_plain_text.return_value = "test content"
        log_file = str(tmp_path / "export.log")

        with patch("src.screens.log_panel.show_form_dialog") as mock_form:
            panel.save_log()

        on_save = mock_form.call_args[1]["on_save"]
        on_save({"Filename": log_file})

        assert (tmp_path / "export.log").exists()
        content = (tmp_path / "export.log").read_text(encoding="utf-8")
        assert content == "test content"

    def test_on_save_empty_filename_returns_early(self, panel):
        panel._log_service = MagicMock()
        panel._log_service.get_plain_text.return_value = "content"

        with patch("src.screens.log_panel.show_form_dialog") as mock_form:
            panel.save_log()

        on_save = mock_form.call_args[1]["on_save"]
        with patch("builtins.open") as mock_open:
            on_save({"Filename": ""})
            mock_open.assert_not_called()

    def test_on_save_appends_log_extension(self, panel, tmp_path):
        panel._log_service = MagicMock()
        panel._log_service.get_plain_text.return_value = "content"
        log_file = str(tmp_path / "export")

        with patch("src.screens.log_panel.show_form_dialog") as mock_form:
            panel.save_log()

        on_save = mock_form.call_args[1]["on_save"]
        on_save({"Filename": log_file})

        assert (tmp_path / "export.log").exists()

    def test_on_save_preserves_existing_log_extension(self, panel, tmp_path):
        panel._log_service = MagicMock()
        panel._log_service.get_plain_text.return_value = "content"
        log_file = str(tmp_path / "export.txt")

        with patch("src.screens.log_panel.show_form_dialog") as mock_form:
            panel.save_log()

        on_save = mock_form.call_args[1]["on_save"]
        on_save({"Filename": log_file})

        assert (tmp_path / "export.txt.log").exists()


class TestShowHelp:
    def test_shows_help_popup(self, panel):
        with patch("src.screens.log_panel.show_help_popup") as mock_help:
            panel.show_help()
        mock_help.assert_called_once()
        assert mock_help.call_args[0][0] == "Log Panel Help"
