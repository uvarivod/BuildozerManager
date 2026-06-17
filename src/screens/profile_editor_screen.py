from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty, ObjectProperty

from src.models.profile import Profile
from src.models.patch import PatchRegistry
from src.services.storage_service import ProfileStore


class ProfileEditorScreen(Screen):
    profile_name = StringProperty("")
    sourcedir = StringProperty("")
    spec_path = StringProperty("")
    adb_path = StringProperty("adb")
    wsl_dir = StringProperty("")
    wsl_distro = StringProperty("Ubuntu-22.04")
    excluded_files = ListProperty([])
    delete_exclusions = ListProperty([".buildozer"])
    enabled_patches = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_profile: Profile | None = None

    def load_profile(self, profile: Profile):
        self._current_profile = profile
        self.profile_name = profile.name
        self.sourcedir = profile.sourcedir
        self.spec_path = profile.spec_path
        self.adb_path = profile.adb_path
        self.wsl_dir = profile.wsl_dir
        self.wsl_distro = profile.wsl_distro
        self.excluded_files = list(profile.excluded_files)
        self.delete_exclusions = list(profile.delete_exclusions)
        self.enabled_patches = list(profile.patches)

    def save_profile(self):
        if not self._current_profile:
            return
        old_name = self._current_profile.name
        self._current_profile.name = self.profile_name
        self._current_profile.sourcedir = self.sourcedir
        self._current_profile.spec_path = self.spec_path
        self._current_profile.adb_path = self.adb_path
        self._current_profile.wsl_dir = self.wsl_dir
        self._current_profile.wsl_distro = self.wsl_distro
        self._current_profile.excluded_files = list(self.excluded_files)
        self._current_profile.delete_exclusions = list(self.delete_exclusions)
        self._current_profile.patches = list(self.enabled_patches)
        profiles = ProfileStore.load_all()
        for i, p in enumerate(profiles):
            if p.name == old_name:
                profiles[i] = self._current_profile
                break
        ProfileStore.save_all(profiles)

    def auto_detect_spec(self):
        import os
        if self.sourcedir and os.path.isdir(self.sourcedir):
            spec_candidate = os.path.join(self.sourcedir, "buildozer.spec")
            if os.path.isfile(spec_candidate):
                self.spec_path = spec_candidate

    def auto_detect_adb(self):
        import shutil
        adb = shutil.which("adb")
        if adb:
            self.adb_path = adb

    def available_patches(self):
        return PatchRegistry.list_patches()
