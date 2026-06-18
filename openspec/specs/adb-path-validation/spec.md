# ADB Path Validation

## Purpose

Allow the user to verify that the configured ADB path points to a valid ADB executable, all from within the profile editor — without needing a connected device.

## Requirements

### Requirement: User can verify ADB connectivity from the profile editor
The system SHALL provide a Check button next to the ADB path field that tests the configured ADB executable and shows the result in a popup.

#### Scenario: ADB check succeeds (valid executable)
- **WHEN** the user clicks "Check" next to the ADB path field
- **THEN** the system runs `<adb_path> version` using the configured ADB path
- **THEN** a popup opens showing "ADB is working" and the ADB version string output

#### Scenario: ADB check fails (invalid path or ADB not found)
- **WHEN** the user clicks "Check" and the ADB path is invalid or ADB is not found
- **THEN** a popup opens showing an error message: "ADB not found at: <path>"
