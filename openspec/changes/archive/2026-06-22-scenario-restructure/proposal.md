## Why

Currently, Actions and Scenarios are presented as two parallel concepts — Actions can be run independently from the main UI, and Scenarios are just an alternative grouping mechanism. This dual-mode creates confusion: users can bypass scenario-level logic (stop-on-failure, skip, sequencing) by running actions individually, undermining the value of scenarios. We need scenarios to be the primary unit of execution, with individual action execution available only within the context of a selected scenario.

## What Changes

- **BREAKING**: Remove standalone action buttons from the main UI. Actions can no longer be triggered independently outside a scenario context.
- Reduce predefined scenarios to two: **Full Clean build** and **Rebuild**.
  - Full Clean build: `CLEAN → SYNC_SRC → BUILD → PATCH → BUILD → PULL_APK → RUN`
  - Rebuild: `SYNC_SRC → BUILD → PULL_APK → RUN`
- Add a scenario selection dropdown that drives the action chain display.
- Add a "Allow running actions separately" checkbox to let users decide if individual action cards should be clickable.
- Introduce a visual action chain: `[Action 1] → [Action 2] → [Action 3]` with skip checkboxes per card.
- Each action card shows: action name button, short description, and a "Skip action" checkbox.
- "Run Scenario" button executes the scenario; "Cancel" button cancels any running operation.
- Action ordering is fixed from the scenario definition. Small arrows rendered between cards indicate flow direction.
- Clicking an individual action card's button runs only that single action (if allowed by the checkbox).
- Add short descriptions for all actions in the codebase (Action enum or service layer). Descriptions:
  - `SYNC_SRC`: "Sync source files to WSL"
  - `CLEAN`: "Clean WSL working directory"
  - `BUILD`: "Build APK with Buildozer"
  - `PATCH`: "Apply patches to .buildozer"
  - `PULL_APK`: "Download APK from WSL"
  - `RUN`: "Install and run APK on device"

## Capabilities

### New Capabilities
- `scenario-ui`: Visual action chain rendering with cards, arrows, skip toggles, and scenario-driven execution. Replaces the current dual-column action/scenario layout.

### Modified Capabilities
- `action-execution`: Requirements change — action execution is no longer accessible as standalone top-level UI controls. Execution is always scoped to a selected scenario. Individual action execution is only possible via clicking an action card within the chain, and only when the "Allow running actions separately" option is enabled.
- `scenario-orchestration`: Requirements change — per-action skip support during scenario execution. The scenario runner must accept a skip mask that tells it which actions to skip. Scenario execution becomes the primary (and only) execution flow exposed by the UI.

## Impact

- **UI**: `actions_screen.kv` / `ActionsScreen.py` — complete rewrite of the main layout. Remove individual action buttons, replace with scenario dropdown, action chain cards, and new controls.
- **Service**: `scenario_service.py` — add optional skip mask support to `run_scenario()`.
- **Service**: `action_runner.py` — no functional change, but its invocation moves from direct UI buttons to scenario-driven calls.
- **Data**: No new persistence required; scenarios and profiles remain as-is.
- **Removals**: Standalone action buttons (Sync SRC, Clean, Build, Patch, Pull APK, Run) from the main actions screen.
