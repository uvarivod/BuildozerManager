from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from pathlib import Path

from src.services.storage_service import SettingsStore
from src.services.log_service import LogService
from src.screens.dialog_helper import show_error_dialog, show_toast, show_help_popup
from src.screens.file_chooser_helper import FileChooserHelper


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

    def _browse_log_dir(self):
        from pathlib import Path as _Path

        current = self.log_dir_input.text.strip() or DEFAULT_LOG_DIR
        try:
            p = _Path(current)
            initial_path = str(p) if p.is_dir() else str(p.parent)
        except Exception:
            initial_path = "."

        def on_choose(chosen):
            self.log_dir_input.text = chosen

        FileChooserHelper.show_dir_chooser(
            initial_path=initial_path, on_choose=on_choose
        )

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
            show_error_dialog("Error", "Log directory path cannot be empty.")
            return

        try:
            max_size = int(max_size_str) if max_size_str else DEFAULT_MAX_LOG_SIZE_MB
            if max_size <= 0:
                show_error_dialog("Error", "Max log size must be a positive number.")
                return
        except ValueError:
            show_error_dialog("Error", "Max log size must be a valid number.")
            return

        try:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            show_error_dialog("Error", f"Cannot create log directory:\n{e}")
            return

        SettingsStore.save({
            "log_dir": log_dir,
            "max_log_size_mb": max_size,
        })
        self._log.info(f"Settings saved: log_dir={log_dir}, max_log_size_mb={max_size}")
        show_toast("Settings saved successfully.")

    def on_back(self):
        if self.manager:
            self.manager.current = "actions"
