## 1. Add the new action to the enum

- [x] 1.1 Add `PULL_AAB = auto()` to `Action` enum in `src/models/action.py`, next to `PULL_APK`
- [x] 1.2 Add description entry `Action.PULL_AAB: "Download AAB from WSL"` to `_ACTION_DESCRIPTIONS` in `src/models/action.py`
- [x] 1.3 Extend `src/screens/scenario_editor_screen.py:_action_label` acronym set to include the new action (already handles `AAB` — verify "Pull_AAB" renders correctly)

## 2. Extend artifact discovery for AAB

- [x] 2.1 Refactor `src/services/apk_service.py` to extract helper `_find_latest_by_ext(profile, ext)` shared by APK and AAB; keep existing `find_latest_apk` delegating with `ext="apk"`
- [x] 2.2 Add `find_latest_aab(profile) -> Path | None` in `src/services/apk_service.py` delegating to `_find_latest_by_ext(profile, "aab")`

## 3. Wire up execution in the action runner

- [x] 3.1 Add `Action.PULL_AAB: ["sourcedir", "wsl_dir", "wsl_distro"]` to the `required` mapping in `ActionRunner.validate_action` (`src/services/action_runner.py`)
- [x] 3.2 Add dispatch branch `elif action == Action.PULL_AAB: return self._run_pull_aab(profile, log_cb)` in `run_action`
- [x] 3.3 Implement `_run_pull_aab` in `src/services/action_runner.py` mirroring `_run_pull_apk`: verify `buildozer.spec` exists, log WSL `bin` path, call `self._apk.find_latest_aab(profile)`, handle not-found (log "Missed" + folder contents), copy newest AAB to `sourcedir/bin/` with replace/success message, return `SUCCESS`/`FAILED`

## 4. Verify UI integration

- [x] 4.1 Confirm the scenario editor action palette shows the new "Pull_AAB" chip automatically (via `for action in Action:` in `src/screens/scenario_editor_screen.py`)
- [x] 4.2 Confirm the actions screen renders the Pull AAB card and can run it separately (`src/screens/actions_screen.py` / `src/screens/action_card.py`)

## 5. Tests

- [x] 5.1 Add tests in `tests/test_apk_service.py` for `find_latest_aab`: matching with version, fallback to prefix, no match, case-insensitive prefix
- [x] 5.2 Add tests in `tests/test_action_runner.py` for `PULL_AAB`: `validate_action` lists missing fields, `run_action` returns `FAILED` when spec missing, returns `FAILED` when no AAB found, returns `SUCCESS` on copy, and handles copy exception
- [x] 5.3 Extend `tests/test_actions_screen.py` to assert the Pull AAB card renders in a chain containing `Action.PULL_AAB`
- [x] 5.4 Run the full test suite and verify no regressions (390+ tests)

## 6. Docs & verification

- [x] 6.1 Manually verify a scenario containing `BUILD_AAB` → `PULL_AAB` builds the AAB and copies it to `sourcedir/bin/` on Windows
