import subprocess

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label

from src.models.patch import PatchRegistry
from src.models.custom_action import CustomAction, ActionType
from src.models.profile import Profile
from src.services.storage_service import ProfileStore, SettingsStore, CustomActionStore
from src.services.log_service import LogService


class ProfileEditorScreen(Screen):
    name_input = ObjectProperty(None)
    sourcedir_input = ObjectProperty(None)
    spec_path_input = ObjectProperty(None)
    adb_path_input = ObjectProperty(None)
    wsl_dir_input = ObjectProperty(None)
    wsl_distro_input = ObjectProperty(None)
    excluded_files_input = ObjectProperty(None)
    patches_container = ObjectProperty(None)
    delete_exclusions_input = ObjectProperty(None)
    save_btn = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._log = LogService()
        self._editing_profile: Profile | None = None
        self._orig_name: str = ""
        self._patch_checkboxes: dict[str, CheckBox] = {}
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        self._build_patch_selector()

    def _build_patch_selector(self):
        if not self.patches_container:
            return
        self.patches_container.clear_widgets()
        self._patch_checkboxes = {}

        selected = set()
        if self._editing_profile:
            profiles = ProfileStore.load_all()
            for p in profiles:
                if p.name == self._editing_profile.name:
                    self._editing_profile = p
                    break
            selected = set(self._editing_profile.patches)

        for patch in PatchRegistry.list_patches():
            self._add_patch_row(patch.name, patch.description, selected)

        custom_patches = [ca for ca in CustomActionStore.load_all() if ca.type == ActionType.PATCH]
        for ca in custom_patches:
            self._add_patch_row(ca.name, ca.description, selected)

    def _add_patch_row(self, name: str, description: str, selected: set):
        row = BoxLayout(size_hint_y=None, height=28, spacing=4, padding=[4, 0])
        cb = CheckBox(active=name in selected, size_hint_x=None, width=28)
        desc = f" ({description})" if description else ""
        lbl = Label(
            text=f"{name}{desc}",
            font_size="11sp",
            color=(0.8, 0.8, 0.8, 1),
            halign="left",
            valign="middle",
        )
        row.bind(size=lambda inst, sz, lb=lbl: setattr(lb, 'text_size', (max(sz[0] - 36, 0), None)))
        row.add_widget(cb)
        row.add_widget(lbl)
        self.patches_container.add_widget(row)
        self._patch_checkboxes[name] = cb

    def _remove_missing_patches(self, profile: Profile, missing: list[str]):
        profile.patches = [p for p in profile.patches if p not in missing]
        profiles = ProfileStore.load_all()
        profiles = [p for p in profiles if p.name != profile.name]
        profiles.append(profile)
        ProfileStore.save_all(profiles)

    def load_profile(self, profile: Profile):
        profiles = ProfileStore.load_all()
        for p in profiles:
            if p.name == profile.name:
                profile = p
                break
        if profile.patches:
            registry_names = {p.name for p in PatchRegistry.list_patches()}
            custom_patch_names = {ca.name for ca in CustomActionStore.load_all() if ca.type == ActionType.PATCH}
            available = registry_names | custom_patch_names
            missing = [p for p in profile.patches if p not in available]
            if missing:
                from kivy.uix.popup import Popup
                from kivy.uix.button import Button
                msg = (f"Profile '{profile.name}' references missing patches:\n" +
                       "\n".join(f"  - {p}" for p in missing) +
                       "\n\nThey will be removed automatically.")
                content = BoxLayout(orientation="vertical", spacing=10, padding=10)
                content.add_widget(Label(text=msg, font_size="11sp"))
                btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
                popup = Popup(title="Missing Patches", content=content, size_hint=(0.45, 0.35))
                def on_ok(*_):
                    self._remove_missing_patches(profile, missing)
                    self._build_patch_selector()
                    popup.dismiss()
                btn_box.add_widget(Button(text="OK", on_release=on_ok))
                content.add_widget(btn_box)
                popup.open()

        self._editing_profile = profile
        self._orig_name = profile.name
        self.name_input.text = profile.name
        self.sourcedir_input.text = profile.sourcedir
        self.spec_path_input.text = profile.spec_path
        self.adb_path_input.text = profile.adb_path
        self.wsl_dir_input.text = profile.wsl_dir
        self.wsl_distro_input.text = profile.wsl_distro
        self.excluded_files_input.text = ", ".join(profile.excluded_files)
        self.delete_exclusions_input.text = ", ".join(profile.delete_exclusions)
        self._build_patch_selector()
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
        self.delete_exclusions_input.text = ""
        self._build_patch_selector()

    def _build_profile(self, name: str) -> Profile:
        selected_patches = [
            name for name, cb in self._patch_checkboxes.items() if cb.active
        ]
        return Profile(
            name=name,
            sourcedir=self.sourcedir_input.text.strip(),
            spec_path=self.spec_path_input.text.strip(),
            adb_path=self.adb_path_input.text.strip(),
            wsl_dir=self.wsl_dir_input.text.strip(),
            wsl_distro=self.wsl_distro_input.text.strip(),
            excluded_files=[x.strip() for x in self.excluded_files_input.text.split(",") if x.strip()],
            patches=selected_patches,
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
