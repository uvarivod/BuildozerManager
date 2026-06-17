# Scenario Orchestration

## Purpose

Execute sequences of actions (scenarios) with predefined and user-customizable combinations, showing aggregate results and stopping on failure by default.

## Requirements

### Requirement: System provides predefined scenarios
The system SHALL include these built-in scenarios: "Build and Patch", "Clean Build", "Clean Build + Patch", "Build and Run".

#### Scenario: Build and Patch
- **WHEN** the user selects "Build and Patch"
- **THEN** the system first executes Build
- **THEN** the system applies all active patches to .buildozer
- **THEN** the system logs each step with timestamps

#### Scenario: Clean Build
- **WHEN** the user selects "Clean Build"
- **THEN** the system cleans the entire WSL working directory (no exclusions)
- **THEN** the system copies source and runs Buildozer

#### Scenario: Build and Run
- **WHEN** the user selects "Build and Run"
- **THEN** the system executes Build
- **THEN** the system downloads the APK
- **THEN** the system installs and launches the app via ADB

### Requirement: User can create custom scenarios
The system SHALL allow composing any sequence of actions into a named custom scenario.

#### Scenario: Create custom scenario
- **WHEN** the user opens the scenario builder
- **THEN** they can name the scenario and select actions (Clean, Build, Patch, Download, Run)
- **THEN** the scenario is saved and appears in the scenarios list

### Requirement: Scenario execution shows aggregate results
The system SHALL display start time, duration, per-action status, and overall pass/fail for each scenario run.

#### Scenario: Scenario run results
- **WHEN** a scenario finishes execution
- **THEN** the UI shows start time, total duration, each action's status (Success/Failed/Skipped/Cancelled), and a combined log

### Requirement: Scenario stops on failure by default
The system SHALL stop executing remaining actions if any action in the sequence fails, unless configured otherwise.

#### Scenario: Failure stops scenario
- **WHEN** the Build action fails during "Build and Run"
- **THEN** the Download and Run actions are skipped
- **THEN** the scenario status is "Failed"
- **THEN** the failed action's log is highlighted
