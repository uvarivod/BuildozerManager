## ADDED Requirements

### Requirement: Action execution states persist across UI rebuilds
The system SHALL preserve per-action execution state (PENDING, RUNNING, SUCCESS, FAILED, CANCELLED, SKIPPED) across any UI widget rebuild triggered by window resize, maximize, or other layout events.

#### Scenario: State survives window resize
- **WHEN** an action has state RUNNING, SUCCESS, or FAILED
- **WHEN** the user resizes or maximizes the window
- **THEN** the action state SHALL remain unchanged after the resize
- **AND** the UI SHALL display the same state indicators (colors, text) as before the resize

#### Scenario: Patch states survive window resize
- **WHEN** a PatchCard has individual patch states tracked in `patch_states`
- **WHEN** the user resizes or maximizes the window
- **THEN** each individual patch state SHALL remain unchanged after the resize
