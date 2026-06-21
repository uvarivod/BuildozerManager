import subprocess

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
        self._cursor_end(self.sourcedir_input)
        self._cursor_end(self.spec_path_input)

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
        self.delete_exclusions_input.text = ""

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

    def _cursor_end(self, widget):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(widget, 'cursor', (len(widget.text), 0)), 0)

    def _browse_sourcedir(self):
        from pathlib import Path
        from src.screens.file_chooser_helper import FileChooserHelper

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

        def on_choose_dir(chosen_path):
            self.sourcedir_input.text = chosen_path
            self._cursor_end(self.sourcedir_input)
            spec_candidate = Path(chosen_path) / "buildozer.spec"
            if spec_candidate.exists():
                self._prompt_use_spec(str(spec_candidate))

        FileChooserHelper.show_dir_chooser(
            initial_path=initial_path, on_choose=on_choose_dir
        )

    def _prompt_use_spec(self, spec_path):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(
            Label(
                text="We found buildozer.spec in the folder you chose.\nDo you want to use it?"
            )
        )
        btn_row = BoxLayout(size_hint_y=None, height=44, spacing=10)
        no_btn = Button(text="No")
        yes_btn = Button(text="Yes", background_color=(0.2, 0.6, 0.2, 1))
        btn_row.add_widget(no_btn)
        btn_row.add_widget(yes_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title="buildozer.spec Found",
            content=content,
            size_hint=(0.5, 0.3),
            auto_dismiss=False,
        )

        def on_yes(*_):
            self.spec_path_input.text = spec_path
            self._cursor_end(self.spec_path_input)
            popup.dismiss()

        def on_no(*_):
            popup.dismiss()

        yes_btn.bind(on_release=on_yes)
        no_btn.bind(on_release=on_no)
        popup.open()

    def _browse_spec_path(self):
        from pathlib import Path
        from src.screens.file_chooser_helper import FileChooserHelper

        current_spec = self.spec_path_input.text.strip()
        if current_spec:
            try:
                p = Path(current_spec)
                start_dir = str(p.parent) if not p.is_dir() else str(p)
            except Exception:
                start_dir = "."
        else:
            sourcedir = self.sourcedir_input.text.strip()
            start_dir = sourcedir if sourcedir and Path(sourcedir).is_dir() else "."

        def on_choose_file(chosen_path):
            self.spec_path_input.text = chosen_path
            self._cursor_end(self.spec_path_input)

        spec_path = self.spec_path_input.text.strip()
        selected = spec_path if spec_path else None

        FileChooserHelper.show_file_chooser(
            initial_path=start_dir,
            target_filename="buildozer.spec",
            on_choose=on_choose_file,
            selected_path=selected,
        )

    def _browse_adb_path(self):
        from pathlib import Path
        from src.screens.file_chooser_helper import FileChooserHelper

        current_adb = self.adb_path_input.text.strip()
        if current_adb:
            try:
                p = Path(current_adb)
                start_dir = str(p.parent) if not p.is_dir() else str(p)
            except Exception:
                start_dir = "."
        else:
            start_dir = "."

        def on_choose_file(chosen_path):
            self.adb_path_input.text = chosen_path
            self._cursor_end(self.adb_path_input)

        adb_path = self.adb_path_input.text.strip()
        selected = adb_path if adb_path else None

        FileChooserHelper.show_file_chooser(
            initial_path=start_dir,
            target_filename="adb.exe",
            on_choose=on_choose_file,
            selected_path=selected,
        )

    def _check_adb(self):
        from kivy.uix.popup import Popup

        adb_path = self.adb_path_input.text.strip()
        if not adb_path:
            from kivy.uix.label import Label
            popup = Popup(
                title="ADB Check",
                content=Label(text="No ADB path configured."),
                size_hint=(0.5, 0.3),
            )
            popup.open()
            return

        try:
            result = subprocess.run(
                [adb_path, "version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                text = f"ADB is working\n\n{result.stdout.strip()}"
            else:
                text = f"ADB error:\n{result.stderr.strip()}"
        except FileNotFoundError:
            text = f"ADB not found at:\n{adb_path}"
        except subprocess.TimeoutExpired:
            text = "ADB check timed out (10s)."
        except Exception as e:
            text = f"Error: {e}"

        from kivy.uix.textinput import TextInput
        from kivy.uix.boxlayout import BoxLayout
        content = BoxLayout()
        text_input = TextInput(
            text=text,
            readonly=True,
            multiline=True,
            size_hint=(1, 1),
        )
        content.add_widget(text_input)
        popup = Popup(
            title="ADB Check",
            content=content,
            size_hint=(0.6, 0.4),
        )
        popup.open()

    def _browse_wsl_dir(self):
        from pathlib import Path
        from src.screens.file_chooser_helper import FileChooserHelper

        current = self.wsl_dir_input.text.strip()
        if current:
            try:
                path = Path(current)
                if not path.is_dir():
                    path = path.parent
                initial_path = str(path)
            except Exception:
                initial_path = "."
        else:
            distro = self.wsl_distro_input.text.strip()
            if distro:
                initial_path = f"\\\\wsl.localhost\\{distro}"
            else:
                initial_path = "."

        def on_choose_dir(chosen_path):
            self.wsl_dir_input.text = chosen_path
            self._cursor_end(self.wsl_dir_input)

        FileChooserHelper.show_dir_chooser(
            initial_path=initial_path, on_choose=on_choose_dir
        )

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
