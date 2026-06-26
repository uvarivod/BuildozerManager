from collections.abc import Callable
from datetime import datetime

from src.models.action import Action, ActionState
from src.models.scenario import Scenario, ScenarioRun
from src.models.custom_action import CustomAction
from src.services.action_runner import ActionRunner
from src.services.storage_service import CustomActionStore
from src.services.log_service import LogService, LogLevel


class ScenarioService:
    def __init__(self, runner: ActionRunner | None = None):
        self._runner = runner or ActionRunner()
        self._log = LogService()

    def get_predefined_scenarios(self) -> list[Scenario]:
        return [
            Scenario(
                name="Full Clean build",
                description="Clean WSL directory, sync source, build, apply patches, rebuild, pull APK, and run on device",
                action_sequence=[
                    Action.CLEAN,
                    Action.SYNC_SRC,
                    Action.BUILD,
                    Action.PATCH,
                    Action.BUILD,
                    Action.PULL_APK,
                    Action.RUN,
                ],
                stop_on_failure=True,
                is_predefined=True,
            ),
            Scenario(
                name="Rebuild",
                description="Sync source, build, pull APK, and run on device",
                action_sequence=[
                    Action.SYNC_SRC,
                    Action.BUILD,
                    Action.PULL_APK,
                    Action.RUN,
                ],
                stop_on_failure=True,
                is_predefined=True,
            ),
        ]

    def run_scenario(
        self,
        scenario: Scenario,
        profile,
        log_callback: Callable | None = None,
        cancel_check: Callable | None = None,
        skip_indices: set[int] | None = None,
        on_action_state_change: Callable[[int, ActionState], None] | None = None,
    ) -> ScenarioRun:
        run = ScenarioRun(
            scenario_name=scenario.name,
            start_time=datetime.now(),
        )

        def default_log(level, msg, source=""):
            level_map = {
                "debug": LogLevel.DEBUG,
                "info": LogLevel.INFO,
                "warn": LogLevel.WARN,
                "error": LogLevel.ERROR,
                "success": LogLevel.SUCCESS,
            }
            self._log.log(level_map.get(level, LogLevel.INFO), msg, source=source)

        cb = log_callback or default_log
        cb("info", f"Starting scenario: {scenario.name}")

        self._runner.reset_cancel()

        skip_set: set[int] = skip_indices or set()
        seq = scenario.action_sequence

        for i, action in enumerate(seq):
            if cancel_check and cancel_check():
                cb("warn", "Scenario cancelled")
                run.overall_status = ActionState.CANCELLED
                if on_action_state_change:
                    on_action_state_change(i, ActionState.CANCELLED)
                break

            if i in skip_set:
                cb("info", f"Skipping action: {action.name}")
                run.per_action_status[action.name] = ActionState.SKIPPED
                if on_action_state_change:
                    on_action_state_change(i, ActionState.SKIPPED)
                continue

            cb("info", f"Running action: {action.name}")
            script_path = None
            if action == Action.CUSTOM_SCRIPT:
                ca_name = scenario.custom_action_names.get(i)
                if ca_name:
                    script_path = next(
                        (ca.logic for ca in CustomActionStore.load_all() if ca.name == ca_name),
                        None,
                    )
            if on_action_state_change:
                on_action_state_change(i, ActionState.RUNNING)
            state = self._runner.run_action(action, profile, script_path=script_path)
            run.per_action_status[action.name] = state
            cb("info", f"Action {action.name} finished: {state.name}")
            if on_action_state_change:
                on_action_state_change(i, state)

            if state in (ActionState.FAILED, ActionState.CANCELLED) and scenario.stop_on_failure:
                cb("warn", f"Scenario stopped due to {state.name} on {action.name}")
                run.overall_status = state
                break
        else:
            all_ok = all(
                s in (ActionState.SUCCESS, ActionState.SKIPPED)
                for s in run.per_action_status.values()
            )
            run.overall_status = ActionState.SUCCESS if all_ok else ActionState.FAILED

        run.duration = (datetime.now() - run.start_time).total_seconds()
        cb("info" if run.overall_status == ActionState.SUCCESS else "error",
           f"Scenario finished: {run.overall_status.name} ({run.duration:.1f}s)")
        return run
