from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock

from src.models.profile import Profile
from src.services.storage_service import ProfileStore, SettingsStore
from src.services.log_service import LogService


class ProfileEditorScreen(Screen):
    name_input = ObjectProperty(None)
    sourcedir_input = ObjectProperty(None)
    spec_path_input = ObjectProperty(None)
    adb_path_input = ObjectProperty(None)
    wsl_dir_input = ObjectProperty(None)
    wsl_distro_input = ObjectProperty(None)
    excluded_files_input = ObjectProperty(None)
    patches_input = ObjectProperty(None)
    delete_exclusions_input = ObjectProperty(None)
    save_btn = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._log = LogService()
        self._editing_profile: Profile | None = None
        self._orig_name: str = ""

    def load_profile(self, profile: Profile):
        self._editing_profile = profile
        self._orig_name = profile.name
        self.name_input.text = profile.name
        self.sourcedir_input.text = profile.sourcedir
        self.spec_path_input.text = profile.spec_path
        self.adb_path_input.text = profile.adb_path
        self.wsl_dir_input.text = profile.wsl_dir
        self.wsl_distro_input.text = profile.wsl_distro
        self.excluded_files_input.text = ", ".join(profile.excluded_files)
        self.patches_input.text = ", ".join(profile.patches)
        self.delete_exclusions_input.text = ", ".join(profile.delete_exclusions)

    def clear_fields(self):
        self._editing_profile = None
        self._orig_name = ""
        self.name_input.text = ""
        self.sourcedir_input.text = ""
        self.spec_path_input.text = ""
        self.adb_path_input.text = "adb"
        self.wsl_dir_input.text = ""
        self.wsl_distro_input.text = "Ubuntu-22.04"
        self.excluded_files_input.text = ""
        self.patches_input.text = ""
        self.delete_exclusions_input.text = ".buildozer"

    def _build_profile(self, name: str) -> Profile:
        return Profile(
            name=name,
            sourcedir=self.sourcedir_input.text.strip(),
            spec_path=self.spec_path_input.text.strip(),
            adb_path=self.adb_path_input.text.strip(),
            wsl_dir=self.wsl_dir_input.text.strip(),
            wsl_distro=self.wsl_distro_input.text.strip(),
            excluded_files=[x.strip() for x in self.excluded_files_input.text.split(",") if x.strip()],
            patches=[x.strip() for x in self.patches_input.text.split(",") if x.strip()],
            delete_exclusions=[x.strip() for x in self.delete_exclusions_input.text.split(",") if x.strip()],
        )

    def _browse_sourcedir(self):
        from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.togglebutton import ToggleButton
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from pathlib import Path

        current = self.sourcedir_input.text.strip()
        if current:
            try:
                path = Path(current)
                if not path.is_dir():
                    path = path.parent
                initial_path = str(path)
            except Exception:
                initial_path = "."
        else:
            initial_path = "."

        from src.services.storage_service import SettingsStore

        import os as _os
        def _dirs_only(folder, filename):
            return _os.path.isdir(_os.path.join(folder, filename))

        saved_view = SettingsStore.load().get("filechooser_view", "icon")

        icon_view = FileChooserIconView(dirselect=True, path=initial_path, filters=[_dirs_only])
        list_view = FileChooserListView(dirselect=True, path=initial_path, filters=[_dirs_only])

        display_path = current if current else ""
        chosen = {"path": display_path}

        label_text = f"Selected: {display_path}" if display_path else "Selected: (none)"
        path_label = Label(text=label_text, size_hint_y=None, height=28, halign="left")
        path_label.bind(size=lambda *_: setattr(path_label, "text_size", (path_label.width, None)))

        def update_path_label(instance, selection):
            if selection:
                chosen["path"] = selection[0]
                path_label.text = f"Selected: {selection[0]}"

        icon_view.bind(selection=update_path_label)
        list_view.bind(selection=update_path_label)

        def confirm(*_):
            if chosen["path"]:
                self.sourcedir_input.text = chosen["path"]
            popup.dismiss()

        def cancel(*_):
            popup.dismiss()

        view_container = BoxLayout()
        current_view = saved_view
        if current_view == "list":
            view_container.add_widget(list_view)
        else:
            view_container.add_widget(icon_view)

        def toggle_view(btn):
            nonlocal current_view
            view_container.clear_widgets()
            if current_view == "icon":
                view_container.add_widget(list_view)
                current_view = "list"
                btn.text = "Icon View"
            else:
                view_container.add_widget(icon_view)
                current_view = "icon"
                btn.text = "List View"
            SettingsStore.save({"filechooser_view": current_view})

        is_list = saved_view == "list"
        toggle_btn = ToggleButton(text="Icon View" if is_list else "List View", size_hint=(None, None), size=(100, 28))
        toggle_btn.bind(on_release=toggle_view)

        top_bar = BoxLayout(size_hint_y=None, height=32)
        top_bar.add_widget(path_label)
        top_bar.add_widget(toggle_btn)

        btn_row = BoxLayout(size_hint_y=None, height=44, spacing=10, padding=[0, 6])
        btn_row.add_widget(Button(text="Cancel", on_release=cancel))
        choose_btn = Button(text="Choose", background_color=(0.2, 0.6, 0.2, 1), on_release=confirm)
        btn_row.add_widget(choose_btn)

        content = BoxLayout(orientation="vertical")
        content.add_widget(top_bar)
        content.add_widget(view_container)
        content.add_widget(btn_row)

        popup = Popup(title="Select Source Directory",
                     content=content,
                     size_hint=(0.8, 0.85))
        popup.open()

    def _show_error(self, message: str):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        popup = Popup(title="Cannot Save",
                     content=Label(text=message),
                     size_hint=(0.5, 0.3))
        popup.open()

    def save(self):
        new_name = self.name_input.text.strip()

        if not new_name:
            self._show_error("Profile name cannot be empty.")
            return

        profiles = ProfileStore.load_all()
        name_taken = any(p.name == new_name for p in profiles)

        if self._editing_profile is None:
            if name_taken:
                self._show_error(f'A profile named "{new_name}" already exists.')
                return
            updated = self._build_profile(new_name)
            profiles.append(updated)
        else:
            if name_taken and new_name != self._orig_name:
                self._show_error(f'A profile named "{new_name}" already exists.')
                return
            profiles = [p for p in profiles if p.name != self._orig_name]
            updated = self._build_profile(new_name)
            profiles.append(updated)

        ProfileStore.save_all(profiles)
        SettingsStore.save({"last_profile": updated.name})

        self._log.info(f"Saved profile '{updated.name}'")

        if self.on_profile_updated:
            self.on_profile_updated(updated)

        if self.manager:
            self.manager.current = "actions"

    def cancel(self):
        if self.manager:
            self.manager.current = "actions"

    @property
    def on_profile_updated(self):
        return getattr(self, "_on_profile_updated", None)

    @on_profile_updated.setter
    def on_profile_updated(self, callback):
        self._on_profile_updated = callback
