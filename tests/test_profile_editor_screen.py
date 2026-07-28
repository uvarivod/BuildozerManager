from unittest.mock import MagicMock, patch

import pytest

from src.models.profile import Profile


@pytest.fixture
def screen():
    from src.screens.profile_editor_screen import ProfileEditorScreen
    s = ProfileEditorScreen()
    s.name_input = MagicMock()
    s.sourcedir_input = MagicMock()
    s.spec_path_input = MagicMock()
    s.adb_path_input = MagicMock()
    s.wsl_dir_input = MagicMock()
    s.wsl_distro_input = MagicMock()
    s.excluded_files_input = MagicMock()
    s.patches_container = MagicMock()
    s.manager = MagicMock()
    return s


# ---------------------------------------------------------------------------
# save()
# ---------------------------------------------------------------------------

class TestSave:
    def test_empty_name_shows_error(self, screen):
        screen.name_input.text = ""
        with patch("src.screens.profile_editor_screen.show_error_dialog") as mock_show_error:
            with patch("src.screens.profile_editor_screen.ProfileStore"):
                screen.save()
        mock_show_error.assert_called_once_with("Cannot Save", "Profile name cannot be empty.")

    def test_new_profile_duplicate_name_shows_error(self, screen):
        screen.name_input.text = "existing"
        screen._editing_profile = None
        existing_profile = Profile(name="existing")
        with patch("src.screens.profile_editor_screen.show_error_dialog") as mock_show_error:
            with patch("src.screens.profile_editor_screen.ProfileStore") as mock_store:
                mock_store.load_all.return_value = [existing_profile]
                screen.save()
        mock_show_error.assert_called_once()
        assert "already exists" in mock_show_error.call_args[0][1]

    def test_editing_duplicate_name_shows_error(self, screen):
        screen.name_input.text = "new_name"
        screen._editing_profile = Profile(name="old_name")
        screen._orig_name = "old_name"
        existing_profile = Profile(name="new_name")
        with patch("src.screens.profile_editor_screen.show_error_dialog") as mock_show_error:
            with patch("src.screens.profile_editor_screen.ProfileStore") as mock_store:
                mock_store.load_all.return_value = [existing_profile]
                screen.save()
        mock_show_error.assert_called_once()
        assert "already exists" in mock_show_error.call_args[0][1]

    def test_new_profile_valid_saves(self, screen):
        screen.name_input.text = "new-profile"
        screen.sourcedir_input.text = "/src"
        screen.spec_path_input.text = "/spec"
        screen.adb_path_input.text = "adb"
        screen.wsl_dir_input.text = ""
        screen.wsl_distro_input.text = ""
        screen.excluded_files_input.text = ""
        screen._editing_profile = None
        screen._patch_checkboxes = {}

        with patch("src.screens.profile_editor_screen.ProfileStore") as mock_store:
            with patch("src.screens.profile_editor_screen.SettingsStore") as mock_settings:
                with patch("src.screens.profile_editor_screen.show_error_dialog") as mock_show_error:
                    mock_store.load_all.return_value = []
                    screen.save()

        mock_show_error.assert_not_called()
        mock_store.save_all.assert_called_once()
        mock_settings.save.assert_called_once_with({"last_profile": "new-profile"})

    def test_valid_save_navigates_to_actions(self, screen):
        screen.name_input.text = "valid"
        screen.sourcedir_input.text = ""
        screen._editing_profile = None
        screen._patch_checkboxes = {}

        with patch("src.screens.profile_editor_screen.ProfileStore") as mock_store:
            with patch("src.screens.profile_editor_screen.SettingsStore"):
                mock_store.load_all.return_value = []
                screen.save()

        assert screen.manager.current == "actions"

    def test_editing_same_name_no_error(self, screen):
        screen.name_input.text = "my-profile"
        screen._editing_profile = Profile(name="my-profile")
        screen._orig_name = "my-profile"
        screen.sourcedir_input.text = ""
        screen._patch_checkboxes = {}
        existing = Profile(name="my-profile")

        with patch("src.screens.profile_editor_screen.ProfileStore") as mock_store:
            with patch("src.screens.profile_editor_screen.SettingsStore"):
                with patch("src.screens.profile_editor_screen.show_error_dialog") as mock_show_error:
                    mock_store.load_all.return_value = [existing]
                    screen.save()

        mock_show_error.assert_not_called()

    def test_profile_name_stripped(self, screen):
        screen.name_input.text = "  spaced-name  "
        screen.sourcedir_input.text = ""
        screen._editing_profile = None
        screen._patch_checkboxes = {}

        with patch("src.screens.profile_editor_screen.ProfileStore") as mock_store:
            with patch("src.screens.profile_editor_screen.SettingsStore"):
                mock_store.load_all.return_value = []
                screen.save()

        saved_profile = mock_store.save_all.call_args[0][0][0]
        assert saved_profile.name == "spaced-name"


# ---------------------------------------------------------------------------
# load_profile()
# ---------------------------------------------------------------------------

class TestLoadProfile:
    def test_missing_patches_shows_info_dialog(self, screen):
        missing_patch_name = "missing-patch"
        profile = Profile(name="test", patches=[missing_patch_name])

        with patch("src.screens.profile_editor_screen.PatchRegistry") as mock_registry:
            mock_registry.list_patches.return_value = []
            with patch("src.screens.profile_editor_screen.CustomActionStore") as mock_ca_store:
                mock_ca_store.load_all.return_value = []
                with patch("src.screens.profile_editor_screen.ProfileStore") as mock_store:
                    mock_store.load_all.return_value = [profile]
                    with patch("src.screens.profile_editor_screen.show_info_dialog") as mock_info:
                        screen.load_profile(profile)

        mock_info.assert_called_once()
        title, msg = mock_info.call_args[1]["title"], mock_info.call_args[1]["message"]
        assert title == "Missing Patches"
        assert missing_patch_name in msg

    def test_no_missing_patches_no_dialog(self, screen):
        profile = Profile(name="test", patches=["available-patch"])

        with patch("src.screens.profile_editor_screen.PatchRegistry") as mock_registry:
            available_mock = MagicMock()
            available_mock.name = "available-patch"
            available_mock.description = ""
            mock_registry.list_patches.return_value = [available_mock]
            with patch("src.screens.profile_editor_screen.CustomActionStore") as mock_ca_store:
                mock_ca_store.load_all.return_value = []
                with patch("src.screens.profile_editor_screen.ProfileStore") as mock_store:
                    mock_store.load_all.return_value = [profile]
                    with patch("src.screens.profile_editor_screen.show_info_dialog") as mock_info:
                        screen.load_profile(profile)

        mock_info.assert_not_called()

    def test_no_patches_no_dialog(self, screen):
        profile = Profile(name="test", patches=[])

        with patch("src.screens.profile_editor_screen.ProfileStore") as mock_store:
            mock_store.load_all.return_value = [profile]
            with patch("src.screens.profile_editor_screen.show_info_dialog") as mock_info:
                screen.load_profile(profile)

        mock_info.assert_not_called()

    def test_load_sets_editing_profile(self, screen):
        profile = Profile(name="test", patches=[])
        with patch("src.screens.profile_editor_screen.ProfileStore") as mock_store:
            mock_store.load_all.return_value = [profile]
            screen.load_profile(profile)

        assert screen._editing_profile is not None
        assert screen._editing_profile.name == "test"

    def test_load_populates_widgets(self, screen):
        profile = Profile(
            name="test", sourcedir="/src", spec_path="/spec",
            adb_path="adb", wsl_dir="/wsl", wsl_distro="Ubuntu",
            excluded_files=["a", "b"], patches=[],
            delete_exclusions=["del_a"],
        )
        with patch("src.screens.profile_editor_screen.ProfileStore") as mock_store:
            mock_store.load_all.return_value = [profile]
            screen.load_profile(profile)

        assert screen.name_input.text == "test"
        assert screen.sourcedir_input.text == "/src"
        assert screen.spec_path_input.text == "/spec"
        assert screen.adb_path_input.text == "adb"
        assert screen.wsl_dir_input.text == "/wsl"
        assert screen.wsl_distro_input.text == "Ubuntu"
        assert screen.excluded_files_input.text == "a, b"


# ---------------------------------------------------------------------------
# _check_adb()
# ---------------------------------------------------------------------------

class TestCheckAdb:
    def test_empty_path_shows_error(self, screen):
        screen.adb_path_input.text = ""
        with patch("src.screens.profile_editor_screen.show_error_dialog") as mock_error:
            screen._check_adb()
        mock_error.assert_called_once_with("ADB Check", "No ADB path configured.")

    @patch("src.screens.profile_editor_screen.subprocess.run")
    def test_valid_path_runs_subprocess(self, mock_run, screen):
        screen.adb_path_input.text = "C:\\adb.exe"
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Android Debug Bridge version 1.0.41"
        mock_run.return_value = mock_result

        screen._check_adb()

        mock_run.assert_called_once_with(
            ["C:\\adb.exe", "version"],
            capture_output=True, text=True, timeout=10
        )

    @patch("src.screens.profile_editor_screen.subprocess.run")
    def test_success_shows_popup_with_output(self, mock_run, screen, kivy_mocks):
        screen.adb_path_input.text = "adb"
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ADB version 1.0"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        screen._check_adb()

        kivy_mocks["Popup"].assert_called()
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["title"] == "ADB Check"

    @patch("src.screens.profile_editor_screen.subprocess.run")
    def test_failure_shows_popup_with_stderr(self, mock_run, screen, kivy_mocks):
        screen.adb_path_input.text = "adb"
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error: device not found"
        mock_run.return_value = mock_result

        screen._check_adb()

        kivy_mocks["Popup"].assert_called()

    @patch("src.screens.profile_editor_screen.subprocess.run")
    def test_file_not_found_shows_popup(self, mock_run, screen, kivy_mocks):
        screen.adb_path_input.text = "/invalid/adb"
        mock_run.side_effect = FileNotFoundError

        screen._check_adb()

        kivy_mocks["Popup"].assert_called()

    @patch("src.screens.profile_editor_screen.subprocess.run")
    def test_timeout_shows_popup(self, mock_run, screen, kivy_mocks):
        screen.adb_path_input.text = "adb"
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("adb", 10)

        screen._check_adb()

        kivy_mocks["Popup"].assert_called()

    @patch("src.screens.profile_editor_screen.subprocess.run")
    def test_popup_contains_textinput(self, mock_run, screen, kivy_mocks):
        screen.adb_path_input.text = "adb"
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "works"
        mock_run.return_value = mock_result

        screen._check_adb()

        assert kivy_mocks["TextInput"].called

    @patch("src.screens.profile_editor_screen.subprocess.run")
    def test_popup_size(self, mock_run, screen, kivy_mocks):
        screen.adb_path_input.text = "adb"
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "ok"
        mock_run.return_value = mock_result

        screen._check_adb()

        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs.get("size_hint") == (0.6, 0.4)


# ---------------------------------------------------------------------------
# _prompt_use_spec()
# ---------------------------------------------------------------------------

class TestPromptUseSpec:
    def test_shows_confirm_dialog(self, screen):
        with patch("src.screens.profile_editor_screen.show_confirm_dialog") as mock_confirm:
            screen._prompt_use_spec("/path/buildozer.spec")

        mock_confirm.assert_called_once()
        _, kwargs = mock_confirm.call_args
        assert kwargs["title"] == "buildozer.spec Found"
        assert kwargs["confirm_text"] == "Yes"
        assert kwargs["cancel_text"] == "No"

    def test_on_yes_sets_spec_path(self, screen):
        screen.spec_path_input.text = ""
        with patch("src.screens.profile_editor_screen.show_confirm_dialog") as mock_confirm:
            screen._prompt_use_spec("/path/buildozer.spec")
            on_confirm = mock_confirm.call_args[1]["on_confirm"]
            on_confirm()

        assert screen.spec_path_input.text == "/path/buildozer.spec"


# ---------------------------------------------------------------------------
# cancel()
# ---------------------------------------------------------------------------

class TestCancel:
    def test_goes_to_actions(self, screen):
        screen.cancel()
        assert screen.manager.current == "actions"

    def test_no_manager_no_error(self, screen):
        screen.manager = None
        screen.cancel()


# ---------------------------------------------------------------------------
# show_help()
# ---------------------------------------------------------------------------

class TestShowHelp:
    def test_shows_help_popup(self, screen):
        with patch("src.screens.profile_editor_screen.show_help_popup") as mock_help:
            screen.show_help()
        mock_help.assert_called_once()
        assert mock_help.call_args[0][0] == "Profile Editor Help"


# ---------------------------------------------------------------------------
# clear_fields()
# ---------------------------------------------------------------------------

class TestClearFields:
    def test_clears_all_fields(self, screen):
        screen.name_input.text = "old"
        screen.sourcedir_input.text = "/old"
        screen.spec_path_input.text = "/old"
        screen.adb_path_input.text = "adb"
        screen.wsl_dir_input.text = "/old"
        screen.wsl_distro_input.text = "Ubuntu"
        screen.excluded_files_input.text = "a, b"
        screen.clear_fields()

        assert screen.name_input.text == ""
        assert screen.sourcedir_input.text == ""
        assert screen.spec_path_input.text == ""
        assert screen.adb_path_input.text == "adb"
        assert screen.wsl_dir_input.text == ""
        assert screen.wsl_distro_input.text == "Ubuntu-22.04"
        assert screen.excluded_files_input.text == ""

    def test_resets_editing_profile(self, screen):
        screen._editing_profile = Profile(name="test")
        screen.clear_fields()
        assert screen._editing_profile is None
