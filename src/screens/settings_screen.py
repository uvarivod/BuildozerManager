from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from pathlib import Path

from src.services.storage_service import SettingsStore
from src.services.log_service import LogService
from src.screens.help_popup import show_help_popup


DEFAULT_LOG_DIR = "logs"
DEFAULT_MAX_LOG_SIZE_MB = 100


class SettingsScreen(Screen):
    log_dir_input = ObjectProperty(None)
    max_log_size_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._log = LogService()

    def on_enter(self, *args):
        self._load_settings()

    def _load_settings(self):
        settings = SettingsStore.load()
        log_dir = settings.get("log_dir", DEFAULT_LOG_DIR)
        max_size = settings.get("max_log_size_mb", DEFAULT_MAX_LOG_SIZE_MB)
        if self.log_dir_input:
            self.log_dir_input.text = log_dir
        if self.max_log_size_input:
            self.max_log_size_input.text = str(max_size)

    def show_help(self):
        show_help_popup(
            "Settings Help",
            "Configure application settings.\n\n"
            "- Log Directory: Path where session log files are saved.\n"
            "  Default: 'logs'. The directory is created if it doesn't exist.\n"
            "- Max Log Size (MB): Maximum size of the log directory before\n"
            "  oldest logs are automatically deleted.\n"
            "  Default: 100 MB.\n\n"
            "Click 'Save' to apply changes. Settings persist across restarts."
        )

    def save(self):
        log_dir = self.log_dir_input.text.strip() if self.log_dir_input else DEFAULT_LOG_DIR
        max_size_str = self.max_log_size_input.text.strip() if self.max_log_size_input else ""

        if not log_dir:
            self._show_error("Log directory path cannot be empty.")
            return

        try:
            max_size = int(max_size_str) if max_size_str else DEFAULT_MAX_LOG_SIZE_MB
            if max_size <= 0:
                self._show_error("Max log size must be a positive number.")
                return
        except ValueError:
            self._show_error("Max log size must be a valid number.")
            return

        try:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self._show_error(f"Cannot create log directory:\n{e}")
            return

        SettingsStore.save({
            "log_dir": log_dir,
            "max_log_size_mb": max_size,
        })
        self._log.info(f"Settings saved: log_dir={log_dir}, max_log_size_mb={max_size}")
        self._show_success("Settings saved successfully.")

    def on_back(self):
        if self.manager:
            self.manager.current = "actions"

    def _show_error(self, message: str):
        content = BoxLayout(orientation="vertical", spacing='10dp', padding='10dp')
        content.add_widget(Label(text=message))
        btn_box = BoxLayout(spacing='10dp', size_hint_y=None, height='40dp')
        popup = Popup(title="Error", content=content, size_hint=(0.5, 0.3))
        btn_box.add_widget(Button(text="OK", on_release=lambda *_: popup.dismiss()))
        content.add_widget(btn_box)
        popup.open()

    def _show_success(self, message: str):
        content = BoxLayout(orientation="vertical", spacing='10dp', padding='10dp')
        content.add_widget(Label(text=message))
        btn_box = BoxLayout(spacing='10dp', size_hint_y=None, height='40dp')
        popup = Popup(title="Saved", content=content, size_hint=(0.4, 0.2))
        btn_box.add_widget(Button(text="OK", on_release=lambda *_: popup.dismiss()))
        content.add_widget(btn_box)
        popup.open()
