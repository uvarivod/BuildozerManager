## Why

The Build action has accumulated issues: no RUNNING state emitted, no buildozer output parsing, broken duration timer, no buildozer.spec validation, no PATH export for WSL, thread-unsafe exclusion list mutation, and no warning when `.buildozer` is missing from Retain During Sync. These make builds fragile and the user experience unclear.

## What Changes

### Core Build Pipeline (clean → copy → buildozer)
- No structural change: the 3-step pipeline stays, but each phase is hardened

### Bugfix: Emit RUNNING state
- `ActionRunner.run_action()` SHALL emit `ActionState.RUNNING` via a callback so the UI shows real-time status (currently only SUCCESS/FAILED/CANCELLED are returned)

### Enhancement: Duration timer tied to action lifecycle
- The `LogPanel` duration timer currently starts on the first log event (app start). Change to reset/start when any action begins and stop when it completes

### Enhancement: Buildozer output parsing
- Parse `buildozer android debug` output for step names and progress indicators; log them with appropriate context so the user sees meaningful progress

### Enhancement: WSL PATH export
- The `exec_buildozer` method SHALL prepend `export PATH=$PATH:~/.local/bin/` before the buildozer command, matching the working approach from the reference script

### Enhancement: buildozer.spec existence check
- Before running `buildozer android debug`, verify `buildozer.spec` exists in the WSL build directory; log a clear warning if missing

### Enhancement: Missing .buildozer protection warning
- During the clean phase, if `.buildozer` is not in the profile's `delete_exclusions` list, show a confirmation popup: "Continue (clean build)", "Add to exclusions and continue", or "Stop"

### Thread safety: exclusion list mutation
- Currently `_run_build` mutates `profile.delete_exclusions` in-place (appends `.buildozer`). Replace with a copy to avoid race conditions

### Old script review
- The reference script confirms the `export PATH=$PATH:~/.local/bin/` pattern is needed for buildozer in WSL. Other aspects (forward-slash UNC paths, flat copy) are already handled better in the current implementation

## Capabilities

### Modified Capabilities
- `action-execution`: Emit RUNNING state, duration tied to action lifecycle, buildozer output parsing, missing .buildozer warning, PATH export for WSL, spec existence check
- `wsl-integration`: buildozer.spec existence check added

## Impact

- **`src/services/action_runner.py`**: Add RUNNING emission via callback; fix thread-unsafe exclusion mutation; add .buildozer missing warning
- **`src/services/wsl_service.py`**: Add `check_spec_exists()` method; add PATH export to `exec_buildozer`; add buildozer output parsing
- **`src/screens/actions_screen.py`**: Wire RUNNING state to UI status label
- **`src/screens/log_panel.py`**: Reset/start duration timer on action start, stop on action complete
- **`src/services/log_service.py`**: No changes needed
- **`src/models/action.py`**: No changes needed (RUNNING already defined)
