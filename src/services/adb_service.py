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

    def list_devices(self, adb_path: str, log_callback=None) -> tuple[list[dict], str]:
        try:
            if log_callback:
                log_callback("debug", f"Running: {adb_path} devices -l")
            result = self._run_adb(adb_path, ["devices", "-l"], timeout=10)
            if log_callback:
                if result.stdout.strip():
                    log_callback("debug", f"stdout: {result.stdout.strip()}")
                if result.stderr.strip():
                    log_callback("debug", f"stderr: {result.stderr.strip()}")

            if result.returncode != 0:
                err = f"ADB returned exit code {result.returncode}"
                return [], err

            devices = []
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("List") or line.startswith("*"):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    serial = parts[0]
                    state = parts[1]
                    devices.append({"serial": serial, "state": state})
            self._last_devices = devices
            return devices, ""
        except FileNotFoundError:
            return [], f"ADB not found at: {adb_path}"
        except subprocess.TimeoutExpired:
            return [], "ADB devices command timed out"
        except OSError as e:
            return [], f"ADB error: {e}"

    def install_apk(
        self, adb_path: str, apk_path: str,
        log_callback=None,
        device_serial: str | None = None,
    ) -> bool:
        if not Path(apk_path).is_file():
            if log_callback:
                log_callback("error", f"APK not found: {apk_path}")
            return False

        try:
            args = ["install", "-r", apk_path]
            if device_serial:
                args = ["-s", device_serial] + args
            cmd_str = f"{adb_path} {' '.join(args)}"
            if log_callback:
                log_callback("info", f"Installing {apk_path}...")
                log_callback("debug", f"Running: {cmd_str}")
            result = self._run_adb(adb_path, args, timeout=120)
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
        log_callback=None,
        device_serial: str | None = None,
    ) -> bool:
        try:
            if activity:
                cmd = ["shell", "am", "start", "-n", f"{package}/{activity}"]
            else:
                cmd = ["shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"]

            if device_serial:
                cmd = ["-s", device_serial] + cmd
            cmd_str = f"{adb_path} {' '.join(cmd)}"
            device_tag = f" on device {device_serial}" if device_serial else ""
            if log_callback:
                log_callback("info", f"Launching {package}{device_tag}...")
                log_callback("debug", f"Running: {cmd_str}")
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
