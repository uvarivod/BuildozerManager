import threading
from collections.abc import Callable
from pathlib import Path

from src.models.action import Action, ActionState
from src.models.profile import Profile
from src.services.wsl_service import WSLService
from src.services.adb_service import ADBService
from src.services.patch_service import PatchService
from src.services.log_service import LogService, LogLevel


class ActionRunner:
    def __init__(self):
        self._wsl = WSLService()
        self._adb = ADBService()
        self._patches = PatchService()
        self._log = LogService()
        self._cancel_event = threading.Event()

    def cancel(self):
        self._cancel_event.set()

    def reset_cancel(self):
        self._cancel_event.clear()

    def _check_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def _make_log_callback(self, source: str = ""):
        def cb(level: str, message: str, src: str = ""):
            level_map = {
                "debug": LogLevel.DEBUG,
                "info": LogLevel.INFO,
                "warn": LogLevel.WARN,
                "error": LogLevel.ERROR,
                "success": LogLevel.SUCCESS,
            }
            self._log.log(level_map.get(level, LogLevel.INFO), message, source=src or source)
        return cb

    @staticmethod
    def validate_action(action: Action, profile: Profile) -> list[str]:
        required = {
            Action.CLEAN: ["wsl_dir", "wsl_distro"],
            Action.BUILD: ["sourcedir", "spec_path", "wsl_dir", "wsl_distro"],
            Action.PATCH: ["wsl_dir", "wsl_distro"],
            Action.DOWNLOAD: ["sourcedir", "wsl_dir", "wsl_distro"],
            Action.RUN: ["sourcedir", "spec_path", "wsl_dir", "wsl_distro", "adb_path"],
        }
        missing = []
        for field in required.get(action, []):
            if not getattr(profile, field, ""):
                missing.append(field)
        return missing

    def run_action(
        self, action: Action, profile: Profile
    ) -> ActionState:
        self.reset_cancel()
        log_cb = self._make_log_callback(action.name.lower())

        missing = self.validate_action(action, profile)
        if missing:
            log_cb("error", f"Cannot run {action.name}: missing {', '.join(missing)}")
            return ActionState.FAILED

        if action == Action.CLEAN:
            return self._run_clean(profile, log_cb)
        elif action == Action.BUILD:
            return self._run_build(profile, log_cb)
        elif action == Action.PATCH:
            return self._run_patch(profile, log_cb)
        elif action == Action.DOWNLOAD:
            return self._run_download(profile, log_cb)
        elif action == Action.RUN:
            return self._run_launch(profile, log_cb)
        return ActionState.FAILED

    def _run_clean(self, profile: Profile, log_cb) -> ActionState:
        log_cb("info", "Starting Clean...")
        if not self._wsl.check_wsl_running(profile):
            log_cb("error", "WSL is not running")
            return ActionState.FAILED
        ok = self._wsl.clean_wsl_dir(profile, log_cb, self._check_cancelled)
        if self._check_cancelled():
            return ActionState.CANCELLED
        log_cb("success" if ok else "error", "Clean finished")
        return ActionState.SUCCESS if ok else ActionState.FAILED

    def _run_build(self, profile: Profile, log_cb) -> ActionState:
        log_cb("info", "Starting Build...")
        if not self._wsl.check_wsl_running(profile):
            log_cb("error", "WSL is not running")
            return ActionState.FAILED

        log_cb("info", "Cleaning WSL directory (preserving .buildozer)...")

        original_exclusions = list(profile.delete_exclusions)
        if ".buildozer" not in profile.delete_exclusions:
            profile.delete_exclusions.append(".buildozer")
        clean_ok = self._wsl.clean_wsl_dir(profile, log_cb, self._check_cancelled)
        profile.delete_exclusions = original_exclusions

        if self._check_cancelled():
            return ActionState.CANCELLED
        if not clean_ok:
            log_cb("error", "Clean failed, aborting build")
            return ActionState.FAILED

        log_cb("info", "Copying source to WSL...")
        copy_ok = self._wsl.copy_source_to_wsl(profile, log_cb, self._check_cancelled)
        if self._check_cancelled():
            return ActionState.CANCELLED
        if not copy_ok:
            log_cb("error", "Copy failed, aborting build")
            return ActionState.FAILED

        log_cb("info", "Running buildozer...")
        build_ok = self._wsl.exec_buildozer(profile, log_callback=log_cb, cancel_check=self._check_cancelled)
        if self._check_cancelled():
            return ActionState.CANCELLED
        log_cb("success" if build_ok else "error", "Build finished")
        return ActionState.SUCCESS if build_ok else ActionState.FAILED

    def _run_patch(self, profile: Profile, log_cb) -> ActionState:
        log_cb("info", "Starting Patch...")
        buildozer_path = self._wsl._wsl_path(profile) / ".buildozer"
        if not buildozer_path.is_dir():
            log_cb("error", ".buildozer directory not found in WSL")
            return ActionState.FAILED

        patches_to_apply = profile.patches
        if not patches_to_apply:
            log_cb("info", "No patches configured for this profile")
            return ActionState.SUCCESS

        result = self._patches.apply_patches(patches_to_apply, buildozer_path, log_cb)
        if self._check_cancelled():
            return ActionState.CANCELLED
        return ActionState.SUCCESS if result else ActionState.FAILED

    def _run_download(self, profile: Profile, log_cb) -> ActionState:
        log_cb("info", "Looking for APK in WSL...")
        apks = self._wsl.find_apk_in_wsl(profile)
        if not apks:
            log_cb("error", "No APK found in WSL .buildozer directory")
            return ActionState.FAILED

        latest = apks[0]
        log_cb("info", f"Found APK: {latest.name}")

        import shutil
        dest = Path(profile.sourcedir) / "bin"
        try:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(latest, dest / latest.name)
            log_cb("success", f"APK copied to {dest / latest.name}")
            return ActionState.SUCCESS
        except Exception as e:
            log_cb("error", f"Failed to copy APK: {e}")
            return ActionState.FAILED

    def _run_launch(self, profile: Profile, log_cb) -> ActionState:
        log_cb("info", "Starting Run action...")
        devices = self._adb.list_devices(profile.adb_path)
        if not devices:
            log_cb("error", "No ADB devices connected")
            return ActionState.FAILED

        apks = self._wsl.find_apk_in_wsl(profile)
        if not apks:
            log_cb("error", "No APK found. Build first.")
            return ActionState.FAILED

        latest = apks[0]
        dest_path = str(Path(profile.sourcedir) / "bin" / latest.name)
        if not Path(dest_path).exists():
            dl_result = self._run_download(profile, log_cb)
            if dl_result != ActionState.SUCCESS:
                return dl_result

        install_ok = self._adb.install_apk(profile.adb_path, dest_path, log_cb)
        if not install_ok:
            return ActionState.FAILED

        launch_ok = self._adb.launch_app(profile.adb_path, "", log_callback=log_cb)
        log_cb("success" if launch_ok else "error", "Launch finished")
        return ActionState.SUCCESS if launch_ok else ActionState.FAILED
