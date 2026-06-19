## Context

The Build pipeline (clean → copy → buildozer) works but has several gaps: no RUNNING state feedback, duration timer measures from app start instead of action lifecycle, buildozer output is raw/unparsed, WSL PATH is not exported (buildozer may not be found), `.buildozer` is silently deleted if missing from exclusions, and the exclusion list mutation is thread-unsafe.

## Goals / Non-Goals

**Goals:**
- Emit `ActionState.RUNNING` so the UI shows real-time action status
- Reset duration timer on action start, stop on action completion
- Parse buildozer output for meaningful progress (step names, %, errors)
- Add `export PATH=$PATH:~/.local/bin/` before buildozer in WSL
- Check `buildozer.spec` exists in WSL build dir before running buildozer
- Prompt user if `.buildozer` is not in Retain During Sync before cleaning
- Fix thread-unsafe mutation of `profile.delete_exclusions`

**Non-Goals:**
- No changes to the `Profile` dataclass or persistence schema
- No changes to ADB/Run/Download actions
- No changes to the scenario system

## Decisions

### 1. RUNNING State — Callback from ActionRunner to UI
- **Decision**: Add an `on_state_change` callback parameter to `run_action()`. `ActionRunner` calls it with `ActionState.RUNNING` at the start of each action phase (clean → copy → buildozer). The UI (`ActionsScreen`) binds to this to update `status_label` in real time.
- **Rationale**: Clean separation — `ActionRunner` doesn't know about Kivy, the UI just reacts to state changes.
- **Alternative considered**: Polling `ActionRunner` state from UI thread — adds latency and complexity.

### 2. Duration Timer — Reset on Action Start, Stop on Completion
- **Decision**: Expose `reset_timer()` and `stop_timer()` methods on `LogPanel`. `ActionsScreen` calls `reset_timer()` before spawning the action thread and `stop_timer()` in `_on_action_done`.
- **Rationale**: Keeps timer logic self-contained in `LogPanel`.

### 3. Buildozer Output Parsing — Regex on Each Line
- **Decision**: In `exec_buildozer`, match each output line against known patterns:
  - `#.*` — step headers → log as `info` with source "buildozer"
  - `[INFO]:.*` — buildozer info → log as `info`
  - `[WARN]:.*` — warnings → log as `warn`
  - `%` progress lines → log with percentage visible
  - Everything else → log as `debug`
- **Rationale**: Simple, no dependencies. Buildozer output is relatively structured.
- **Alternative considered**: Parsing the full output buffer with state machine — overkill for current needs.

### 4. WSL PATH Export — Prepend to Buildozer Command
- **Decision**: Change the executed command from `cd <dir> && buildozer android debug` to `export PATH=$PATH:~/.local.bin/; cd <dir> && buildozer android debug`. The `--exec` flag on `wsl.exe` runs via shell so `export` works natively.
- **Rationale**: Confirmed working in the user's reference script. Buildozer is typically installed via `pip install --user buildozer` which places it in `~/.local/bin`.

### 5. Missing .buildozer Warning — Popup with Options
- **Decision**: Before cleaning, if `.buildozer` is not in `profile.delete_exclusions`, pause the action and show a popup with three choices: "Continue (clean build)", "Add to exclusions and continue", "Stop Action". The popup is shown from `ActionsScreen` before calling `run_action()`.
- **Rationale**: The user explicitly requested this. Prevents accidental full rebuilds.

### 6. Thread Safety — Copy Exclusion List
- **Decision**: Replace `profile.delete_exclusions.append(".buildozer")` with `exclusions = list(profile.delete_exclusions)` and operate on the copy.
- **Rationale**: Eliminates race condition without adding locks.

### 7. buildozer.spec Existence Check
- **Decision**: Add `find_spec_in_wsl(profile) -> bool` method to `WSLService` that checks if `buildozer.spec` exists in the WSL build dir. Call it before `exec_buildozer` and log a clear warning if missing.
- **Rationale**: Buildozer will fail silently or cryptically without a spec file.

## Risks / Trade-offs

- **Buildozer output parsing regex may miss new formats**: Buildozer output format may change between versions. Mitigation: use broad patterns and fall back to raw logging for unparseable lines.
- **PATH export assumes bash shell**: If the default WSL shell is not bash, `export` may fail. Mitigation: use `wsl.exe --exec bash -c "..."` to ensure bash.
- **Popup during build adds UI dependency**: Without user response, build won't start. Mitigation: popup is modal and non-dismissable until a choice is made.
