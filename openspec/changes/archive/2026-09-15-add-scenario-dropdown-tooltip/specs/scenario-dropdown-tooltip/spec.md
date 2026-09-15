## ADDED Requirements

### Requirement: Scenario dropdown shows description on hover
The system SHALL show a tooltip containing the scenario's description when the user hovers over an item in the Scenarios dropdown on the main ActionsScreen. The tooltip SHALL be derived from `Scenario.description` for the hovered scenario name, with empty descriptions resulting in no tooltip.

#### Scenario: Hover shows description
- **WHEN** the Scenarios dropdown is open on the main page and the user hovers over a scenario name
- **THEN** a tooltip appears near the hovered item displaying that scenario's `description`

#### Scenario: No description hides tooltip
- **WHEN** the hovered scenario has an empty or whitespace-only `description`
- **THEN** no tooltip is shown

#### Scenario: Tooltip hides on leave or selection
- **WHEN** the user moves the cursor away from the hovered item or selects a scenario
- **THEN** the tooltip is dismissed and no longer visible

#### Scenario: Predefined scenarios show their built-in descriptions
- **WHEN** the user hovers over "Full Clean build", "Rebuild", or "Build and Sign AAB" in the dropdown
- **THEN** the tooltip shows the predefined description for that scenario
