## 1. Add the new action to the enum

- [x] 1.1 Add `BUILD_AAB = auto()` to `Action` enum in `src/models/action.py`, next to `BUILD`
- [x] 1.2 Add description entry `Action.BUILD_AAB: "Build AAB with Buildozer (release)"` to `_ACTION_DESCRIPTIONS` in `src/models/action.py`

## 2. Wire up execution in the action runner

- [x] 2.1 Add `Action.BUILD_AAB: ["sourcedir", "wsl_dir", "wsl_distro"]` to the `required` mapping in `ActionRunner.validate_action` (`src/services/action_runner.py`)
- [x] 2.2 Add dispatch branch `elif action == Action.BUILD_AAB: return self._run_build_aab(profile, log_cb)` in `run_action`
- [x] 2.3 Implement `_run_build_aab` in `src/services/action_runner.py` mirroring `_run_build`: check WSL running, warn if `buildozer.spec` missing in WSL, call `self._wsl.exec_buildozer(profile, command="buildozer android release", log_callback=log_cb, cancel_check=self._check_cancelled)`, check cancellation, log result, return `SUCCESS`/`FAILED`/`CANCELLED`

## 3. Verify UI integration

- [x] 3.1 Confirm the scenario editor action palette shows the new "BUILD_AAB" chip automatically (via `for action in Action:` in `src/screens/scenario_editor_screen.py`)
- [x] 3.2 Confirm the actions screen renders the Build AAB card and can run it separately (`src/screens/actions_screen.py` / `src/screens/action_card.py`)

## 4. Tests

- [x] 4.1 Add tests in `tests/test_action_runner.py` covering: `_run_build_aab` returns SUCCESS on build success, returns FAILED when WSL is not running, returns FAILED/CANCELLED appropriately, and `validate_action` lists missing fields for `BUILD_AAB`
- [x] 4.2 Extend `tests/test_actions_screen.py` (if applicable) to assert the Build AAB card renders in a chain containing `Action.BUILD_AAB`
- [x] 4.3 Run the full test suite and verify no regressions
