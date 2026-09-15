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

    def test_builds_card_for_pull_aab(self, screen):
        from src.models.action import Action
        from src.models.scenario import Scenario
        from src.screens.action_card import ActionCard

        scenario = Scenario(name="pull-aab", action_sequence=[Action.PULL_AAB])
        screen.chain_container = MagicMock()
        screen._active_profile = MagicMock()

        screen._build_action_chain(scenario)

        assert len(screen._action_cards) == 1
        assert isinstance(screen._action_cards[0], ActionCard)
        assert screen._action_cards[0].action == Action.PULL_AAB

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


class TestScenarioSpinnerOption:
    def test_trigger_shows_tooltip_for_known_scenario(self):
        from src.screens.actions_screen import ScenarioSpinnerOption

        ScenarioSpinnerOption.desc_map = {"MyScenario": "Do something cool"}
        opt = ScenarioSpinnerOption(text="MyScenario")
        with patch("src.screens.actions_screen._show_scenario_tooltip") as mock_show:
            opt._trigger_tooltip((100, 100))
            mock_show.assert_called_once()
            args, _ = mock_show.call_args
            assert args[0] == "Do something cool"
            assert args[1] == (100, 100)

    def test_trigger_hides_for_empty_description(self):
        from src.screens.actions_screen import ScenarioSpinnerOption

        ScenarioSpinnerOption.desc_map = {"Empty": "   "}
        opt = ScenarioSpinnerOption(text="Empty")
        with patch("src.screens.actions_screen._show_scenario_tooltip") as mock_show:
            with patch("src.screens.actions_screen._hide_scenario_tooltip") as mock_hide:
                opt._trigger_tooltip((10, 10))
                mock_show.assert_not_called()
                mock_hide.assert_called_once()

    def test_trigger_hides_for_missing_scenario(self):
        from src.screens.actions_screen import ScenarioSpinnerOption

        ScenarioSpinnerOption.desc_map = {}
        opt = ScenarioSpinnerOption(text="Unknown")
        with patch("src.screens.actions_screen._hide_scenario_tooltip") as mock_hide:
            opt._trigger_tooltip((0, 0))
            mock_hide.assert_called_once()

    def test_hide_on_leave_cancels_hover(self):
        from src.screens.actions_screen import ScenarioSpinnerOption
        from unittest.mock import MagicMock

        ScenarioSpinnerOption.desc_map = {"A": "desc"}
        opt = ScenarioSpinnerOption(text="A")
        # simulate hover started
        opt._hover_inside = True
        mock_event = MagicMock()
        opt._hover_event = mock_event
        opt.get_parent_window = MagicMock(return_value=MagicMock())
        opt.to_widget = MagicMock(return_value=(0, 0))
        opt.collide_point = MagicMock(return_value=False)
        with patch("src.screens.actions_screen._hide_scenario_tooltip") as mock_hide:
            opt._on_mouse_pos(MagicMock(), (0, 0))
            mock_event.cancel.assert_called_once()
            mock_hide.assert_called_once()
            assert opt._hover_inside is False

    def test_refresh_sets_desc_map_and_option_cls(self, screen):
        from src.screens.actions_screen import ScenarioSpinnerOption
        from src.models.scenario import Scenario
        from src.models.action import Action

        s1 = Scenario(name="Full Clean build", description="clean desc", action_sequence=[Action.CLEAN], is_predefined=True)
        s2 = Scenario(name="Custom", description="custom desc", action_sequence=[Action.BUILD], is_predefined=False)
        screen._scenarios = []
        screen.scenario_spinner = MagicMock()
        with patch("src.screens.actions_screen.ScenarioStore") as mock_store, \
             patch("src.screens.actions_screen.ScenarioService") as mock_svc:
            mock_svc.return_value.get_predefined_scenarios.return_value = [s1]
            mock_store.load_all.return_value = [s2]
            # replace service instance
            screen._scenario_service = mock_svc.return_value
            screen._refresh_scenarios()
            assert ScenarioSpinnerOption.desc_map["Full Clean build"] == "clean desc"
            assert ScenarioSpinnerOption.desc_map["Custom"] == "custom desc"
            assert screen.scenario_spinner.option_cls == ScenarioSpinnerOption

    def test_click_before_delay_cancels_hover_and_hides(self):
        from src.screens.actions_screen import ScenarioSpinnerOption

        ScenarioSpinnerOption.desc_map = {"A": "desc"}
        opt = ScenarioSpinnerOption(text="A")
        mock_event = MagicMock()
        opt._hover_event = mock_event
        with patch("src.screens.actions_screen._hide_scenario_tooltip") as mock_hide:
            opt._on_option_press()
            mock_event.cancel.assert_called_once()
            mock_hide.assert_called_once()
            assert opt._hover_event is None
        # also on_release
        mock_event2 = MagicMock()
        opt._hover_event = mock_event2
        with patch("src.screens.actions_screen._hide_scenario_tooltip") as mock_hide2:
            opt._on_option_release()
            mock_event2.cancel.assert_called_once()
            mock_hide2.assert_called_once()

    def test_dropdown_close_hides_tooltip(self, screen):
        with patch("src.screens.actions_screen._hide_scenario_tooltip") as mock_hide:
            screen._on_scenario_spinner_open(MagicMock(), False)
            mock_hide.assert_called_once()
        with patch("src.screens.actions_screen._hide_scenario_tooltip") as mock_hide2:
            screen._on_scenario_spinner_open(MagicMock(), True)
            mock_hide2.assert_not_called()

    def test_selecting_before_tooltip_delay_does_not_leave_stuck_tooltip(self):
        from src.screens.actions_screen import ScenarioSpinnerOption
        from unittest.mock import MagicMock

        ScenarioSpinnerOption.desc_map = {"Build and Sign AAB": "Build AAB, signs ..."}
        opt = ScenarioSpinnerOption(text="Build and Sign AAB")
        # hover schedules event
        mock_event = MagicMock()
        opt._hover_event = mock_event
        opt._hover_inside = True
        # user clicks before delay -> press cancels event and hides
        with patch("src.screens.actions_screen._hide_scenario_tooltip") as mock_hide, \
             patch("src.screens.actions_screen._show_scenario_tooltip") as mock_show:
            opt._on_option_press()
            mock_event.cancel.assert_called_once()
            mock_hide.assert_called_once()
            # even if the Clock event would have fired, it is cancelled so no show
            assert opt._hover_event is None
            mock_show.assert_not_called()
