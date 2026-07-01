# Scenario Orchestration

## Purpose

Execute sequences of actions (scenarios) with predefined and user-customizable combinations, showing aggregate results and stopping on failure by default.

## Requirements

### Requirement: System provides precisely two predefined scenarios
The system SHALL include exactly two built-in scenarios: "Full Clean build" and "Rebuild". The previous four-scenario set (Build, Clean Build, Clean Build + Patch, Build and Run) SHALL be removed.

#### Scenario: Full Clean build
- **WHEN** the user selects "Full Clean build"
- **THEN** the system runs CLEAN (delete everything in WSL working directory including `.buildozer`)
- **THEN** the system runs SYNC_SRC (copy fresh source preserving exclusions)
- **THEN** the system runs BUILD (buildozer build)
- **THEN** the system runs PATCH (apply all active patches)
- **THEN** the system runs BUILD again (rebuild with patches applied)
- **THEN** the system runs PULL_APK (copy APK from WSL to local sourcedir/bin)
- **THEN** the system runs RUN (install APK via ADB and launch on device)

#### Scenario: Rebuild
- **WHEN** the user selects "Rebuild"
- **THEN** the system runs SYNC_SRC (copy fresh source preserving exclusions)
- **THEN** the system runs BUILD (buildozer build)
- **THEN** the system runs PULL_APK (copy APK from WSL to local sourcedir/bin)
- **THEN** the system runs RUN (install APK via ADB and launch on device)

### Requirement: Scenario runner accepts a skip mask
The system SHALL accept an optional `skip_indices` parameter (a set of integer indices) in the `run_scenario` method. Actions matching these indices SHALL be skipped during execution — their state SHALL be recorded as "Skipped" and the runner SHALL proceed to the next action.

#### Scenario: Skip actions during scenario run
- **WHEN** the user selects "Full Clean build"
- **WHEN** the skip mask contains `{3}` (the PATCH index)
- **WHEN** the user clicks "Run Scenario"
- **THEN** the runner skips PATCH but executes all other actions (CLEAN, SYNC_SRC, BUILD, BUILD, PULL_APK, RUN) in order
- **THEN** PATCH is recorded with status "Skipped"
- **THEN** the scenario result shows overall duration excluding skipped actions

### Requirement: User can create custom scenarios
The system SHALL allow composing any sequence of actions into a named custom scenario via the Scenario Editor. The existing scenario builder SHALL be removed and replaced by the Scenario Editor.

#### Scenario: Create custom scenario in editor
- **WHEN** the user opens the Scenario Editor
- **THEN** they can name the scenario, add a description, and compose actions via drag-and-drop
- **THEN** the scenario is saved via `ScenarioStore` and appears in the scenarios list and selector

### Requirement: Scenario execution shows aggregate results
The system SHALL display start time, duration, per-action status, and overall pass/fail for each scenario run. Per-action status SHALL include "Skipped" as a valid state in addition to Success, Failed, and Cancelled.

#### Scenario: Scenario run results
- **WHEN** a scenario finishes execution
- **THEN** the UI shows start time, total duration, each action's status (Success/Failed/Skipped/Cancelled), and a combined log

### Requirement: Scenario stops on failure by default
The system SHALL stop executing remaining actions if any action in the sequence fails, unless configured otherwise. Actions that are skipped via the skip mask are not executed regardless of stop-on-failure.

#### Scenario: Failure stops scenario
- **WHEN** the BUILD action fails during "Full Clean build" (at the first BUILD step)
- **THEN** the remaining actions (PATCH, second BUILD, PULL_APK, RUN) are skipped (due to stop-on-failure)
- **THEN** the scenario status is "Failed"
- **THEN** the failed action's log is highlighted

#### Scenario: Skipped actions are not affected by failure
- **WHEN** the Build action fails during a scenario
- **WHEN** the Run action was already marked as skipped in the skip mask
- **THEN** the Run action is recorded as "Skipped" (not affected by the failure cascade)

### Requirement: Predefined scenarios are not editable
Predefined scenarios ("Full Clean build", "Rebuild") SHALL NOT be editable or deletable via the Scenario Editor. Their action sequences, names, and descriptions SHALL be fixed.

#### Scenario: Opening predefined scenario shows read-only
- **WHEN** the user selects a predefined scenario in the Scenario Editor
- **THEN** all editing controls are disabled
- **THEN** name and description fields are read-only
- **THEN** the delete button is hidden

### Requirement: User scenarios and predefined scenarios coexist
If a user creates a scenario with the same name as a predefined scenario, the predefined version SHALL continue to exist in `ScenarioService.get_predefined_scenarios()` while the user version is stored separately in `ScenarioStore`. Both appear in the scenario list and selector without source suffixes.
