# Scenario Editor Storage

## Purpose

TBD

## Requirements

### Requirement: ScenarioStore provides typed CRUD methods
The system SHALL extend `ScenarioStore` with typed CRUD methods that work with `Scenario` model objects rather than raw dicts.

#### Scenario: load_all returns Scenario list
- **WHEN** `ScenarioStore.load_all()` is called
- **THEN** it returns a `list[Scenario]` deserialized from `data/scenarios.json`
- **THEN** it correctly parses `action_sequence` back to `Action` enum values
- **THEN** it correctly reads the `description` field if present

#### Scenario: save persists scenario list
- **WHEN** `ScenarioStore.save_all(scenarios)` is called with a `list[Scenario]`
- **THEN** `data/scenarios.json` is written with name, description, action_sequence as strings, and stop_on_failure for each scenario

### Requirement: ScenarioStore supports individual CRUD operations
The system SHALL provide `save(scenario)`, `delete(name)`, and `get(name)` methods on `ScenarioStore`.

#### Scenario: Save individual scenario
- **WHEN** `ScenarioStore.save(scenario)` is called with a new scenario
- **THEN** the scenario is appended to the list and persisted

#### Scenario: Update individual scenario
- **WHEN** `ScenarioStore.save(scenario)` is called with an existing scenario name
- **THEN** the existing entry is replaced

#### Scenario: Delete scenario
- **WHEN** `ScenarioStore.delete(name)` is called
- **THEN** the scenario with that name is removed from storage

#### Scenario: Get scenario by name
- **WHEN** `ScenarioStore.get(name)` is called
- **THEN** it returns the matching `Scenario` or `None` if not found

### Requirement: Predefined scenarios are stored separately
The system SHALL maintain predefined scenarios in `ScenarioService` code, not in `data/scenarios.json`. `ScenarioStore` SHALL only handle user-defined scenarios.

#### Scenario: Predefined scenarios not in storage
- **WHEN** `ScenarioStore.load_all()` is called
- **THEN** predefined scenarios ("Full Clean build", "Rebuild") are NOT returned
- **WHEN** a user creates a scenario named "Full Clean build"
- **THEN** it is stored as a user scenario (the predefined version remains separate)

### Requirement: ScenarioStore returns empty list if file missing or corrupt
If `data/scenarios.json` does not exist or contains invalid JSON, `ScenarioStore.load_all()` SHALL return an empty list without raising an exception.

#### Scenario: Missing file returns empty list
- **WHEN** `data/scenarios.json` does not exist
- **THEN** `ScenarioStore.load_all()` returns `[]`

#### Scenario: Corrupt file returns empty list
- **WHEN** `data/scenarios.json` contains invalid JSON
- **THEN** `ScenarioStore.load_all()` returns `[]`
