## ADDED Requirements

### Requirement: Scenario run per-action status survives UI rebuilds
The system SHALL preserve per-action status displayed during a scenario run across any UI widget rebuild triggered by window resize.

#### Scenario: Scenario states persist on resize
- **WHEN** a scenario is running and at least one action has completed with SUCCESS or FAILED
- **WHEN** the user resizes or maximizes the window
- **THEN** each action's displayed status SHALL remain unchanged
- **THEN** the running action's state SHALL remain RUNNING
