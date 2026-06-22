# Scenario UI

## Purpose

Replace the current dual-panel action/scenario layout with a scenario-centric interface featuring a visual action chain, per-action skip toggles, and configurable individual action execution.

## ADDED Requirements

### Requirement: Scenario selection drives the action chain
The system SHALL display a scenario selection dropdown (Spinner) at the top of the main screen. When the user selects a scenario, the system SHALL render its action sequence as a visual chain of action cards.

#### Scenario: Select scenario populates chain (Full Clean build)
- **WHEN** the user selects "Full Clean build" from the scenario dropdown
- **THEN** the action chain displays: `[CLEAN] → [SYNC_SRC] → [BUILD] → [PATCH] → [BUILD] → [PULL_APK] → [RUN]` with arrow separators
- **THEN** each card shows the action name, a short description, and an unchecked Skip checkbox

#### Scenario: Select scenario populates chain (Rebuild)
- **WHEN** the user selects "Rebuild" from the scenario dropdown
- **THEN** the action chain displays: `[SYNC_SRC] → [BUILD] → [PULL_APK] → [RUN]` with arrow separators

#### Scenario: Custom scenario populates chain
- **WHEN** the user selects a custom scenario with actions [Sync SRC, Patch, Build]
- **THEN** the chain displays three cards: `[Sync SRC] → [Patch] → [Build]`

### Requirement: Action chain shows cards with skip toggles
The system SHALL render action cards inside a horizontal layout. Each card SHALL contain:
- A Button displaying the action name
- A short description label (below or beside the name)
- A "Skip action" Checkbox

Cards SHALL be separated by arrow indicators (`→`) showing flow direction.

#### Scenario: Card layout
- **WHEN** a scenario with 3 actions is selected
- **THEN** the user sees: `[Action 1 | desc | ☐ Skip] → [Action 2 | desc | ☐ Skip] → [Action 3 | desc | ☐ Skip]`

#### Scenario: Horizontal scroll for long chains
- **WHEN** a scenario contains more actions than fit the screen width
- **THEN** the action chain area is horizontally scrollable

### Requirement: User can toggle which actions to skip
The system SHALL allow the user to check or uncheck "Skip action" per card. Checked actions SHALL be skipped when "Run Scenario" is clicked.

#### Scenario: Skip checked action
- **WHEN** the user checks "Skip action" on the "Clean" card
- **WHEN** the user clicks "Run Scenario"
- **THEN** the scenario runs but skips the Clean action
- **THEN** the skipped action's status is shown as "Skipped" in results

### Requirement: User can allow or disallow running individual actions
The system SHALL provide a Checkbox labeled "Allow running actions separately" (or equivalent). When unchecked, clicking an action card's button SHALL do nothing. When checked, clicking an action card button SHALL run only that single action (not the full scenario).

#### Scenario: Run single action from card
- **WHEN** "Allow running actions separately" is checked
- **WHEN** the user clicks "Build" on the Build action card
- **THEN** only the Build action executes (same as current individual action execution)
- **THEN** the status label shows "Running: BUILD"

#### Scenario: Single action blocked
- **WHEN** "Allow running actions separately" is unchecked
- **WHEN** the user clicks an action card button
- **THEN** no action is triggered
- **THEN** optionally a popup or visual hint explains that individual execution is disabled

### Requirement: Run Scenario button executes the full chain
The system SHALL provide a "Run Scenario" button. When clicked, the system SHALL iterate through the scenario's action sequence, skipping any actions whose card checkbox is checked, and execute the remaining actions in order. The existing stop-on-failure behavior SHALL still apply.

#### Scenario: Run scenario with skips
- **WHEN** the user selects "Full Clean build"
- **WHEN** the "PATCH" card has Skip checked
- **WHEN** the user clicks "Run Scenario"
- **THEN** the system runs CLEAN, SYNC_SRC, BUILD, BUILD, PULL_APK, RUN
- **THEN** PATCH is recorded as "Skipped"

### Requirement: Cancel button stops any running operation
The system SHALL provide a single "Cancel" button that cancels any running action or scenario. The existing cancellation mechanism (threading.Event in ActionRunner) SHALL be reused.

#### Scenario: Cancel scenario (Rebuild)
- **WHEN** BUILD is running as part of a "Rebuild" scenario
- **WHEN** the user clicks "Cancel"
- **THEN** BUILD is cancelled
- **THEN** remaining actions (PULL_APK, RUN) do not execute
- **THEN** the scenario status is "Cancelled"

### Requirement: Arrow indicators show flow direction between cards
The system SHALL render small arrow indicators between consecutive action cards to visually communicate the execution order.

#### Scenario: Arrows between actions
- **WHEN** a scenario has actions [A, B, C]
- **THEN** the UI displays: `[A] → [B] → [C]`

### Requirement: No standalone action buttons on main screen
The system SHALL NOT render standalone action buttons (Sync SRC, Clean, Build, Patch, Pull APK, Run) outside the context of the action chain.

#### Scenario: Only action chain shown
- **WHEN** the user opens the main screen
- **THEN** there are no individual action buttons in the toolbar or sidebar
- **THEN** the only way to execute actions is through the scenario chain or Run Scenario button
