from collections.abc import Callable
from pathlib import Path

from src.models.patch import PatchRegistry


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
