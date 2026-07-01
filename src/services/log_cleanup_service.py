from pathlib import Path
from src.services.storage_service import SettingsStore


DEFAULT_LOG_DIR = "logs"
DEFAULT_MAX_SIZE_MB = 100


def cleanup_logs(log_dir: str | None = None, max_size_mb: int | None = None, skip_file: str | None = None):
    settings = SettingsStore.load()
    if log_dir is None:
        log_dir = settings.get("log_dir", DEFAULT_LOG_DIR)
    if max_size_mb is None:
        max_size_mb = settings.get("max_log_size_mb", DEFAULT_MAX_SIZE_MB)

    log_path = Path(log_dir)
    if not log_path.is_dir():
        return

    max_size_bytes = max_size_mb * 1024 * 1024

    files = []
    total_size = 0
    for f in log_path.iterdir():
        if not f.is_file():
            continue
        if skip_file and str(f.resolve()) == str(Path(skip_file).resolve()):
            total_size += f.stat().st_size
            continue
        files.append(f)
        total_size += f.stat().st_size

    if total_size <= max_size_bytes:
        return

    files.sort(key=lambda f: f.stat().st_mtime)

    for f in files:
        if total_size <= max_size_bytes:
            break
        try:
            file_size = f.stat().st_size
            f.unlink()
            total_size -= file_size
        except OSError:
            pass
