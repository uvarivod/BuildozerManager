from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, NumericProperty
from kivy.logger import Logger

from ..models.profile import Profile
from ..services.storage_service import ProfileStore


class ProfileListItem(Button):
    index = NumericProperty(0)
    profile_screen = ObjectProperty(None)

    def on_release(self):
        if self.profile_screen:
            self.profile_screen._on_tap(self.index)


class ProfileListScreen(Screen):
    profile_list = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._profiles: list[Profile] = []
        self._selected_index: int = -1
        self.on_profile_selected = None

    def on_enter(self, *args):
        Logger.debug(f"ProfileListScreen.on_enter, ids={list(self.ids.keys())}")
        self.refresh_list()

    def refresh_list(self):
        self._profiles = ProfileStore.load_all()
        Logger.debug(f"refresh_list: {len(self._profiles)} profiles, profile_list={self.profile_list}, ids={list(self.ids.keys()) if hasattr(self, 'ids') else 'no ids'}")
        rv = self.profile_list or self.ids.get("profile_list")
        if rv:
            data = [{"text": p.name, "index": i, "profile_screen": self} for i, p in enumerate(self._profiles)]
            Logger.debug(f"setting data: {data}")
            rv.data = data
        else:
            Logger.error("profile_list RecycleView not found!")

    def _on_tap(self, index: int):
        if 0 <= index < len(self._profiles):
            self._selected_index = index
            if self.on_profile_selected:
                self.on_profile_selected(self._profiles[index])
            if self.manager:
                self.manager.current = "editor"

    def add_profile(self):
        name = "New Profile"
        existing_names = [p.name for p in self._profiles]
        if name in existing_names:
            i = 2
            while f"{name} {i}" in existing_names:
                i += 1
            name = f"{name} {i}"
        profile = Profile(name=name)
        self._profiles.append(profile)
        print(f"[DEBUG] saving {len(self._profiles)} profiles")
        ProfileStore.save_all(self._profiles)
        self.refresh_list()
        if self.manager:
            self.manager.get_screen("editor").load_profile(profile)
            self.manager.current = "editor"

    def delete_selected(self):
        if self._selected_index < 0 or self._selected_index >= len(self._profiles):
            return
        ProfileStore.delete(self._profiles[self._selected_index].name)
        self._profiles.pop(self._selected_index)
        self._selected_index = -1
        self.refresh_list()

    def get_selected(self) -> Profile | None:
        if 0 <= self._selected_index < len(self._profiles):
            return self._profiles[self._selected_index]
        return None
