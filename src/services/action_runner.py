import threading
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from src.models.action import Action, ActionState
from src.models.profile import Profile
from src.services.wsl_service import WSLService
from src.services.adb_service import ADBService
from src.services.apk_service import APKService
from src.services.patch_service import PatchService
from src.services.log_service import LogService, LogLevel


class ActionRunner:
    def __init__(self):
        self._wsl = WSLService()
        self._adb = ADBService()
        self._apk = APKService()
        self._patches = PatchService()
        self._log = LogService()
        self._cancel_event = threading.Event()

    def cancel(self):
        self._cancel_event.set()

    def reset_cancel(self):
        self._cancel_event.clear()

    def _check_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def _make_log_callback(self, default_source: str = ""):
        def cb(level: str, message: str, source: str = "", replace_last: bool = False):
            level_map = {
                "debug": LogLevel.DEBUG,
                "info": LogLevel.INFO,
                "warn": LogLevel.WARN,
                "error": LogLevel.ERROR,
                "success": LogLevel.SUCCESS,
            }
            self._log.log(level_map.get(level, LogLevel.INFO), message, source=source or default_source, replace_last=replace_last)
        return cb

    @staticmethod
    def validate_action(action: Action, profile: Profile) -> list[str]:
        required = {
            Action.SYNC_SRC: ["sourcedir", "wsl_dir", "wsl_distro"],
            Action.CLEAN: ["wsl_dir", "wsl_distro"],
            Action.BUILD: ["sourcedir", "wsl_dir", "wsl_distro"],
            Action.PATCH: ["wsl_dir", "wsl_distro"],
            Action.PULL_APK: ["sourcedir", "wsl_dir", "wsl_distro"],
            Action.RUN: ["sourcedir", "spec_path", "wsl_dir", "wsl_distro", "adb_path"],
        }
        missing = []
        for field in required.get(action, []):
            if not getattr(profile, field, ""):
                missing.append(field)
        return missing

    def run_action(
        self, action: Action, profile: Profile,
        on_state_change: Callable[[ActionState], None] | None = None,
    ) -> ActionState:
        self.reset_cancel()
        if on_state_change:
            on_state_change(ActionState.RUNNING)
        log_cb = self._make_log_callback(action.name.lower())

        missing = self.validate_action(action, profile)
        if missing:
            log_cb("error", f"Cannot run {action.name}: missing {', '.join(missing)}")
            return ActionState.FAILED

        if action == Action.SYNC_SRC:
            return self._run_sync_src(profile, log_cb)
        elif action == Action.CLEAN:
            return self._run_clean(profile, log_cb)
        elif action == Action.BUILD:
            return self._run_build(profile, log_cb)
        elif action == Action.PATCH:
            return self._run_patch(profile, log_cb)
        elif action == Action.PULL_APK:
            return self._run_pull_apk(profile, log_cb)
        elif action == Action.RUN:
            return self._run_launch(profile, log_cb)
        return ActionState.FAILED

    def _run_sync_src(self, profile: Profile, log_cb) -> ActionState:
        log_cb("info", "Starting Sync SRC...")
        if not self._wsl.check_wsl_running(profile):
            log_cb("error", "WSL is not running")
            return ActionState.FAILED
        ok = self._wsl.sync_src(profile, log_cb, self._check_cancelled)
        if self._check_cancelled():
            return ActionState.CANCELLED
        log_cb("success" if ok else "error", "Sync SRC finished")
        return ActionState.SUCCESS if ok else ActionState.FAILED

    def _run_clean(self, profile: Profile, log_cb) -> ActionState:
        log_cb("info", "Starting Clean WSL Project...")
        if not self._wsl.check_wsl_running(profile):
            log_cb("error", "WSL is not running")
            return ActionState.FAILED
        ok = self._wsl.clean_wsl_project(profile, log_cb, self._check_cancelled)
        if self._check_cancelled():
            return ActionState.CANCELLED
        log_cb("success" if ok else "error", "Clean WSL Project finished")
        return ActionState.SUCCESS if ok else ActionState.FAILED

    def _run_build(self, profile: Profile, log_cb) -> ActionState:
        log_cb("info", "Starting Build...")
        if not self._wsl.check_wsl_running(profile):
            log_cb("error", "WSL is not running")
            return ActionState.FAILED

        if not self._wsl.find_spec_in_wsl(profile):
            log_cb("warn", "buildozer.spec not found in WSL build directory")

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

        result = self._patches.apply_patches(patches_to_apply, buildozer_path, log_cb, profile=profile)
        if self._check_cancelled():
            return ActionState.CANCELLED
        return ActionState.SUCCESS if result else ActionState.FAILED

    def run_single_patch(self, patch_name: str, profile: Profile, log_cb) -> ActionState:
        buildozer_path = self._wsl._wsl_path(profile) / ".buildozer"
        if not buildozer_path.is_dir():
            log_cb("error", ".buildozer directory not found in WSL")
            return ActionState.FAILED

        result = self._patches.apply_patches([patch_name], buildozer_path, log_cb, profile=profile)
        return ActionState.SUCCESS if result else ActionState.FAILED

    def _run_pull_apk(self, profile: Profile, log_cb) -> ActionState:
        spec_path = Path(profile.sourcedir) / "buildozer.spec"
        if not spec_path.is_file():
            log_cb("error", f"buildozer.spec not found at {spec_path}")
            return ActionState.FAILED

        bin_dir = Path(f"\\\\wsl$\\{profile.wsl_distro}") / profile.wsl_dir.lstrip("/") / "bin"
        log_cb("info", f"Searching for file under {bin_dir}")
        latest = self._apk.find_latest_apk(profile)
        if not latest:
            log_cb("info", "Missed")
            if bin_dir.is_dir():
                files = [p.name for p in sorted(bin_dir.iterdir())]
                if files:
                    log_cb("info", "Files in folder: " + ", ".join(files))
            return ActionState.FAILED

        log_cb("info", f"{latest.name} .. FOUND")

        import shutil
        dest = Path(profile.sourcedir) / "bin"
        dest_path = dest / latest.name
        replaced = dest_path.exists()
        try:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(latest, dest_path)
            msg = "Replaced with new" if replaced else "SUCCESS"
            log_cb("success", f"Copying to {dest_path} .. {msg}")
            return ActionState.SUCCESS
        except Exception as e:
            log_cb("error", f"Copying to {dest_path} .. FAILED ({e})")
            return ActionState.FAILED

    def _run_launch(self, profile: Profile, log_cb) -> ActionState:
        log_cb("info", "Starting Run action...")

        spec_path = Path(profile.sourcedir) / "buildozer.spec"
        if not spec_path.is_file():
            log_cb("error", f"buildozer.spec not found at {spec_path} — cannot determine package name")
            return ActionState.FAILED

        package_name = self._apk.get_package_name(profile)
        if not package_name:
            log_cb("error", "Could not determine package name from buildozer.spec")
            return ActionState.FAILED
        log_cb("info", f"Package name: {package_name}")

        log_cb("info", f"Checking connected ADB devices using: {profile.adb_path}")
        devices, err = self._adb.list_devices(profile.adb_path, log_cb)
        if err:
            log_cb("error", err)
            return ActionState.FAILED
        if not devices:
            log_cb("error", "No ADB devices connected")
            return ActionState.FAILED

        log_cb("info", f"Found {len(devices)} device(s):")
        for d in devices:
            log_cb("info", f"  {d['serial']} ({d['state']})")

        device_serial = devices[0]["serial"]
        if len(devices) > 1:
            log_cb("info", f"Multiple devices detected — using first: {device_serial}")
        else:
            log_cb("info", f"Using device: {device_serial}")

        latest = self._apk.find_latest_apk(profile)
        if not latest:
            log_cb("error", "No matching APK found in WSL. Build or pull APK first.")
            return ActionState.FAILED

        dest_path = str(Path(profile.sourcedir) / "bin" / latest.name)
        if not Path(dest_path).exists():
            log_cb("info", f"APK not found locally, pulling from WSL first...")
            dl_result = self._run_pull_apk(profile, log_cb)
            if dl_result != ActionState.SUCCESS:
                return dl_result

        log_cb("info", f"Installing APK from: {dest_path}")
        install_ok = self._adb.install_apk(profile.adb_path, dest_path, log_cb, device_serial=device_serial)
        if not install_ok:
            return ActionState.FAILED

        log_cb("info", f"Launching {package_name} on device {device_serial}...")
        launch_ok = self._adb.launch_app(profile.adb_path, package_name, log_callback=log_cb, device_serial=device_serial)
        log_cb("success" if launch_ok else "error", "Launch finished")
        return ActionState.SUCCESS if launch_ok else ActionState.FAILED
