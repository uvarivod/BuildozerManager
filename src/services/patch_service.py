import subprocess
from collections.abc import Callable
from pathlib import Path

from src.models.patch import PatchRegistry
from src.services.storage_service import CustomActionStore


class PatchService:
    def apply_patches(
        self,
        patch_names: list[str],
        buildozer_path: Path,
        log_callback: Callable | None = None,
        profile=None,
    ) -> bool:
        all_success = True
        for name in patch_names:
            func = PatchRegistry.get(name)
            if func is None:
                custom_actions = CustomActionStore.load_all()
                ca = next((c for c in custom_actions if c.name == name), None)
                if ca and ca.logic:
                    script = Path(ca.logic)
                    if script.is_file():
                        if log_callback:
                            log_callback("info", f"Starting custom patch script: {ca.logic}")
                        try:
                            result = subprocess.run(
                                ["cmd.exe", "/c", str(script)],
                                capture_output=True,
                                text=True,
                                timeout=3600,
                            )
                            out = (result.stdout or "").strip()
                            err = (result.stderr or "").strip()
                            err_lines = [l for l in err.split('\n') if l and 'Input redirection is not supported' not in l]
                            if out:
                                if log_callback:
                                    log_callback("info", out)
                            if err_lines:
                                if log_callback:
                                    log_callback("warn", '\n'.join(err_lines))
                            if result.returncode == 0:
                                if log_callback:
                                    log_callback("success", f"Custom patch '{name}' completed")
                            else:
                                if log_callback:
                                    log_callback("error", f"Custom patch '{name}' failed with code {result.returncode}")
                                all_success = False
                        except subprocess.TimeoutExpired:
                            if log_callback:
                                log_callback("error", f"Custom patch '{name}' timed out")
                            all_success = False
                        except Exception as e:
                            if log_callback:
                                log_callback("error", f"Custom patch '{name}' error: {e}")
                            all_success = False
                        continue
                if log_callback:
                    log_callback("warn", f"Patch '{name}' not found, skipping")
                continue

            try:
                if log_callback:
                    log_callback("info", f"Applying patch: {name}")
                result = func(buildozer_path, profile=profile, log_callback=log_callback)
                if result is False:
                    if log_callback:
                        log_callback("error", f"Patch '{name}' reported failure")
                    all_success = False
                else:
                    if log_callback:
                        log_callback("success", f"Patch '{name}' applied")
            except Exception as e:
                if log_callback:
                    log_callback("error", f"Patch '{name}' failed: {e}")
                all_success = False

        return all_success
