import json
from pathlib import Path

import pytest

from src.models.action import Action
from src.models.profile import Profile
from src.models.scenario import Scenario
from src.services import storage_service


@pytest.fixture
def temp_data_dir(monkeypatch, tmp_path):
    storage_service.DATA_DIR = tmp_path
    return tmp_path


class TestProfileStore:
    def test_load_all_empty(self, temp_data_dir):
        profiles = storage_service.ProfileStore.load_all()
        assert profiles == []

    def test_save_and_load(self, temp_data_dir):
        p = Profile(name="p1", sourcedir="/src", delete_exclusions=["custom_cache"])
        storage_service.ProfileStore.save_all([p])

        loaded = storage_service.ProfileStore.load_all()
        assert len(loaded) == 1
        assert loaded[0].name == "p1"
        assert loaded[0].sourcedir == "/src"
        assert loaded[0].delete_exclusions == ["custom_cache"]

    def test_save_multiple(self, temp_data_dir):
        p1 = Profile(name="a")
        p2 = Profile(name="b")
        storage_service.ProfileStore.save_all([p1, p2])

        loaded = storage_service.ProfileStore.load_all()
        assert len(loaded) == 2
        names = {p.name for p in loaded}
        assert names == {"a", "b"}

    def test_delete(self, temp_data_dir):
        p1 = Profile(name="keep")
        p2 = Profile(name="remove")
        storage_service.ProfileStore.save_all([p1, p2])
        storage_service.ProfileStore.delete("remove")

        loaded = storage_service.ProfileStore.load_all()
        assert len(loaded) == 1
        assert loaded[0].name == "keep"

    def test_delete_nonexistent(self, temp_data_dir):
        p = Profile(name="only")
        storage_service.ProfileStore.save_all([p])
        storage_service.ProfileStore.delete("nonexistent")

        loaded = storage_service.ProfileStore.load_all()
        assert len(loaded) == 1

    def test_save_single_updates_existing(self, temp_data_dir):
        p = Profile(name="test", sourcedir="/old")
        storage_service.ProfileStore.save_all([p])

        p.sourcedir = "/new"
        storage_service.ProfileStore.save(p)

        loaded = storage_service.ProfileStore.load_all()
        assert len(loaded) == 1
        assert loaded[0].sourcedir == "/new"

    def test_save_single_appends_new(self, temp_data_dir):
        existing = Profile(name="existing")
        storage_service.ProfileStore.save_all([existing])

        new_p = Profile(name="new")
        storage_service.ProfileStore.save(new_p)

        loaded = storage_service.ProfileStore.load_all()
        assert len(loaded) == 2

    def test_json_structure(self, temp_data_dir):
        p = Profile(
            name="full",
            sourcedir="/src",
            spec_path="/sp",
            adb_path="/adb",
            excluded_files=["*.pyc"],
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
            patches=["fix"],
            delete_exclusions=["custom_cache"],
        )
        storage_service.ProfileStore.save_all([p])

        data_file = temp_data_dir / "profiles.json"
        assert data_file.exists()
        raw = json.loads(data_file.read_text(encoding="utf-8"))
        assert len(raw) == 1
        entry = raw[0]
        assert entry["name"] == "full"
        assert entry["sourcedir"] == "/src"
        assert entry["excluded_files"] == ["*.pyc"]
        assert entry["delete_exclusions"] == ["custom_cache"]
        assert entry["patches"] == ["fix"]


class TestSettingsStore:
    def test_load_default(self, temp_data_dir):
        settings = storage_service.SettingsStore.load()
        assert settings == {}

    def test_save_and_load(self, temp_data_dir):
        storage_service.SettingsStore.save({"key": "value"})
        loaded = storage_service.SettingsStore.load()
        assert loaded["key"] == "value"

    def test_save_merges(self, temp_data_dir):
        storage_service.SettingsStore.save({"a": 1})
        storage_service.SettingsStore.save({"b": 2})
        loaded = storage_service.SettingsStore.load()
        assert loaded["a"] == 1
        assert loaded["b"] == 2

    def test_save_overwrites_same_key(self, temp_data_dir):
        storage_service.SettingsStore.save({"theme": "dark"})
        storage_service.SettingsStore.save({"theme": "light"})
        loaded = storage_service.SettingsStore.load()
        assert loaded["theme"] == "light"


class TestScenarioStore:
    def test_load_all_empty(self, temp_data_dir):
        scenarios = storage_service.ScenarioStore.load_all()
        assert scenarios == []

    def test_save_and_load(self, temp_data_dir):
        scenario = Scenario(
            name="scenario1",
            description="test desc",
            action_sequence=[Action.BUILD],
            stop_on_failure=True,
        )
        storage_service.ScenarioStore.save_all([scenario])
        loaded = storage_service.ScenarioStore.load_all()
        assert len(loaded) == 1
        assert loaded[0].name == "scenario1"
        assert loaded[0].description == "test desc"
        assert loaded[0].action_sequence == [Action.BUILD]

    def test_load_returns_list_only(self, temp_data_dir):
        (temp_data_dir / "scenarios.json").write_text('{"invalid": true}', encoding="utf-8")
        loaded = storage_service.ScenarioStore.load_all()
        assert loaded == []

    def test_save_individual(self, temp_data_dir):
        scenario = Scenario(name="s1", description="d1", action_sequence=[Action.CLEAN])
        storage_service.ScenarioStore.save(scenario)
        loaded = storage_service.ScenarioStore.load_all()
        assert len(loaded) == 1
        assert loaded[0].name == "s1"

    def test_save_updates_existing(self, temp_data_dir):
        s1 = Scenario(name="s1", description="old", action_sequence=[Action.CLEAN])
        storage_service.ScenarioStore.save(s1)
        s1.description = "updated"
        storage_service.ScenarioStore.save(s1)
        loaded = storage_service.ScenarioStore.load_all()
        assert len(loaded) == 1
        assert loaded[0].description == "updated"

    def test_delete_scenario(self, temp_data_dir):
        s1 = Scenario(name="s1", action_sequence=[Action.BUILD])
        s2 = Scenario(name="s2", action_sequence=[Action.CLEAN])
        storage_service.ScenarioStore.save_all([s1, s2])
        storage_service.ScenarioStore.delete("s1")
        loaded = storage_service.ScenarioStore.load_all()
        assert len(loaded) == 1
        assert loaded[0].name == "s2"

    def test_get_scenario_by_name(self, temp_data_dir):
        s1 = Scenario(name="s1", action_sequence=[Action.BUILD])
        storage_service.ScenarioStore.save(s1)
        result = storage_service.ScenarioStore.get("s1")
        assert result is not None
        assert result.name == "s1"
        assert storage_service.ScenarioStore.get("nonexistent") is None

    def test_load_missing_file(self, temp_data_dir):
        loaded = storage_service.ScenarioStore.load_all()
        assert loaded == []

    def test_description_defaults_to_empty(self, temp_data_dir):
        scenario = Scenario(name="s1", action_sequence=[Action.RUN])
        assert scenario.description == ""
        storage_service.ScenarioStore.save(scenario)
        loaded = storage_service.ScenarioStore.get("s1")
        assert loaded is not None
        assert loaded.description == ""
