from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.label import Label
from kivy.clock import Clock

from src.models.action import Action, ActionState
from src.models.profile import Profile
from src.models.scenario import Scenario
from src.screens.action_card import ActionCard, PatchCard
from src.services.action_runner import ActionRunner
from src.services.scenario_service import ScenarioService
from src.services.log_service import LogService
from src.services.storage_service import ProfileStore, ScenarioStore, SettingsStore, CustomActionStore


class ActionsScreen(Screen):
    log_panel = ObjectProperty(None)
    scenario_spinner = ObjectProperty(None)
    profile_spinner = ObjectProperty(None)
    chain_container = ObjectProperty(None)
    status_label = StringProperty("Ready")
    is_running = BooleanProperty(False)
    allow_separate_execution = BooleanProperty(False)

    def on_allow_separate_execution(self, instance, value):
        if hasattr(self, "_action_cards"):
            for card in self._action_cards:
                card.allow_click = value
        self._save_separate_setting()

    def toggle_allow_separate(self):
        self.allow_separate_execution = not self.allow_separate_execution

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._runner = ActionRunner()
        self._scenario_service = ScenarioService(runner=self._runner)
        self._log = LogService()
        self._active_profile: Profile | None = None
        self._scenarios: list[Scenario] = []
        self._current_scenario: Scenario | None = None
        self._updating_spinner = False
        self._run_counter = 0
        self.on_profile_selected = None
        settings = SettingsStore.load()
        saved = settings.get("allow_separate_execution", False)
        self.allow_separate_execution = saved

    def _save_separate_setting(self):
        SettingsStore.save({"allow_separate_execution": self.allow_separate_execution})

    def _on_action_state_change(self, action_index: int, state: ActionState):
        if hasattr(self, "_action_cards") and 0 <= action_index < len(self._action_cards):
            self._action_cards[action_index].set_state(state)

    def _reset_action_chain_states(self):
        if hasattr(self, "_action_cards"):
            for card in self._action_cards:
                card.reset_state()

    def _disable_controls(self):
        if hasattr(self, "_action_cards"):
            for card in self._action_cards:
                card.allow_click = False
        if self.profile_spinner:
            self.profile_spinner.disabled = True
        if self.scenario_spinner:
            self.scenario_spinner.disabled = True

    def _enable_controls(self):
        if hasattr(self, "_action_cards"):
            for card in self._action_cards:
                card.allow_click = self.allow_separate_execution
        if self.profile_spinner:
            self.profile_spinner.disabled = False
        if self.scenario_spinner:
            self.scenario_spinner.disabled = False

    def on_enter(self, *args):
        self._refresh_scenarios()
        self._refresh_profile_spinner()
        if self._active_profile:
            profiles = ProfileStore.load_all()
            for p in profiles:
                if p.name == self._active_profile.name:
                    self._active_profile = p
                    break
        if self._current_scenario:
            for s in self._scenarios:
                if s.name == self._current_scenario.name:
                    self._current_scenario = s
                    break
            self._build_action_chain(self._current_scenario)

    def _refresh_profile_spinner(self):
        profiles = ProfileStore.load_all()
        if self.profile_spinner:
            self.profile_spinner.values = [p.name for p in profiles]

    def set_active_profile(self, profile: Profile | None):
        self._active_profile = profile
        if profile:
            self.status_label = "Ready"
            self._refresh_profile_spinner()
            self._updating_spinner = True
            if self.profile_spinner:
                self.profile_spinner.text = profile.name
            self._updating_spinner = False
            if self._current_scenario:
                self._build_action_chain(self._current_scenario)
        else:
            self.status_label = "No profile selected"

    def on_profile_spinner_text(self, text: str):
        if self._updating_spinner or not text or text == "Select profile":
            return
        profiles = ProfileStore.load_all()
        profile = next((p for p in profiles if p.name == text), None)
        if profile and self.on_profile_selected:
            self.on_profile_selected(profile)

    def delete_profile(self):
        if not self._active_profile:
            self._log.warn("No profile to delete")
            return
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button

        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=f"Delete profile '{self._active_profile.name}'?"))
        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
        popup = Popup(title="Confirm", content=content, size_hint=(0.4, 0.3))
        btn_box.add_widget(Button(text="Cancel", on_release=lambda *_: popup.dismiss()))
        btn_box.add_widget(Button(
            text="Delete",
            background_color=(0.8, 0.2, 0.2, 1),
            on_release=lambda *_: self._confirm_delete(popup)
        ))
        content.add_widget(btn_box)
        popup.open()

    def _confirm_delete(self, popup):
        popup.dismiss()
        name = self._active_profile.name
        ProfileStore.delete(name)
        self._active_profile = None
        self.status_label = "No profile selected"
        self._refresh_profile_spinner()
        if self.profile_spinner:
            self.profile_spinner.text = "Select profile"
        self._log.info(f"Deleted profile '{name}'")

    def edit_profile(self):
        if not self._active_profile or not self.manager:
            return
        editor = self.manager.get_screen("editor")
        if hasattr(editor, "load_profile"):
            editor.load_profile(self._active_profile)
        self.manager.current = "editor"

    def new_profile(self):
        if not self.manager:
            return
        editor = self.manager.get_screen("editor")
        editor.clear_fields()
        self.manager.current = "editor"

    def open_scenario_editor(self):
        if self.manager:
            self.manager.current = "scenario_builder"

    def _refresh_scenarios(self):
        predefined = self._scenario_service.get_predefined_scenarios()
        user = ScenarioStore.load_all()
        self._scenarios = predefined + user
        if self.scenario_spinner:
            self.scenario_spinner.values = [s.name for s in self._scenarios]

    def on_scenario_selected(self, text: str):
        if not text or text == "Select scenario":
            self._current_scenario = None
            self._clear_action_chain()
            return
        scenario = next((s for s in self._scenarios if s.name == text), None)
        if scenario:
            if scenario.custom_action_names:
                custom_actions = CustomActionStore.load_all()
                ca_names = {ca.name for ca in custom_actions}
                missing = sorted(set(name for name in scenario.custom_action_names.values() if name not in ca_names))
                if missing:
                    msg = f"Scenario '{scenario.name}' references missing actions:\n" + "\n".join(f"  - {name}" for name in missing)
                    from kivy.uix.popup import Popup
                    from kivy.uix.boxlayout import BoxLayout
                    from kivy.uix.button import Button
                    content = BoxLayout(orientation="vertical", spacing=10, padding=10)
                    content.add_widget(Label(text=msg, font_size="11sp"))
                    btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
                    popup = Popup(title="Missing Actions", content=content, size_hint=(0.45, 0.3))
                    btn_box.add_widget(Button(text="OK", on_release=lambda *_: popup.dismiss()))
                    content.add_widget(btn_box)
                    popup.open()
                    return
            self._current_scenario = scenario
            self._build_action_chain(scenario)

    def _clear_action_chain(self):
        if self.chain_container:
            self.chain_container.clear_widgets()

    def _build_action_chain(self, scenario: Scenario):
        self._clear_action_chain()
        if not self.chain_container:
            return
        cards = []
        for i, action in enumerate(scenario.action_sequence):
            if i > 0:
                arrow = Label(
                    text="->",
                    size_hint_x=None,
                    width=24,
                    bold=True,
                    color=(0.6, 0.6, 0.6, 1),
                )
                self.chain_container.add_widget(arrow)

            if action == Action.CUSTOM_SCRIPT:
                display_name = scenario.custom_action_names.get(i, "Custom Script")
                card = ActionCard(
                    action=action,
                    on_card_click=self._on_action_card_click,
                    allow_click=self.allow_separate_execution,
                )
                card.action_name = display_name
                card.description = scenario.custom_action_names.get(i, "")
            elif action == Action.PATCH and self._active_profile:
                card = PatchCard(
                    action=action,
                    on_card_click=self._on_action_card_click,
                    on_patch_click=self._on_patch_card_click,
                    profile=self._active_profile,
                    allow_click=self.allow_separate_execution,
                )
                card._build_patch_buttons()
            else:
                card = ActionCard(
                    action=action,
                    on_card_click=self._on_action_card_click,
                    allow_click=self.allow_separate_execution,
                )
            card.action_index = i
            cards.append(card)
            self.chain_container.add_widget(card)
        self._action_cards = cards
        # Force container width to fit all children
        self.chain_container.bind(minimum_width=self.chain_container.setter("width"))

    def _on_action_card_click(self, action: Action, card_index: int = -1):
        if not self._active_profile:
            self._log.warn("No profile selected")
            return
        if not self.allow_separate_execution:
            self._log.warn("Individual action execution is disabled")
            return

        if card_index < 0 and hasattr(self, "_action_cards"):
            for i, card in enumerate(self._action_cards):
                if card.action == action:
                    card_index = i
                    break

        script_path = None
        action_name = action.name
        if action == Action.CUSTOM_SCRIPT and self._current_scenario and hasattr(self, "_action_cards"):
            if 0 <= card_index < len(self._action_cards):
                card = self._action_cards[card_index]
                action_name = card.action_name
            if self._current_scenario.custom_action_names:
                ca_name = self._current_scenario.custom_action_names.get(card_index, "")
                custom_actions = CustomActionStore.load_all()
                for ca in custom_actions:
                    if ca.name == ca_name:
                        script_path = ca.logic
                        break

        self._log.info(f"Starting {action_name}...")
        self.status_label = f"Running: {action_name}"
        self.is_running = True
        self._disable_controls()
        self._run_counter += 1
        run_id = self._run_counter

        def on_state_change(state):
            Clock.schedule_once(lambda dt: self._update_status(state))
            if card_index >= 0:
                self._on_action_state_change(card_index, state)

        self.log_panel.reset_timer()

        def run():
            if card_index >= 0:
                self._on_action_state_change(card_index, ActionState.RUNNING)
            state = self._runner.run_action(action, self._active_profile, on_state_change=on_state_change, script_path=script_path)
            Clock.schedule_once(lambda dt: self._on_action_done(action, state, run_id), 0)

        import threading
        t = threading.Thread(target=run, daemon=True)
        t.start()

    def _on_patch_card_click(self, action: Action, patch_name: str):
        if not self._active_profile:
            self._log.warn("No profile selected")
            return
        if not self.allow_separate_execution:
            self._log.warn("Individual action execution is disabled")
            return

        card = None
        if hasattr(self, "_action_cards"):
            for c in self._action_cards:
                if c.action == action and hasattr(c, "set_patch_state"):
                    card = c
                    break

        self._log.info(f"Starting patch: {patch_name}...")
        self.status_label = f"Running: {patch_name}"
        self.is_running = True
        self._disable_controls()
        self._run_counter += 1
        run_id = self._run_counter

        self.log_panel.reset_timer()

        def run():
            if card:
                card.set_patch_state(patch_name, "RUNNING")
            log_cb = self._runner._make_log_callback(patch_name)

            log_cb("info", f"STARTING SINGLE PATCH: {patch_name}")
            state = self._runner.run_single_patch(patch_name, self._active_profile, log_cb)

            if card:
                card.set_patch_state(patch_name, state.name)
            Clock.schedule_once(lambda dt: self._on_single_patch_done(patch_name, state, run_id, card), 0)

        import threading
        t = threading.Thread(target=run, daemon=True)
        t.start()

    def _on_single_patch_done(self, patch_name: str, state: ActionState, run_id: int, card=None):
        if run_id != self._run_counter:
            return
        self.log_panel.stop_timer()
        self._log.info(f"Patch '{patch_name}': {state.name}")
        self.status_label = f"Patch '{patch_name}': {state.name}"
        self.is_running = False
        if card:
            card.set_patch_state(patch_name, state.name)
        self._enable_controls()

    def run_scenario(self):
        if not self._active_profile:
            self._log.warn("No profile selected")
            return

        if not self._current_scenario:
            self._log.warn("No scenario selected")
            return

        scenario = self._current_scenario
        skip_indices: set[int] = set()
        if hasattr(self, "_action_cards"):
            for card in self._action_cards:
                if card.is_skipped:
                    skip_indices.add(card.action_index)

        self._log.info(f"Starting scenario: {scenario.name}")
        self.status_label = f"Running: {scenario.name}"
        self.is_running = True
        self._disable_controls()
        self._reset_action_chain_states()
        self._run_counter += 1
        run_id = self._run_counter
        self.log_panel.reset_timer()

        def run():
            run_result = self._scenario_service.run_scenario(
                scenario,
                self._active_profile,
                skip_indices=skip_indices,
                cancel_check=lambda: self._runner._check_cancelled(),
                on_action_state_change=self._on_action_state_change,
            )
            Clock.schedule_once(lambda dt: self._on_scenario_done(run_result, run_id), 0)

        import threading
        t = threading.Thread(target=run, daemon=True)
        t.start()

    def cancel_action(self):
        self._runner.cancel()
        self._log.warn("Cancelling current operation...")
        self.status_label = "Cancelling..."
        self.is_running = False
        self._enable_controls()

    def _update_status(self, state: ActionState):
        self.status_label = state.name

    def _on_action_done(self, action: Action, state: ActionState, run_id: int):
        if run_id != self._run_counter:
            return
        self.log_panel.stop_timer()
        self._log.info(f"{action.name}: {state.name}")
        self.status_label = f"{action.name}: {state.name}"
        self.is_running = False

        if hasattr(self, "_action_cards"):
            done_index = next((i for i, card in enumerate(self._action_cards) if card.action == action), -1)
            for i, card in enumerate(self._action_cards):
                if i == done_index:
                    card.set_state(state)
                    card.allow_click = True
                else:
                    card.reset_state()

        self._enable_controls()

    def _on_scenario_done(self, run_result, run_id: int):
        if run_id != self._run_counter:
            return
        self.log_panel.stop_timer()
        status_str = run_result.overall_status.name
        self._log.info(f"Scenario completed: {status_str} ({run_result.duration:.1f}s)")
        self.status_label = f"Scenario: {status_str}"
        self.is_running = False
        self._enable_controls()
