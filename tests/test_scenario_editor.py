from src.models.action import Action
from src.models.scenario import Scenario
from src.screens.scenario_editor_screen import UndoRedoManager


class TestUndoRedoManager:
    def test_record_and_undo(self):
        mgr = UndoRedoManager()
        mgr.record("add", {"action": Action.BUILD}, {})
        assert mgr.can_undo is True
        assert mgr.can_redo is False
        result = mgr.undo()
        assert result is not None
        assert result[0] == "add"
        assert mgr.can_undo is False
        assert mgr.can_redo is True

    def test_redo_after_undo(self):
        mgr = UndoRedoManager()
        mgr.record("add", {"action": Action.BUILD}, {})
        mgr.undo()
        result = mgr.redo()
        assert result is not None
        assert result[0] == "add"

    def test_clear_resets_stacks(self):
        mgr = UndoRedoManager()
        mgr.record("add", {}, {})
        mgr.record("remove", {}, {})
        assert mgr.can_undo is True
        mgr.clear()
        assert mgr.can_undo is False
        assert mgr.can_redo is False

    def test_max_size(self):
        mgr = UndoRedoManager(max_size=3)
        for i in range(5):
            mgr.record(f"op{i}", {}, {})
        # Only last 3 should be retained
        assert mgr.can_undo is True
        # Undo 3 times should work
        assert mgr.undo() is not None
        assert mgr.undo() is not None
        assert mgr.undo() is not None
        # Fourth undo should fail (oldest 2 were dropped)
        assert mgr.undo() is None

    def test_has_unsaved_after_record(self):
        mgr = UndoRedoManager()
        assert mgr.has_unsaved is False
        mgr.record("add", {}, {})
        assert mgr.has_unsaved is True

    def test_mark_saved(self):
        mgr = UndoRedoManager()
        mgr.record("add", {}, {})
        mgr.mark_saved()
        assert mgr.has_unsaved is False

    def test_redo_cleared_on_new_record(self):
        mgr = UndoRedoManager()
        mgr.record("add", {}, {})
        mgr.undo()
        assert mgr.can_redo is True
        mgr.record("remove", {}, {})
        assert mgr.can_redo is False

    def test_undo_on_empty_stack_returns_none(self):
        mgr = UndoRedoManager()
        assert mgr.undo() is None

    def test_redo_on_empty_stack_returns_none(self):
        mgr = UndoRedoManager()
        assert mgr.redo() is None


class TestScenarioDefaults:
    def test_description_defaults_to_empty(self):
        s = Scenario(name="test")
        assert s.description == ""

    def test_is_predefined_defaults_to_false(self):
        s = Scenario(name="test")
        assert s.is_predefined is False

    def test_predefined_flag_set(self):
        from src.services.scenario_service import ScenarioService
        svc = ScenarioService()
        for sc in svc.get_predefined_scenarios():
            assert sc.is_predefined is True

    def test_action_sequence_serialization(self):
        s = Scenario(
            name="test",
            action_sequence=[Action.BUILD, Action.PULL_APK],
        )
        from src.services.storage_service import ScenarioStore
        import tempfile, os
        from pathlib import Path
        from src.services import storage_service

        old_data_dir = storage_service.DATA_DIR
        try:
            storage_service.DATA_DIR = Path(tempfile.mkdtemp())
            # Re-initialize the scenarios.json
            ScenarioStore.save_all([s])
            loaded = ScenarioStore.load_all()
            assert len(loaded) == 1
            assert loaded[0].name == "test"
            assert loaded[0].action_sequence == [Action.BUILD, Action.PULL_APK]
            assert loaded[0].description == ""
        finally:
            storage_service.DATA_DIR = old_data_dir

    def test_scenario_round_trips_json(self):
        s = Scenario(
            name="test",
            description="desc",
            action_sequence=[Action.BUILD],
            stop_on_failure=True,
        )
        from src.services.storage_service import ScenarioStore
        import tempfile
        from pathlib import Path
        from src.services import storage_service

        old = storage_service.DATA_DIR
        try:
            storage_service.DATA_DIR = Path(tempfile.mkdtemp())
            ScenarioStore.save_all([s])
            loaded = ScenarioStore.load_all()
            assert len(loaded) == 1
            assert loaded[0].name == "test"
            assert loaded[0].description == "desc"
            assert loaded[0].action_sequence == [Action.BUILD]
            assert loaded[0].stop_on_failure is True
        finally:
            storage_service.DATA_DIR = old


class TestMergeBehavior:
    def test_user_scenario_same_name_as_predefined(self):
        from src.services.scenario_service import ScenarioService
        from src.services.storage_service import ScenarioStore
        import tempfile
        from pathlib import Path
        from src.services import storage_service

        old = storage_service.DATA_DIR
        try:
            storage_service.DATA_DIR = Path(tempfile.mkdtemp())
            svc = ScenarioService()
            user_scenario = Scenario(
                name="Full Clean build",
                description="user version",
                action_sequence=[Action.BUILD],
            )
            ScenarioStore.save(user_scenario)

            predefined = svc.get_predefined_scenarios()
            user = ScenarioStore.load_all()

            # Predefined still has the original
            assert any(s.name == "Full Clean build" and s.is_predefined for s in predefined)
            # User has their own version
            assert any(s.name == "Full Clean build" and not s.is_predefined for s in user)
        finally:
            storage_service.DATA_DIR = old
