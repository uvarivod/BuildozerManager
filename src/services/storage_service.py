import json
from pathlib import Path

from src.models.action import Action
from src.models.profile import Profile
from src.models.scenario import Scenario

_PROFILE_FIELDS = {"name", "sourcedir", "spec_path", "adb_path", "excluded_files", "wsl_dir", "wsl_distro", "patches", "delete_exclusions"}

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(filename: str) -> dict | list:
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


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
            return [
                Profile(**{k: v for k, v in item.items() if k in _PROFILE_FIELDS})
                for item in data
            ]
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
    def save(profile: Profile):
        profiles = ProfileStore.load_all()
        for i, p in enumerate(profiles):
            if p.name == profile.name:
                profiles[i] = profile
                break
        else:
            profiles.append(profile)
        ProfileStore.save_all(profiles)

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
    def load_all() -> list[Scenario]:
        data = _read_json("scenarios.json")
        if not isinstance(data, list):
            return []
        result = []
        for item in data:
            try:
                action_names = item.get("action_sequence", [])
                sequence = []
                for name in action_names:
                    try:
                        sequence.append(Action[name])
                    except KeyError:
                        pass
                custom_names = item.get("custom_action_names", {})
                custom_names = {int(k): v for k, v in custom_names.items()}
                result.append(Scenario(
                    name=item.get("name", ""),
                    description=item.get("description", ""),
                    action_sequence=sequence,
                    custom_action_names=custom_names,
                    stop_on_failure=item.get("stop_on_failure", True),
                    is_predefined=False,
                ))
            except Exception:
                continue
        return result

    @staticmethod
    def save_all(scenarios: list[Scenario]):
        _write_json("scenarios.json", [
            {
                "name": s.name,
                "description": s.description,
                "action_sequence": [a.name for a in s.action_sequence],
                "custom_action_names": {str(k): v for k, v in s.custom_action_names.items()},
                "stop_on_failure": s.stop_on_failure,
            }
            for s in scenarios
        ])

    @staticmethod
    def save(scenario: Scenario):
        scenarios = ScenarioStore.load_all()
        for i, s in enumerate(scenarios):
            if s.name == scenario.name:
                scenarios[i] = scenario
                break
        else:
            scenarios.append(scenario)
        ScenarioStore.save_all(scenarios)

    @staticmethod
    def delete(name: str):
        scenarios = ScenarioStore.load_all()
        scenarios = [s for s in scenarios if s.name != name]
        ScenarioStore.save_all(scenarios)

    @staticmethod
    def get(name: str) -> Scenario | None:
        scenarios = ScenarioStore.load_all()
        return next((s for s in scenarios if s.name == name), None)


class CustomActionStore:

    @staticmethod
    def load_all() -> list:
        from src.models.custom_action import CustomAction, ActionType
        data = _read_json("custom_actions.json")
        if not isinstance(data, list):
            return []
        result = []
        for item in data:
            try:
                type_val = ActionType[item.get("type", "ACTION")]
                result.append(CustomAction(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    description=item.get("description", ""),
                    type=type_val,
                    logic=item.get("logic", ""),
                    is_builtin=item.get("is_builtin", False),
                ))
            except Exception:
                continue
        return result

    @staticmethod
    def save_all(actions: list):
        from src.models.custom_action import ActionType
        _write_json("custom_actions.json", [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "type": a.type.name,
                "logic": a.logic,
                "is_builtin": a.is_builtin,
            }
            for a in actions
        ])

    @staticmethod
    def save(action) -> None:
        actions = CustomActionStore.load_all()
        for i, a in enumerate(actions):
            if a.id == action.id:
                actions[i] = action
                break
        else:
            actions.append(action)
        CustomActionStore.save_all(actions)

    @staticmethod
    def delete(action_id: str) -> None:
        actions = CustomActionStore.load_all()
        actions = [a for a in actions if a.id != action_id]
        CustomActionStore.save_all(actions)


class SettingsStore:
    _SETTINGS_FILE = "settings.json"

    @staticmethod
    def load() -> dict:
        _ensure_data_dir()
        path = DATA_DIR / SettingsStore._SETTINGS_FILE
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    @staticmethod
    def save(settings: dict):
        _ensure_data_dir()
        path = DATA_DIR / SettingsStore._SETTINGS_FILE
        existing = {}
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        existing.update(settings)
        path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
