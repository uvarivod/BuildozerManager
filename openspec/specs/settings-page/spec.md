# Settings Page

## Purpose

TBD

## Requirements

### Requirement: Settings screen is accessible from bottom navigation
The system SHALL provide a Settings screen accessible via a "Settings" button in the bottom navigation bar.

#### Scenario: Navigate to settings
- **WHEN** the user clicks the "Settings" button in the bottom nav
- **THEN** the Settings screen is displayed
- **THEN** a "Back" or navigation button returns to the previous screen

### Requirement: User can configure log directory path
The system SHALL allow the user to set the directory path where log files are saved.

#### Scenario: Change log directory
- **WHEN** the user enters a new path in the "Log Directory" field on the Settings screen
- **AND** clicks "Save"
- **THEN** the path is persisted via SettingsStore
- **THEN** subsequent log auto-saves write to the new directory

#### Scenario: Invalid path shows error
- **WHEN** the user enters an invalid or non-writable path
- **AND** clicks "Save"
- **THEN** an error message is shown
- **AND** the previous valid path is retained

### Requirement: User can configure maximum log folder size
The system SHALL allow the user to set the maximum size (in MB) of the log directory before auto-cleanup is triggered.

#### Scenario: Set max log size
- **WHEN** the user enters a numeric value in the "Max Log Size (MB)" field on the Settings screen
- **AND** clicks "Save"
- **THEN** the value is persisted via SettingsStore
- **THEN** subsequent cleanup checks use this threshold

#### Scenario: Default values on first visit
- **WHEN** the user opens the Settings screen for the first time
- **THEN** the Log Directory field defaults to "logs"
- **THEN** the Max Log Size field defaults to "100"

### Requirement: Settings values are persisted across app restarts
The system SHALL persist all settings values using SettingsStore so they survive app restarts.

#### Scenario: Settings persist after restart
- **WHEN** the user saves settings
- **AND** closes and reopens the app
- **THEN** the saved values are displayed on the Settings screen
