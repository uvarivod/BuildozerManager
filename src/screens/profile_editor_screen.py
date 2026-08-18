import subprocess

from kivy.uix.screenmanager import Screen
from kivy.metrics import dp
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
from src.screens.dialog_helper import show_error_dialog, show_confirm_dialog, show_info_dialog, show_help_popup


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
    cert_path_input = ObjectProperty(None)
    cert_password_input = ObjectProperty(None)
    signing_check_label = ObjectProperty(None)
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
        row = BoxLayout(size_hint_y=None, height='28dp', spacing='4dp', padding=[dp(4), dp(0)])
        cb = CheckBox(active=name in selected, size_hint_x=None, width='28dp')
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
                msg = (f"Profile '{profile.name}' references missing patches:\n" +
                       "\n".join(f"  - {p}" for p in missing) +
                       "\n\nThey will be removed automatically.")

                def on_ok():
                    self._remove_missing_patches(profile, missing)
                    self._build_patch_selector()

                show_info_dialog(title="Missing Patches", message=msg)

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
        self.cert_path_input.text = profile.cert_path
        self.cert_password_input.text = profile.cert_password
        if self.signing_check_label:
            self.signing_check_label.text = ""
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
        if self.cert_path_input:
            self.cert_path_input.text = ""
        if self.cert_password_input:
            self.cert_password_input.text = ""
        if self.signing_check_label:
            self.signing_check_label.text = ""
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
            cert_path=self.cert_path_input.text.strip() if self.cert_path_input else "",
            cert_password=self.cert_password_input.text if self.cert_password_input else "",
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
        def on_yes():
            self.spec_path_input.text = spec_path
            self._cursor_end(self.spec_path_input)

        show_confirm_dialog(
            title="buildozer.spec Found",
            message="We found buildozer.spec in the folder you chose.\nDo you want to use it?",
            on_confirm=on_yes,
            confirm_text="Yes",
            cancel_text="No",
        )

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
        adb_path = self.adb_path_input.text.strip()
        if not adb_path:
            show_error_dialog("ADB Check", "No ADB path configured.")
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
        from kivy.uix.popup import Popup
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

    def _browse_cert_path(self):
        from pathlib import Path
        from src.screens.file_chooser_helper import FileChooserHelper

        current_cert = self.cert_path_input.text.strip()
        if current_cert:
            try:
                p = Path(current_cert)
                start_dir = str(p.parent) if not p.is_dir() else str(p)
            except Exception:
                start_dir = "."
        else:
            sourcedir = self.sourcedir_input.text.strip()
            start_dir = sourcedir if sourcedir and Path(sourcedir).is_dir() else "."

        def on_choose_file(chosen_path):
            self.cert_path_input.text = chosen_path
            self._cursor_end(self.cert_path_input)

        cert_path = self.cert_path_input.text.strip()
        selected = cert_path if cert_path else None

        FileChooserHelper.show_file_chooser(
            initial_path=start_dir,
            target_filename="*",
            on_choose=on_choose_file,
            selected_path=selected,
        )

    def _check_signing_tools(self):
        from src.services.wsl_service import WSLService
        from src.models.profile import Profile

        wsl_dir = self.wsl_dir_input.text.strip() if self.wsl_dir_input else ""
        wsl_distro = self.wsl_distro_input.text.strip() if self.wsl_distro_input else ""

        if not wsl_dir or not wsl_distro:
            missing = [f for f, v in [("wsl_dir", wsl_dir), ("wsl_distro", wsl_distro)] if not v]
            show_error_dialog("Signing Tools Check", f"Cannot check signing tools: missing {', '.join(missing)}")
            return

        profile = Profile(name="check", wsl_dir=wsl_dir, wsl_distro=wsl_distro)
        ok, detail = WSLService().check_signing_tools(profile)

        if ok:
            if self.signing_check_label:
                self.signing_check_label.text = "jarsigner & zipalign OK"
                self.signing_check_label.color = (0.3, 0.9, 0.4, 1)
        else:
            if self.signing_check_label:
                self.signing_check_label.text = "jarsigner/zipalign Not Found"
                self.signing_check_label.color = (0.9, 0.3, 0.3, 1)
            missing = detail or "<jarsigner>,<zipalign>"
            message = (
                f"{missing} Not Found\n"
                f"{missing} should be installed in WSL and added to PATH.\n"
                "This is required for Signing Android App Action only"
            )
            show_error_dialog("Signing Tools Check", message)

    def save(self):
        new_name = self.name_input.text.strip()

        if not new_name:
            show_error_dialog("Cannot Save", "Profile name cannot be empty.")
            return

        profiles = ProfileStore.load_all()
        name_taken = any(p.name == new_name for p in profiles)

        if self._editing_profile is None:
            if name_taken:
                show_error_dialog("Cannot Save", f'A profile named "{new_name}" already exists.')
                return
            updated = self._build_profile(new_name)
            profiles.append(updated)
        else:
            if name_taken and new_name != self._orig_name:
                show_error_dialog("Cannot Save", f'A profile named "{new_name}" already exists.')
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

    def show_help(self):
        show_help_popup(
            "Profile Editor Help",
            "This screen lets you create and edit build profiles.\n\n"
            "- Name: A unique identifier for this profile.\n"
            "- Source Directory: Path to your Buildozer project folder.\n"
            "- buildozer.spec path: Location of the buildozer.spec file.\n"
            "- ADB path: Path to adb.exe for Android debugging.\n"
            "- Excluded files: Files/directories to exclude (comma-separated).\n"
            "- Patches: Select patches to apply with this profile.\n"
            "- WSL settings: Configuration for Windows Subsystem for Linux.\n"
            "- Path to certificate / Password: Used by the Signing Android App action for signing AABs.\n"
            "- 'Check jarsigner and zipalign' verifies both tools are installed in WSL (required for signing only).\n"
            "- Click 'Save' to persist the profile, 'Cancel' to discard changes."
        )

    def cancel(self):
        if self.manager:
            self.manager.current = "actions"

    @property
    def on_profile_updated(self):
        return getattr(self, "_on_profile_updated", None)

    @on_profile_updated.setter
    def on_profile_updated(self, callback):
        self._on_profile_updated = callback
