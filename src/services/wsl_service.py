import os
import queue
import re
import shlex
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path

from src.models.profile import Profile


class WSLService:
    def __init__(self):
        self._lock = threading.Lock()

    def _wsl_path(self, profile: Profile) -> Path:
        return Path(f"\\\\wsl$\\{profile.wsl_distro}") / profile.wsl_dir.lstrip("/")

    @staticmethod
    def _linux_dir(profile: Profile) -> str:
        wsl_dir = profile.wsl_dir
        if "\\" in wsl_dir:
            parts = wsl_dir.split("\\")
            try:
                idx = parts.index(profile.wsl_distro)
                return "/" + "/".join(parts[idx + 1:])
            except ValueError:
                pass
        return wsl_dir.lstrip("/")

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

        excluded = set(profile.excluded_files)
        excluded_wild = [e.lstrip("*") for e in excluded if e.startswith("*")]

        total = 0
        for root, dirs, files in src.walk():
            if cancel_check and cancel_check():
                if log_callback:
                    log_callback("warn", "Copy cancelled")
                return False
            dirs[:] = [d for d in dirs if d not in excluded and not any(
                d.endswith(w) for w in excluded_wild
            )]
            rel = Path(root).relative_to(src)
            target = dst / rel
            try:
                target.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            for f in files:
                if f in excluded or any(f.endswith(w) for w in excluded_wild):
                    continue
                shutil.copy2(Path(root) / f, target / f)
                total += 1
                if log_callback:
                    log_callback("debug", f"Copied {rel / f}")
            time.sleep(0)

        if log_callback:
            log_callback("info", f"Copied {total} files to WSL")
        return True

    def _wsl_delete(self, profile: Profile, linux_path: str) -> bool:
        try:
            result = subprocess.run(
                ["wsl.exe", "--distribution", profile.wsl_distro,
                 "--exec", "bash", "-c", 'rm -rf "$1"', "_", linux_path],
                capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False

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

        linux_dir = self._linux_dir(profile)
        exclusions = set(profile.delete_exclusions)
        deleted = 0
        for item in wsl_path.iterdir():
            if cancel_check and cancel_check():
                if log_callback:
                    log_callback("warn", "Clean cancelled")
                return False
            if item.name in exclusions:
                if log_callback:
                    log_callback("debug", f"Skipping: {item.name}")
                continue
            try:
                ok = self._wsl_delete(profile, f"{linux_dir}/{item.name}")
                if ok:
                    deleted += 1
                    if log_callback:
                        log_callback("debug", f"Deleted {item.name}")
                else:
                    if log_callback:
                        log_callback("error", f"Failed to delete {item.name}")
            except Exception as e:
                if log_callback:
                    log_callback("error", f"Failed to delete {item.name}: {e}")
            time.sleep(0)

        if log_callback:
            log_callback("info", f"Cleaned {deleted} items from WSL directory")
        return True

    _ANSI_RE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    @classmethod
    def _strip_ansi(cls, text: str) -> str:
        return cls._ANSI_RE.sub('', text)

    _NOISE_RE = re.compile(
        r'^stty:'
        r'|^-> running rm -f'
    )

    _TOOL_CMDS_RE = re.compile(
        r'^(?:gcc|g\+\+|ld|ar|mkdir|cp|rm|chmod|ln|python[23]|configure|autoconf|cmake|ninja|ccache)'
    )

    _GCC_CONT_RE = re.compile(r'^-[a-zA-Z]')

    def _parse_buildozer_line(self, line: str) -> tuple[str, str] | None:
        stripped = self._strip_ansi(line).strip()
        if not stripped or self._NOISE_RE.match(stripped):
            return None
        step = re.match(r"^# (.+)", stripped)
        if step:
            return ("info", f"Step: {step.group(1)}")
        info = re.match(r"^\[INFO\]:?\s*(.*)", stripped, re.IGNORECASE)
        if info:
            return ("info", info.group(1))
        warn = re.match(r"^\[WARN(?:ING)?\]:?\s*(.*)", stripped, re.IGNORECASE)
        if warn:
            return ("warn", warn.group(1))
        err = re.match(r"^\[ERROR\]:?\s*(.*)", stripped, re.IGNORECASE)
        if err:
            return ("error", err.group(1))
        return ("debug", stripped)

    def exec_buildozer(
        self, profile: Profile,
        command: str = "buildozer android debug",
        log_callback=None,
        cancel_check=None
    ):
        tmp_path = None
        try:
            linux_dir = self._linux_dir(profile)
            inner = f"export PATH=$PATH:~/.local/bin/; cd {linux_dir} && {command}"

            tmp = tempfile.NamedTemporaryFile(prefix="buildozer_", suffix=".out", delete=False, mode='w')
            tmp_path = tmp.name
            tmp.close()

            drive_letter = tmp_path[0].lower()
            wsl_tmp_path = f"/mnt/{drive_letter}{tmp_path[2:].replace(chr(92), '/')}"
            shell_cmd = f"script -q -c {shlex.quote(inner)} /dev/null > {shlex.quote(wsl_tmp_path)} 2>&1"

            if log_callback:
                log_callback("debug", f"WSL build dir: {linux_dir}", source="buildozer")
                log_callback("debug", f"Running: {inner}", source="buildozer")

            process = subprocess.Popen(
                [
                    "wsl.exe",
                    "--distribution", profile.wsl_distro,
                    "--exec", "bash", "-c", shell_cmd,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            line_queue: queue.Queue[str | None] = queue.Queue()

            def file_reader():
                last_pos = 0
                leftover = ""
                while process.poll() is None:
                    try:
                        current_size = os.path.getsize(tmp_path)
                    except OSError:
                        current_size = last_pos
                    if current_size > last_pos:
                        try:
                            with open(tmp_path, 'r', encoding='utf-8', errors='replace') as f:
                                f.seek(last_pos)
                                data = f.read(current_size - last_pos)
                            last_pos = current_size
                        except OSError:
                            time.sleep(0.05)
                            continue
                        lines = (leftover + data).split('\n')
                        leftover = lines[-1]
                        for line in lines[:-1]:
                            line_queue.put(line + '\n')
                    else:
                        time.sleep(0.05)
                try:
                    with open(tmp_path, 'r', encoding='utf-8', errors='replace') as f:
                        f.seek(last_pos)
                        remaining = f.read()
                    lines = (leftover + remaining).split('\n')
                    for line in lines:
                        line_queue.put(line + '\n')
                except OSError:
                    pass
                line_queue.put(None)

            reader_thread = threading.Thread(target=file_reader, daemon=True)
            reader_thread.start()

            lines_read = 0
            _progress_state: dict[str, int] = {}
            _last_line_time = time.monotonic()
            _last_heartbeat = 0.0
            while True:
                if cancel_check and cancel_check():
                    process.kill()
                    if log_callback:
                        log_callback("warn", "Build cancelled by user")
                    return False
                try:
                    line = line_queue.get(timeout=0.5)
                except queue.Empty:
                    now = time.monotonic()
                    if log_callback and now - _last_heartbeat >= 60:
                        elapsed = int(now - _last_line_time)
                        mins = elapsed // 60
                        secs = elapsed % 60
                        if lines_read > 0:
                            log_callback("debug", f"⏱ Still working... ({mins}:{secs:02d} since last output)", source="buildozer", replace_last=True)
                        _last_heartbeat = now
                    if lines_read > 0 and now - _last_line_time > 900:
                        if log_callback:
                            log_callback("error", "Build timed out — no output for 15 minutes")
                        process.kill()
                        return False
                    continue
                if line is None:
                    break
                _last_line_time = time.monotonic()
                lines_read += 1
                if log_callback:
                    raw = self._strip_ansi(line).strip()
                    clean = re.sub(r'^\[DEBUG\]:\s*', '', raw).strip()

                    if re.match(r'^-\s+Download \d+ bytes', clean):
                        continue
                    dl_pct_match = re.match(r'^-\s+Download ([\d.]+)%', clean)
                    if dl_pct_match:
                        log_callback("debug", f"- Download {dl_pct_match.group(1)}%", source="buildozer", replace_last=True)
                        continue
                    pb_match = re.match(r'^\[ *={0,} *\] (\d+)% (.+)', clean)
                    if pb_match:
                        pct = int(pb_match.group(1))
                        desc = pb_match.group(2).rstrip(".")
                        bucket = (pct // 25) * 25
                        key = f"pb:{desc}"
                        last = _progress_state.get(key)
                        if last is None or bucket != last:
                            _progress_state[key] = bucket
                            log_callback("debug", f"- {desc}... {pct}%", source="buildozer", replace_last=True)
                        elif pct == 100 and last != 100:
                            _progress_state[key] = 100
                            log_callback("debug", f"- {desc}... 100%", source="buildozer", replace_last=True)
                        continue
                    git_match = re.match(r'^((?:remote: )?[A-Za-z][A-Za-z ]+):\s*(\d+)%.*\(\d+/\d+\)', clean)
                    if git_match:
                        verb = git_match.group(1)
                        pct = int(git_match.group(2))
                        bucket = (pct // 25) * 25
                        key = f"git:{verb}"
                        last = _progress_state.get(key)
                        if last is None or bucket != last:
                            _progress_state[key] = bucket
                            log_callback("debug", f"- {verb}: {pct}%", source="buildozer", replace_last=True)
                        elif pct == 100 and last != 100:
                            _progress_state[key] = 100
                            log_callback("debug", f"- {verb}: 100%", source="buildozer", replace_last=True)
                        continue
                    if self._TOOL_CMDS_RE.match(clean) or self._GCC_CONT_RE.match(clean):
                        continue
                    parsed = self._parse_buildozer_line(line)
                    if parsed:
                        level, msg = parsed
                        if level == "debug" and len(msg) > 300:
                            msg = msg[:297] + "..."
                        log_callback(level, msg, source="buildozer")

            process.wait()
            if log_callback:
                log_callback("debug", f"Buildozer exit code: {process.returncode} (lines: {lines_read})", source="buildozer")
            return process.returncode == 0
        except FileNotFoundError:
            if log_callback:
                log_callback("error", "wsl.exe not found. Is WSL installed?")
            return False
        except Exception as e:
            if log_callback:
                log_callback("error", f"Buildozer execution failed: {e}")
            return False
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    def find_spec_in_wsl(self, profile: Profile) -> bool:
        wsl_path = self._wsl_path(profile)
        return (wsl_path / "buildozer.spec").is_file()

    def find_apk_in_wsl(self, profile: Profile) -> list[Path]:
        buildozer_path = self._wsl_path(profile) / ".buildozer"
        if not buildozer_path.is_dir():
            return []
        apks = list(buildozer_path.rglob("*.apk"))
        return sorted(apks, key=lambda p: p.stat().st_mtime, reverse=True)
