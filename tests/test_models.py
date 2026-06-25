from datetime import datetime

from src.models.action import Action, ActionState
from src.models.patch import Patch, PatchRegistry
from src.models.profile import Profile
from src.models.scenario import Scenario, ScenarioRun
from src.services.log_service import LogEvent, LogLevel


class TestProfile:
    def test_default_values(self):
        p = Profile(name="test")
        assert p.name == "test"
        assert p.sourcedir == ""
        assert p.spec_path == ""
        assert p.adb_path == "adb"
        assert p.excluded_files == []
        assert p.wsl_dir == ""
        assert p.wsl_distro == "Ubuntu-22.04"
        assert p.patches == []
        assert p.delete_exclusions == []

    def test_custom_values(self):
        p = Profile(
            name="custom",
            sourcedir="/src",
            excluded_files=["*.log"],
            wsl_distro="Debian",
            patches=["fix"],
            delete_exclusions=["node_modules"],
        )
        assert p.name == "custom"
        assert p.sourcedir == "/src"
        assert p.excluded_files == ["*.log"]
        assert p.wsl_distro == "Debian"
        assert p.patches == ["fix"]
        assert p.delete_exclusions == ["node_modules"]

    def test_delete_exclusions_mutable_default(self):
        p1 = Profile(name="a")
        p2 = Profile(name="b")
        assert p1.delete_exclusions is not p2.delete_exclusions


class TestAction:
    def test_values(self):
        assert Action.SYNC_SRC.name == "SYNC_SRC"
        assert Action.CLEAN.name == "CLEAN"
        assert Action.BUILD.name == "BUILD"
        assert Action.PATCH.name == "PATCH"
        assert Action.PULL_APK.name == "PULL_APK"
        assert Action.RUN.name == "RUN"

    def test_all_enum_values_unique(self):
        values = [a.value for a in Action]
        assert len(values) == len(set(values))


class TestActionState:
    def test_values(self):
        assert ActionState.IDLE.name == "IDLE"
        assert ActionState.RUNNING.name == "RUNNING"
        assert ActionState.SUCCESS.name == "SUCCESS"
        assert ActionState.FAILED.name == "FAILED"
        assert ActionState.CANCELLED.name == "CANCELLED"


class TestScenario:
    def test_defaults(self):
        s = Scenario(name="test")
        assert s.name == "test"
        assert s.action_sequence == []
        assert s.stop_on_failure is True

    def test_with_actions(self):
        s = Scenario(
            name="build-and-patch",
            action_sequence=[Action.BUILD, Action.PATCH],
            stop_on_failure=False,
        )
        assert s.name == "build-and-patch"
        assert s.action_sequence == [Action.BUILD, Action.PATCH]
        assert s.stop_on_failure is False


class TestScenarioRun:
    def test_defaults(self):
        now = datetime.now()
        r = ScenarioRun(scenario_name="test", start_time=now)
        assert r.scenario_name == "test"
        assert r.start_time == now
        assert r.duration == 0.0
        assert r.per_action_status == {}
        assert r.overall_status == ActionState.IDLE


class TestPatch:
    def test_defaults(self):
        p = Patch(name="fix-sdl")
        assert p.name == "fix-sdl"
        assert p.description == ""
        assert p.enabled is True

    def test_all_fields(self):
        p = Patch(name="fix-sdl", description="Fixes SDL issue", enabled=False)
        assert p.description == "Fixes SDL issue"
        assert p.enabled is False


class TestPatchRegistry:
    def setup_method(self):
        PatchRegistry._patches = {}

    def test_register_and_get(self):
        PatchRegistry._patches = {}

        @PatchRegistry.register("my-patch", "A test patch")
        def my_patch_func(path):
            pass

        func = PatchRegistry.get("my-patch")
        assert func is my_patch_func
        assert func._patch_name == "my-patch"
        assert func._patch_description == "A test patch"

    def test_get_unknown_returns_none(self):
        PatchRegistry._patches = {}
        assert PatchRegistry.get("nonexistent") is None

    def test_list_patches(self):
        PatchRegistry._patches = {}

        @PatchRegistry.register("patch-a", "First patch")
        def patch_a(path):
            pass

        @PatchRegistry.register("patch-b", "Second patch")
        def patch_b(path):
            pass

        patches = PatchRegistry.list_patches()
        names = [p.name for p in patches]
        assert "patch-a" in names
        assert "patch-b" in names
        assert len(patches) == 2


class TestLogEvent:
    def test_formatted(self):
        ts = datetime(2026, 6, 19, 16, 30, 0)
        event = LogEvent(timestamp=ts, level=LogLevel.INFO, message="hello", source="test")
        formatted = event.formatted()
        assert "2026-06-19 16:30:00" in formatted
        assert "INFO" in formatted
        assert "[test]" in formatted
        assert "hello" in formatted

    def test_formatted_no_source(self):
        ts = datetime(2026, 6, 19, 16, 30, 0)
        event = LogEvent(timestamp=ts, level=LogLevel.INFO, message="no source")
        assert "[no source]" not in event.formatted()

    def test_plain_text(self):
        ts = datetime(2026, 6, 19, 16, 30, 0)
        event = LogEvent(timestamp=ts, level=LogLevel.ERROR, message="fail", source="build")
        text = event.plain_text()
        assert "[2026-06-19 16:30:00]" in text
        assert "ERROR" in text
        assert "[build]" in text
        assert "fail" in text
        assert "[b]" not in text  # no markup

    def test_replace_last_default(self):
        event = LogEvent(timestamp=datetime.now(), level=LogLevel.DEBUG, message="progress")
        assert event.replace_last is False

    def test_replace_last_true(self):
        event = LogEvent(
            timestamp=datetime.now(), level=LogLevel.DEBUG, message="progress",
            replace_last=True,
        )
        assert event.replace_last is True
