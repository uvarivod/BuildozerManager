## 1. WSLService — new methods

- [x] 1.1 Add `sync_src(profile, log_callback, cancel_check)` method: delete WSL project files except `.buildozer` + user's `delete_exclusions`, then copy source
- [x] 1.2 Add `clean_wsl_project(profile, log_callback, cancel_check)` method: delete everything including `.buildozer`
- [x] 1.3 Remove `clean_wsl_dir()` method (no callers after step 2)

## 2. Action model — add SYNC_SRC enum

- [x] 2.1 Add `SYNC_SRC = auto()` to Action enum
- [x] 2.2 Add `validate_action` entry for SYNC_SRC: `["sourcedir", "wsl_dir", "wsl_distro"]`
- [x] 2.3 Add `_run_sync_src` method to ActionRunner that calls `self._wsl.sync_src()`
- [x] 2.4 Add SYNC_SRC branch to `run_action` dispatch

## 3. ActionRunner — rewire existing operations

- [x] 3.1 Rewrite `_run_build(profile, log_cb)`: call `sync_src()` then buildozer build (remove the standalone clean/copy steps)
- [x] 3.2 Rewrite `_run_clean(profile, log_cb)`: call `clean_wsl_project()` (always nukes `.buildozer`)
- [x] 3.3 Remove `spec_path` from BUILD validation (buildozer finds its own spec in WSL)
- [x] 3.4 Remove the `.buildozer` protection check and popup logic from `_run_build`

## 4. Profile model — keep delete_exclusions with updated semantics

- [x] 4.1 Keep `delete_exclusions` field on Profile with default `[]` (user stores custom items to retain)
- [x] 4.2 `sync_src` merges `{".buildozer"}` (hardcoded) with `set(profile.delete_exclusions)`
- [x] 4.3 `clean_wsl_project` ignores all exclusions
- [x] 4.4 `ProfileStore.load_all` filters unknown fields so old profiles with extra keys don't crash
- [x] 4.5 `ProfileStore.save_all` writes `delete_exclusions` to JSON

## 5. Scenario service — update predefined scenarios

- [x] 5.1 Add "Build" scenario: `[BUILD]`
- [x] 5.2 Keep "Clean Build" scenario: `[CLEAN, BUILD]`
- [x] 5.3 Keep "Clean Build + Patch" scenario: `[CLEAN, BUILD, PATCH]`
- [x] 5.4 Keep "Build and Run" scenario: `[BUILD, PULL_APK, RUN]`
- [x] 5.5 Remove "Build and Patch" scenario (covered by standalone Build + Patch)

## 6. UI — add Sync SRC button, keep Clean button

- [x] 6.1 Add Sync SRC button to `actions_screen.kv`
- [x] 6.2 Restore Clean button in `actions_screen.kv`
- [x] 6.3 Add `"sync_src": Action.SYNC_SRC` to action_map in `actions_screen.py`
- [x] 6.4 Restore `"clean": Action.CLEAN` to action_map in `actions_screen.py`
- [x] 6.5 Remove `_check_buildozer_exclusion` method and the buildozer protection popup

## 7. Profile editor — keep delete_exclusions UI

- [x] 7.1 Keep `delete_exclusions_input` property on ProfileEditorScreen
- [x] 7.2 Keep "Retain During Sync" row in `profile_editor_screen.kv`
- [x] 7.3 Keep `delete_exclusions` in `_build_profile()` method

## 8. Tests — update for new semantics

- [x] 8.1 Update `test_action_runner.py` — BUILD no longer requires `spec_path`
- [x] 8.2 Update `test_models.py` — `delete_exclusions` default is `[]`
- [x] 8.3 Update `test_storage_service.py` — `delete_exclusions` is written to JSON
- [x] 8.4 Update `conftest.py` — sample profile has `delete_exclusions=[]`
