from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def screen():
    from src.screens.actions_screen import ActionsScreen
    s = ActionsScreen()
    s.manager = MagicMock()
    return s


class TestDeleteProfile:
    def test_no_active_profile_returns_early(self, screen):
        screen._active_profile = None
        with patch("src.screens.actions_screen.show_confirm_dialog") as mock_confirm:
            screen.delete_profile()
        mock_confirm.assert_not_called()

    def test_shows_confirm_dialog(self, screen):
        screen._active_profile = MagicMock()
        screen._active_profile.name = "test-profile"
        with patch("src.screens.actions_screen.show_confirm_dialog") as mock_confirm:
            screen.delete_profile()
        mock_confirm.assert_called_once()
        _, kwargs = mock_confirm.call_args
        assert kwargs["title"] == "Confirm"
        assert "test-profile" in kwargs["message"]
        assert kwargs["confirm_text"] == "Delete"

    def test_confirm_calls_delete(self, screen):
        screen._active_profile = MagicMock()
        screen._active_profile.name = "test-profile"
        with patch("src.screens.actions_screen.show_confirm_dialog") as mock_confirm:
            screen.delete_profile()
            on_confirm = mock_confirm.call_args[1]["on_confirm"]
            with patch.object(screen, "_confirm_delete") as mock_delete:
                on_confirm()
                mock_delete.assert_called_once()

    def test_confirm_delete_removes_profile(self, screen):
        screen._active_profile = MagicMock()
        screen._active_profile.name = "test-profile"
        screen.profile_spinner = MagicMock()
        with patch("src.screens.actions_screen.ProfileStore") as mock_store:
            screen._confirm_delete()
        mock_store.delete.assert_called_once_with("test-profile")
        assert screen._active_profile is None
        assert screen.status_label == "No profile selected"


class TestOnScenarioSelected:
    def test_empty_text_clears_scenario(self, screen):
        screen.on_scenario_selected("")
        assert screen._current_scenario is None

    def test_select_text_clears_scenario(self, screen):
        screen.on_scenario_selected("Select scenario")
        assert screen._current_scenario is None

    def test_scenario_not_found_does_nothing(self, screen):
        screen._scenarios = []
        screen.on_scenario_selected("nonexistent")

    def test_missing_actions_shows_error(self, screen):
        scenario = MagicMock()
        scenario.name = "test-scenario"
        scenario.custom_action_names = {0: "missing-action"}
        scenario.action_sequence = []
        screen._scenarios = [scenario]
        screen._active_profile = MagicMock()

        with patch("src.screens.actions_screen.CustomActionStore") as mock_ca_store:
            mock_ca_store.load_all.return_value = []
            with patch("src.screens.actions_screen.show_error_dialog") as mock_error:
                screen.on_scenario_selected("test-scenario")

        mock_error.assert_called_once()
        args, _ = mock_error.call_args
        assert args[0] == "Missing Actions"
        assert "missing-action" in args[1]

    def test_missing_actions_returns_early(self, screen):
        scenario = MagicMock()
        scenario.name = "test-scenario"
        scenario.custom_action_names = {0: "missing-action"}
        screen._scenarios = [scenario]
        screen._active_profile = MagicMock()

        with patch("src.screens.actions_screen.CustomActionStore") as mock_ca_store:
            mock_ca_store.load_all.return_value = []
            with patch.object(screen, "_build_action_chain") as mock_build:
                screen.on_scenario_selected("test-scenario")
                mock_build.assert_not_called()

    def test_valid_scenario_sets_current(self, screen):
        scenario = MagicMock()
        scenario.name = "valid-scenario"
        scenario.custom_action_names = {}
        scenario.action_sequence = []
        screen._scenarios = [scenario]
        screen._active_profile = MagicMock()

        with patch("src.screens.actions_screen.show_error_dialog") as mock_error:
            with patch.object(screen, "_build_action_chain") as mock_build:
                screen.on_scenario_selected("valid-scenario")

        mock_error.assert_not_called()
        assert screen._current_scenario is scenario
        mock_build.assert_called_once_with(scenario)


class TestActionChain:
    def test_builds_card_for_sign_apk(self, screen):
        from src.models.action import Action
        from src.models.scenario import Scenario
        from src.screens.action_card import ActionCard

        scenario = Scenario(name="sign", action_sequence=[Action.SIGN_APK])
        screen.chain_container = MagicMock()
        screen._active_profile = MagicMock()

        screen._build_action_chain(scenario)

        assert len(screen._action_cards) == 1
        assert isinstance(screen._action_cards[0], ActionCard)
        assert screen._action_cards[0].action == Action.SIGN_APK

    def test_builds_card_for_build_aab(self, screen):
        from src.models.action import Action
        from src.models.scenario import Scenario
        from src.screens.action_card import ActionCard

        scenario = Scenario(name="build-aab", action_sequence=[Action.BUILD_AAB])
        screen.chain_container = MagicMock()
        screen._active_profile = MagicMock()

        screen._build_action_chain(scenario)

        assert len(screen._action_cards) == 1
        assert isinstance(screen._action_cards[0], ActionCard)
        assert screen._action_cards[0].action == Action.BUILD_AAB

    def test_builds_card_in_full_chain(self, screen):
        from src.models.action import Action
        from src.models.scenario import Scenario

        scenario = Scenario(
            name="full",
            action_sequence=[Action.CLEAN, Action.SYNC_SRC, Action.BUILD, Action.SIGN_APK],
        )
        screen.chain_container = MagicMock()
        screen._active_profile = MagicMock()

        screen._build_action_chain(scenario)

        actions = [card.action for card in screen._action_cards]
        assert actions == [Action.CLEAN, Action.SYNC_SRC, Action.BUILD, Action.SIGN_APK]


class TestShowHelp:
    def test_shows_help_popup(self, screen):
        with patch("src.screens.actions_screen.show_help_popup") as mock_help:
            screen.show_help()
        mock_help.assert_called_once()
        assert mock_help.call_args[0][0] == "Actions Screen Help"


class TestOpenSettings:
    def test_opens_settings_screen(self, screen):
        screen.manager.screen_names = ["settings"]
        screen.open_settings()
        assert screen.manager.current == "settings"

    def test_no_settings_screen_does_nothing(self, screen):
        screen.manager.screen_names = []
        screen.open_settings()
        assert screen.manager.current != "settings"


class TestOpenScenarioEditor:
    def test_opens_scenario_builder(self, screen):
        screen.open_scenario_editor()
        assert screen.manager.current == "scenario_builder"
