from collections.abc import Callable
from datetime import datetime

from src.models.action import Action, ActionState
from src.models.scenario import Scenario, ScenarioRun
from src.services.action_runner import ActionRunner
from src.services.log_service import LogService, LogLevel


class ScenarioService:
    def __init__(self):
        self._runner = ActionRunner()
        self._log = LogService()

    def get_predefined_scenarios(self) -> list[Scenario]:
        return [
            Scenario(
                name="Build and Patch",
                action_sequence=[Action.BUILD, Action.PATCH],
                stop_on_failure=True,
            ),
            Scenario(
                name="Clean Build",
                action_sequence=[Action.CLEAN, Action.BUILD],
                stop_on_failure=True,
            ),
            Scenario(
                name="Clean Build + Patch",
                action_sequence=[Action.CLEAN, Action.BUILD, Action.PATCH],
                stop_on_failure=True,
            ),
            Scenario(
                name="Build and Run",
                action_sequence=[Action.BUILD, Action.PULL_APK, Action.RUN],
                stop_on_failure=True,
            ),
        ]

    def run_scenario(
        self,
        scenario: Scenario,
        profile,
        log_callback: Callable | None = None,
        cancel_check: Callable | None = None,
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

        for action in scenario.action_sequence:
            if cancel_check and cancel_check():
                cb("warn", "Scenario cancelled")
                run.overall_status = ActionState.CANCELLED
                break

            cb("info", f"Running action: {action.name}")
            state = self._runner.run_action(action, profile)
            run.per_action_status[action.name] = state
            cb("info", f"Action {action.name} finished: {state.name}")

            if state in (ActionState.FAILED, ActionState.CANCELLED) and scenario.stop_on_failure:
                cb("warn", f"Scenario stopped due to {state.name} on {action.name}")
                run.overall_status = state
                break
        else:
            all_ok = all(
                s == ActionState.SUCCESS
                for s in run.per_action_status.values()
            )
            run.overall_status = ActionState.SUCCESS if all_ok else ActionState.FAILED

        run.duration = (datetime.now() - run.start_time).total_seconds()
        cb("info" if run.overall_status == ActionState.SUCCESS else "error",
           f"Scenario finished: {run.overall_status.name} ({run.duration:.1f}s)")
        return run
