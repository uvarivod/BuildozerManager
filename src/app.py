from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from pathlib import Path

from .screens.profile_list_screen import ProfileListScreen
from .screens.profile_editor_screen import ProfileEditorScreen
from .screens.actions_screen import ActionsScreen
from .screens.scenario_builder_screen import ScenarioBuilderScreen
from .screens.log_panel import LogPanel
from .services.log_service import LogService
from .services.storage_service import ProfileStore, SettingsStore
from .models.profile import Profile


class MainScreen(Screen):
    pass


class BuildozerManagerApp(App):
    kv_directory = str(Path(__file__).parent / "kv")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._log = LogService()
        self._active_profile: Profile | None = None

    def build(self):
        self._log.info("Buildozer Manager starting...")

        Builder.load_file(str(Path(self.kv_directory) / "profile_list_screen.kv"))
        Builder.load_file(str(Path(self.kv_directory) / "profile_editor_screen.kv"))
        Builder.load_file(str(Path(self.kv_directory) / "actions_screen.kv"))
        Builder.load_file(str(Path(self.kv_directory) / "scenario_builder_screen.kv"))
        Builder.load_file(str(Path(self.kv_directory) / "log_panel.kv"))

        sm = ScreenManager()
        sm.add_widget(ProfileListScreen(name="profiles"))
        sm.add_widget(ProfileEditorScreen(name="editor"))
        sm.add_widget(ActionsScreen(name="actions"))
        sm.add_widget(ScenarioBuilderScreen(name="scenario_builder"))

        profile_screen = sm.get_screen("profiles")
        editor_screen = sm.get_screen("editor")
        actions_screen = sm.get_screen("actions")

        def on_profile_selected(profile: Profile):
            self._active_profile = profile
            editor_screen.load_profile(profile)
            actions_screen.set_active_profile(profile)
            SettingsStore.save({"last_profile": profile.name})

        profile_screen.on_profile_selected = on_profile_selected
        actions_screen.on_profile_selected = on_profile_selected

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
