# Patch Card UI

## Purpose

Provide a specialized PatchCard widget for displaying PATCH actions with per-patch control buttons, execution state tracking, and scrollable patch lists.

## Requirements

### Requirement: PatchCard widget exists
The system SHALL provide a `PatchCard` widget (subclass of `ActionCard` or standalone) that renders differently from regular action cards.
The PatchCard SHALL be wider than standard ActionCards. The left side SHALL mirror the standard ActionCard (name, description, skip checkbox, state colors). The right side SHALL contain a vertical list of buttons, one per available patch for the current profile.
If the number of patch buttons exceeds the card height, the right button panel SHALL scroll vertically.

#### Scenario: PATCH action displayed in Actions screen
- **WHEN** a scenario containing a PATCH action is loaded
- **THEN** the PATCH action card SHALL be rendered as a PatchCard with wider width and patch buttons on the right

#### Scenario: Many patches exceed card height
- **WHEN** profile has 10+ patches selected
- **THEN** the right-side button panel SHALL contain a vertical ScrollView

### Requirement: Patch buttons trigger individual patch execution
Each button in the right panel SHALL display the patch name. Clicking a button SHALL immediately run that single patch against the current profile.
The button SHALL show running/success/failed state while the patch executes.
Patch execution SHALL use the same threaded mechanism as other actions.

#### Scenario: Clicking a patch button runs one patch
- **WHEN** user clicks a patch button labeled "disable-analytics"
- **THEN** `ActionRunner.run_single_patch("disable-analytics")` SHALL be called with the current profile

#### Scenario: Patch button shows execution state
- **WHEN** a patch is running
- **THEN** its button SHALL show a running indicator (matching ActionCard state colors)
- **WHEN** the patch succeeds
- **THEN** the button SHALL show success state
- **WHEN** the patch fails
- **THEN** the button SHALL show failed state
