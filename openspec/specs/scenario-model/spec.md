# Scenario Model

## Purpose

TBD

## Requirements

### Requirement: Scenario has a description field
The `Scenario` model SHALL include a `description: str` field in addition to `name` and `action_sequence`. The default value SHALL be an empty string.

#### Scenario: Create scenario with description
- **WHEN** a `Scenario` is created with `name="Test"`, `description="My test scenario"`, and a sequence list
- **THEN** `scenario.description == "My test scenario"`

#### Scenario: Default description is empty
- **WHEN** a `Scenario` is created without a description
- **THEN** `scenario.description == ""`

### Requirement: Scenario has an is_predefined flag
The `Scenario` model SHALL include an `is_predefined: bool` field with a default of `False`. This flag SHALL NOT be persisted in `data/scenarios.json` (it is determined by the runtime, not storage).

#### Scenario: User-created scenario is not predefined
- **WHEN** a user creates a scenario via the editor
- **THEN** `scenario.is_predefined == False`

#### Scenario: Predefined scenario has flag set
- **WHEN** `ScenarioService.get_predefined_scenarios()` creates a scenario
- **THEN** `scenario.is_predefined == True`

### Requirement: Scenario action_sequence serializes to/from strings
The `action_sequence: list[Action]` field SHALL serialize to `list[str]` (action enum names) in JSON and deserialize back to `list[Action]` on load.

#### Scenario: Scenario round-trips through JSON
- **WHEN** a Scenario with `action_sequence=[Action.BUILD, Action.PULL_APK]` is serialized and deserialized
- **THEN** the resulting Scenario has the same `action_sequence`
