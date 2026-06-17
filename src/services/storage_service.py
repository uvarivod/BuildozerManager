import json
from pathlib import Path

from src.models.action import Action
from src.models.profile import Profile


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(filename: str) -> dict | list:
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(filename: str, data: dict | list):
    _ensure_data_dir()
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)


class ProfileStore:

    @staticmethod
    def load_all() -> list[Profile]:
        data = _read_json("profiles.json")
        if isinstance(data, list):
            return [Profile(**item) for item in data]
        return []

    @staticmethod
    def save_all(profiles: list[Profile]):
        _write_json("profiles.json", [
            {
                "name": p.name,
                "sourcedir": p.sourcedir,
                "spec_path": p.spec_path,
                "adb_path": p.adb_path,
                "excluded_files": p.excluded_files,
                "wsl_dir": p.wsl_dir,
                "wsl_distro": p.wsl_distro,
                "patches": p.patches,
                "delete_exclusions": p.delete_exclusions,
            }
            for p in profiles
        ])

    @staticmethod
    def delete(name: str):
        profiles = ProfileStore.load_all()
        profiles = [p for p in profiles if p.name != name]
        ProfileStore.save_all(profiles)


class SettingsStore:

    @staticmethod
    def load() -> dict:
        return _read_json("settings.json")

    @staticmethod
    def save(settings: dict):
        existing = SettingsStore.load()
        existing.update(settings)
        _write_json("settings.json", existing)


class ScenarioStore:

    @staticmethod
    def load_all() -> list[dict]:
        data = _read_json("scenarios.json")
        if isinstance(data, list):
            return data
        return []

    @staticmethod
    def save_all(scenarios: list[dict]):
        _write_json("scenarios.json", scenarios)
