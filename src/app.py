from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from pathlib import Path

import src.patches

from .screens.actions_screen import ActionsScreen
from .screens.profile_editor_screen import ProfileEditorScreen
from .screens.scenario_editor_screen import ScenarioEditorScreen
from .services.log_service import LogService
from .services.storage_service import ProfileStore, SettingsStore
from .models.profile import Profile


class BuildozerManagerApp(App):
    kv_directory = str(Path(__file__).parent / "kv")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._log = LogService()
        self._active_profile: Profile | None = None

    def build(self):
        self._log.info("Buildozer Manager starting...")

        Builder.load_file(str(Path(self.kv_directory) / "action_card.kv"))
        Builder.load_file(str(Path(self.kv_directory) / "actions_screen.kv"))
        Builder.load_file(str(Path(self.kv_directory) / "profile_editor_screen.kv"))
        Builder.load_file(str(Path(self.kv_directory) / "scenario_editor_screen.kv"))
        Builder.load_file(str(Path(self.kv_directory) / "log_panel.kv"))

        sm = ScreenManager()
        sm.add_widget(ActionsScreen(name="actions"))
        sm.add_widget(ProfileEditorScreen(name="editor"))
        sm.add_widget(ScenarioEditorScreen(name="scenario_builder"))

        actions_screen = sm.get_screen("actions")
        editor_screen = sm.get_screen("editor")

        def on_profile_selected(profile: Profile):
            self._active_profile = profile
            actions_screen.set_active_profile(profile)
            SettingsStore.save({"last_profile": profile.name})

        actions_screen.on_profile_selected = on_profile_selected
        editor_screen.on_profile_updated = on_profile_selected

        # Restore last active profile
        settings = SettingsStore.load()
        last_name = settings.get("last_profile", "")
        if last_name:
            profiles = ProfileStore.load_all()
            profile = next((p for p in profiles if p.name == last_name), None)
            if profile:
                on_profile_selected(profile)

        sm.current = "actions"
        self._log.success("Buildozer Manager ready")
        return sm

    def on_stop(self):
        self._log.info("Buildozer Manager shutting down")
