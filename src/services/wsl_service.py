import shutil
import subprocess
import threading
from pathlib import Path

from src.models.profile import Profile


class WSLService:
    def __init__(self):
        self._lock = threading.Lock()

    def _wsl_path(self, profile: Profile) -> Path:
        return Path(f"\\\\wsl$\\{profile.wsl_distro}") / profile.wsl_dir.lstrip("/")

    def _wsl_cmd(self, profile: Profile, command: str) -> list[str]:
        return [
            "wsl.exe",
            "--distribution", profile.wsl_distro,
            "--exec", *command.split()
        ]

    def check_wsl_running(self, profile: Profile) -> bool:
        try:
            result = subprocess.run(
                ["wsl.exe", "--distribution", profile.wsl_distro, "--exec", "echo", "ok"],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def copy_source_to_wsl(
        self, profile: Profile,
        log_callback=None,
        cancel_check=None
    ):
        src = Path(profile.sourcedir)
        dst = self._wsl_path(profile)
        if not src.is_dir():
            if log_callback:
                log_callback("error", f"Source directory does not exist: {src}")
            return False

        try:
            dst.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        def ignore_patterns(dirname, filenames):
            if cancel_check and cancel_check():
                return filenames
            excluded = set(profile.excluded_files)
            return [f for f in filenames if f in excluded or any(
                f.endswith(e.lstrip("*")) for e in excluded if e.startswith("*")
            )]

        total = 0
        for root, dirs, files in src.walk():
            if cancel_check and cancel_check():
                if log_callback:
                    log_callback("warn", "Copy cancelled")
                return False
            rel = Path(root).relative_to(src)
            target = dst / rel
            try:
                target.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            for f in files:
                if any(f.endswith(e.lstrip("*")) for e in profile.excluded_files if e.startswith("*")):
                    continue
                if f in profile.excluded_files:
                    continue
                shutil.copy2(Path(root) / f, target / f)
                total += 1

        if log_callback:
            log_callback("info", f"Copied {total} files to WSL")
        return True

    def clean_wsl_dir(
        self, profile: Profile,
        log_callback=None,
        cancel_check=None
    ):
        wsl_path = self._wsl_path(profile)
        if not wsl_path.is_dir():
            if log_callback:
                log_callback("info", "WSL directory does not exist, nothing to clean")
            return True

        exclusions = set(profile.delete_exclusions)
        deleted = 0
        for item in wsl_path.iterdir():
            if cancel_check and cancel_check():
                if log_callback:
                    log_callback("warn", "Clean cancelled")
                return False
            if item.name in exclusions:
                if log_callback:
                    log_callback("debug", f"Skipping excluded: {item.name}")
                continue
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                deleted += 1
            except Exception as e:
                if log_callback:
                    log_callback("error", f"Failed to delete {item.name}: {e}")

        if log_callback:
            log_callback("info", f"Cleaned {deleted} items from WSL directory")
        return True

    def exec_buildozer(
        self, profile: Profile,
        command: str = "buildozer android debug",
        log_callback=None,
        cancel_check=None
    ):
        try:
            process = subprocess.Popen(
                self._wsl_cmd(profile, f"cd {profile.wsl_dir} && {command}"),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=None,
            )
            for line in iter(process.stdout.readline, ""):
                if cancel_check and cancel_check():
                    process.kill()
                    if log_callback:
                        log_callback("warn", "Build cancelled by user")
                    return False
                if log_callback:
                    log_callback("info", line.rstrip(), source="buildozer")

            process.wait()
            return process.returncode == 0
        except FileNotFoundError:
            if log_callback:
                log_callback("error", "wsl.exe not found. Is WSL installed?")
            return False
        except Exception as e:
            if log_callback:
                log_callback("error", f"Buildozer execution failed: {e}")
            return False

    def find_apk_in_wsl(self, profile: Profile) -> list[Path]:
        buildozer_path = self._wsl_path(profile) / ".buildozer"
        if not buildozer_path.is_dir():
            return []
        apks = list(buildozer_path.rglob("*.apk"))
        return sorted(apks, key=lambda p: p.stat().st_mtime, reverse=True)
