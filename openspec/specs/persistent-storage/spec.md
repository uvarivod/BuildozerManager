# Persistent Storage

## Purpose

Persist profiles, settings, and scenarios to human-readable JSON files in the application data directory.

## Requirements

### Requirement: Profiles are persisted to JSON
The system SHALL save all profiles to `<app_root>/data/profiles.json` on every save operation.

#### Scenario: Save profiles
- **WHEN** the user creates, modifies, or deletes a profile
- **THEN** the system writes the complete profiles list to the JSON file

#### Scenario: Load profiles on startup
- **WHEN** the application starts
- **THEN** the system reads `profiles.json` and loads all profiles into memory
- **THEN** the profiles list in the UI is populated

#### Scenario: Missing profiles file
- **WHEN** `profiles.json` does not exist at startup
- **THEN** the system creates the directory and file with an empty profiles array

### Requirement: Global settings are persisted to JSON
The system SHALL save application-wide settings to `<app_root>/data/settings.json`.

#### Scenario: Save settings
- **WHEN** the user changes a global setting
- **THEN** the system writes the settings to the JSON file

#### Scenario: Load settings on startup
- **WHEN** the application starts
- **THEN** the system reads `settings.json` and applies saved settings

### Requirement: Scenarios are persisted to JSON
The system SHALL save user-defined custom scenarios to `<app_root>/data/scenarios.json`.

#### Scenario: Save custom scenario
- **WHEN** the user creates or modifies a custom scenario
- **THEN** the system writes the scenarios list to the JSON file

#### Scenario: Load scenarios on startup
- **WHEN** the application starts
- **THEN** the system reads `scenarios.json` and loads all custom scenarios

### Requirement: JSON files use human-readable formatting
The system SHALL write JSON with indentation for readability.

#### Scenario: Formatted JSON
- **WHEN** any JSON file is written
- **THEN** it uses 2-space indentation and sorted keys
