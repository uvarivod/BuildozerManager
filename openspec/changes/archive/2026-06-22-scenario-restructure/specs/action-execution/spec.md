# Action Execution

## Purpose

Execute build pipeline actions (Clean, Build, Pull APK, Run) with real-time status, cancellation support, and validation of required profile fields before execution.

## MODIFIED Requirements

### Requirement: Action execution emits RUNNING state
The system SHALL emit ActionState.RUNNING when an action begins execution. The UI SHALL update the status label to reflect the current running state in real time.

#### Scenario: Build shows running status
- **WHEN** the user triggers an action (via card click or scenario run)
- **THEN** the status label immediately changes to "Running: BUILD"
- **THEN** the UI remains responsive during the build

### Requirement: User can cancel a running action
The system SHALL allow cancellation of any running action via a Cancel button and log the cancellation with duration.

#### Scenario: Cancel during build
- **WHEN** the user clicks Cancel during a Build action (triggered from card or scenario)
- **THEN** the running subprocess is terminated
- **THEN** the action status is set to "Cancelled"
- **THEN** the timer stops and duration is logged with the cancellation

## ADDED Requirements

### Requirement: Action execution is always scenario-scoped
The system SHALL NOT expose standalone action execution buttons outside the scenario action chain. All action execution SHALL be initiated either by clicking an action card within the chain or by clicking "Run Scenario".

#### Scenario: No standalone action UI
- **WHEN** the main screen is rendered
- **THEN** there are no buttons labeled "Sync SRC", "Clean", "Build", "Patch", "Pull APK", or "Run" outside the action chain cards

### Requirement: Individual action execution honors the "allow separately" flag
When a single action is triggered from an action card, the system SHALL check the "Allow running actions separately" flag. If disabled, the action SHALL NOT execute.

#### Scenario: Action blocked when separate execution disabled
- **WHEN** "Allow running actions separately" is unchecked
- **WHEN** the user clicks an action card's button
- **THEN** the action is not executed
