## Why

The current "Clean" action conflates two distinct operations — refreshing source files while preserving build cache (`.buildozer`) vs. nuking everything for a full rebuild — under a single name that also collides with `buildozer clean`. The internal soft-clean step within "Build" also needed to be exposed as a standalone primitive for users who want finer control.

## What Changes

- Split the old ambiguous "Clean" into two well-named operations:
  - **SyncSRC** (`Action.SYNC_SRC`): Delete WSL project files except `.buildozer` (hardcoded) and user's `delete_exclusions` list, then copy fresh source. Exposed as both a standalone action button and used internally by Build.
  - **CleanWSLProject** (`Action.CLEAN`): Delete everything in WSL project dir including `.buildozer` (ignores all exclusions). Exposed as a standalone button and used internally by Clean Build scenarios.
- Keep `delete_exclusions` field on Profile (default `[]`) for user's custom retain items. `sync_src` merges hardcoded `.buildozer` with the user's list.
- Remove the `.buildozer` protection popup (no longer needed since SyncSRC always preserves `.buildozer`).
- Add `buildozer clean` step to the "Clean Build" scenario.
- Add a standalone "Build" predefined scenario.
- Remove "Build and Patch" predefined scenario (covered by "Build" + "Patch" individually).

## Capabilities

### New Capabilities

- `src-sync`: Operation that replaces source files in the WSL project directory while preserving `.buildozer` (hardcoded) and user's custom retain items.

### Modified Capabilities

- `action-execution`: Clean action now maps to CleanWSLProject (always nukes `.buildozer`). Build action no longer warns about `.buildozer` protection. NEW: SYNC_SRC action added.
- `wsl-integration`: WSLService gets `sync_src()` (preserves .buildozer + user exclusions) and `clean_wsl_project()` (nukes everything). `clean_wsl_dir()` removed.
- `scenario-orchestration`: "Clean Build" gains `buildozer clean` step. "Build" scenario added. "Build and Patch" removed.
- `profile-management`: `delete_exclusions` field kept with default changed from `[".buildozer"]` to `[]`.

## Impact

- `src/models/action.py` — add `SYNC_SRC` enum value
- `src/models/profile.py` — keep `delete_exclusions` with default `[]`
- `src/services/wsl_service.py` — add `sync_src()` and `clean_wsl_project()`, remove `clean_wsl_dir()`
- `src/services/action_runner.py` — add `_run_sync_src`, rewrite `_run_clean` and `_run_build`, add `SYNC_SRC` validation
- `src/services/storage_service.py` — keep `delete_exclusions` in save/load
- `src/services/scenario_service.py` — add "Build", remove "Build and Patch"
- `src/screens/actions_screen.py` — restore Clean button, add Sync SRC button, remove popup logic
- `src/kv/actions_screen.kv` — add Sync SRC and Clean buttons
- `src/screens/profile_editor_screen.py` — keep `delete_exclusions_input`
- `src/kv/profile_editor_screen.kv` — keep "Retain During Sync" row
- Specs referencing `clean_wsl_dir` or old Clean semantics need delta updates
