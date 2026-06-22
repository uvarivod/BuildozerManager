# Scenario Orchestration

## Purpose

Execute sequences of actions (scenarios) with predefined and user-customizable combinations, showing aggregate results, per-action skip support, and stopping on failure by default.

## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Scenario runner accepts a skip mask
The system SHALL accept an optional `skip_actions` parameter (a set of Action enums) in the `run_scenario` method. Actions in this set SHALL be skipped during execution — their state SHALL be recorded as "Skipped" and the runner SHALL proceed to the next action.

#### Scenario: Skip actions during scenario run
- **WHEN** the user selects "Full Clean build"
- **WHEN** the skip mask contains `{Action.PATCH}`
- **WHEN** the user clicks "Run Scenario"
- **THEN** the runner skips PATCH but executes all other actions (CLEAN, SYNC_SRC, BUILD, BUILD, PULL_APK, RUN) in order
- **THEN** PATCH is recorded with status "Skipped"
- **THEN** the scenario result shows overall duration excluding skipped actions
