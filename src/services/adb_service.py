import subprocess
from pathlib import Path


class ADBService:
    def __init__(self):
        self._last_devices: list[dict] = []

    def _get_adb_cmd(self, adb_path: str, args: list[str]) -> list[str]:
        return [adb_path] + args

    def _run_adb(self, adb_path: str, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
        cmd = self._get_adb_cmd(adb_path, args)
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def list_devices(self, adb_path: str) -> list[dict]:
        try:
            result = self._run_adb(adb_path, ["devices", "-l"], timeout=10)
            if result.returncode != 0:
                return []

            devices = []
            for line in result.stdout.splitlines():
                if line.startswith("List") or line.startswith("*"):
                    continue
                if "\t" in line:
                    parts = line.split()
                    serial = parts[0]
                    state = parts[1] if len(parts) > 1 else "unknown"
                    devices.append({"serial": serial, "state": state})
            self._last_devices = devices
            return devices
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return []

    def install_apk(
        self, adb_path: str, apk_path: str,
        log_callback=None
    ) -> bool:
        if not Path(apk_path).is_file():
            if log_callback:
                log_callback("error", f"APK not found: {apk_path}")
            return False

        try:
            if log_callback:
                log_callback("info", f"Installing {apk_path}...")
            result = self._run_adb(adb_path, ["install", "-r", apk_path], timeout=120)
            output = result.stdout + result.stderr
            if log_callback:
                for line in output.splitlines():
                    log_callback("info", line, source="adb")
            if "Success" in result.stdout:
                if log_callback:
                    log_callback("success", "APK installed successfully")
                return True
            else:
                if log_callback:
                    log_callback("error", "APK installation failed")
                return False
        except subprocess.TimeoutExpired:
            if log_callback:
                log_callback("error", "ADB install timed out")
            return False
        except FileNotFoundError:
            if log_callback:
                log_callback("error", f"ADB not found at: {adb_path}")
            return False
        except Exception as e:
            if log_callback:
                log_callback("error", f"ADB install error: {e}")
            return False

    def launch_app(
        self, adb_path: str, package: str,
        activity: str | None = None,
        log_callback=None
    ) -> bool:
        try:
            if activity:
                cmd = ["shell", "am", "start", "-n", f"{package}/{activity}"]
            else:
                cmd = ["shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"]

            if log_callback:
                log_callback("info", f"Launching {package}...")
            result = self._run_adb(adb_path, cmd, timeout=30)
            output = result.stdout + result.stderr
            if log_callback:
                for line in output.splitlines():
                    if line.strip():
                        log_callback("info", line, source="adb")
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            if log_callback:
                log_callback("error", "ADB launch timed out")
            return False
        except FileNotFoundError:
            if log_callback:
                log_callback("error", f"ADB not found at: {adb_path}")
            return False
        except Exception as e:
            if log_callback:
                log_callback("error", f"ADB launch error: {e}")
            return False
