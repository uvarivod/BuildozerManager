## ADDED Requirements

### Requirement: Scenario switch resets displayed results
The system SHALL reset all displayed scenario run results when the user switches to a different scenario via the scenario selector dropdown. Displayed results include per-action visual state and the aggregate scenario status label.

#### Scenario: Switch scenario after successful run
- **WHEN** the user has run scenario "Full Clean build" and at least one action shows Success
- **WHEN** the user selects a different scenario (e.g., "Rebuild") from the scenario dropdown
- **THEN** every action card in the newly built chain SHALL show initial state (PENDING, not completed, not skipped)
- **THEN** patch action states SHALL be reset to PENDING
- **THEN** the aggregate status label SHALL reset to "Ready" (not "Scenario: Success/Failed")

#### Scenario: Switch scenario after failed run
- **WHEN** the user has run a scenario that failed and cards show Failed
- **WHEN** the user switches to another scenario via the dropdown
- **THEN** the new scenario's cards SHALL NOT inherit Failed/Success from the previous scenario by index
- **THEN** the status label SHALL NOT show the previous run's "Scenario: Failed"

#### Scenario: Switch scenario clears stale skip states
- **WHEN** the previous scenario had skipped cards (via skip mask or failure cascade)
- **WHEN** the user switches scenarios
- **THEN** skipped visual state SHALL NOT carry over to the new scenario's cards

#### Scenario: Selecting placeholder clears results
- **WHEN** the user selects the placeholder "Select scenario" or an empty value
- **THEN** the action chain SHALL be cleared
- **THEN** the status label SHALL reset to "Ready" (if not running)

#### Scenario: Resize still preserves current scenario results
- **WHEN** a scenario is running or has completed and shows per-action status
- **WHEN** the user resizes the window (triggering UI rebuild for the same current scenario)
- **THEN** each action's displayed status SHALL remain unchanged (existing Requirement: Scenario run per-action status survives UI rebuilds SHALL still hold)
