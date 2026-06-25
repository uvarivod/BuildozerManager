## MODIFIED Requirements

### Requirement: User can create custom scenarios
The system SHALL allow composing any sequence of actions into a named custom scenario via the Scenario Editor. The existing scenario builder SHALL be removed and replaced by the Scenario Editor.

#### Scenario: Create custom scenario in editor
- **WHEN** the user opens the Scenario Editor
- **THEN** they can name the scenario, add a description, and compose actions via drag-and-drop
- **THEN** the scenario is saved via `ScenarioStore` and appears in the scenarios list and selector

## ADDED Requirements

### Requirement: Predefined scenarios are not editable
Predefined scenarios ("Full Clean build", "Rebuild") SHALL NOT be editable or deletable via the Scenario Editor. Their action sequences, names, and descriptions SHALL be fixed.

#### Scenario: Opening predefined scenario shows read-only
- **WHEN** the user selects a predefined scenario in the Scenario Editor
- **THEN** all editing controls are disabled
- **THEN** name and description fields are read-only
- **THEN** the delete button is hidden

### Requirement: User scenarios override predefined names
If a user creates a scenario with the same name as a predefined scenario, the predefined version SHALL continue to exist in `ScenarioService.get_predefined_scenarios()` while the user version is stored separately in `ScenarioStore`. The scenario selector SHALL show both, distinguished by their source.

#### Scenario: Same name in user and predefined
- **WHEN** the user creates a scenario named "Full Clean build"
- **THEN** both the predefined "Full Clean build" and the user "Full Clean build" appear in the scenario list
- **THEN** they are visually distinguished (e.g., "(predefined)" / "(custom)" suffix)
