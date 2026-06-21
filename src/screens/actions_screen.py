from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.clock import Clock

from src.models.action import Action, ActionState
from src.models.profile import Profile
from src.models.scenario import Scenario
from src.services.action_runner import ActionRunner
from src.services.scenario_service import ScenarioService
from src.services.log_service import LogService
from src.services.storage_service import ProfileStore


class ActionsScreen(Screen):
    log_panel = ObjectProperty(None)
    scenario_spinner = ObjectProperty(None)
    profile_spinner = ObjectProperty(None)
    status_label = StringProperty("Ready")
    is_running = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._runner = ActionRunner()
        self._scenario_service = ScenarioService()
        self._log = LogService()
        self._active_profile: Profile | None = None
        self._scenarios: list[Scenario] = []
        self._current_running_action: Action | None = None
        self._updating_spinner = False
        self.on_profile_selected = None

    def on_enter(self, *args):
        self._refresh_scenarios()
        self._refresh_profile_spinner()

    def _refresh_profile_spinner(self):
        profiles = ProfileStore.load_all()
        if self.profile_spinner:
            self.profile_spinner.values = [p.name for p in profiles]

    def set_active_profile(self, profile: Profile | None):
        self._active_profile = profile
        if profile:
            self.status_label = f"Ready"
            self._refresh_profile_spinner()
            self._updating_spinner = True
            if self.profile_spinner:
                self.profile_spinner.text = profile.name
            self._updating_spinner = False
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

    def _refresh_scenarios(self):
        self._scenarios = self._scenario_service.get_predefined_scenarios()
        if self.scenario_spinner:
            self.scenario_spinner.values = [s.name for s in self._scenarios]

    def run_single_action(self, action_name: str):
        if not self._active_profile:
            self._log.warn("No profile selected")
            return

        action_map = {
            "sync_src": Action.SYNC_SRC,
            "clean": Action.CLEAN,
            "build": Action.BUILD,
            "patch": Action.PATCH,
            "download": Action.DOWNLOAD,
            "pull_apk": Action.PULL_APK,
            "run": Action.RUN,
        }
        action = action_map.get(action_name.lower())
        if not action:
            return

        self._log.info(f"Starting {action.name}...")
        self.status_label = f"Running: {action.name}"
        self.is_running = True

        def on_state_change(state):
            Clock.schedule_once(lambda dt: self._update_status(state))

        self.log_panel.reset_timer()

        def run():
            state = self._runner.run_action(action, self._active_profile, on_state_change=on_state_change)
            Clock.schedule_once(lambda dt: self._on_action_done(action, state), 0)

        import threading
        t = threading.Thread(target=run, daemon=True)
        t.start()

    def run_scenario(self):
        if not self._active_profile:
            self._log.warn("No profile selected")
            return

        if not self.scenario_spinner or not self.scenario_spinner.text:
            self._log.warn("No scenario selected")
            return

        scenario_name = self.scenario_spinner.text
        scenario = next((s for s in self._scenarios if s.name == scenario_name), None)
        if not scenario:
            return

        self._log.info(f"Starting scenario: {scenario.name}")
        self.status_label = f"Running: {scenario.name}"

        def run():
            run_result = self._scenario_service.run_scenario(scenario, self._active_profile)
            Clock.schedule_once(lambda dt: self._on_scenario_done(run_result), 0)

        import threading
        t = threading.Thread(target=run, daemon=True)
        t.start()

    def cancel_action(self):
        self._runner.cancel()
        self._log.warn("Cancelling current operation...")
        self.status_label = "Cancelling..."
        self.is_running = False

    def _update_status(self, state: ActionState):
        self.status_label = state.name

    def _on_action_done(self, action: Action, state: ActionState):
        self.log_panel.stop_timer()
        self._log.info(f"{action.name}: {state.name}")
        self.status_label = f"{action.name}: {state.name}"
        self.is_running = False

    def _on_scenario_done(self, run_result):
        status_str = run_result.overall_status.name
        self._log.info(f"Scenario completed: {status_str} ({run_result.duration:.1f}s)")
        self.status_label = f"Scenario: {status_str}"
