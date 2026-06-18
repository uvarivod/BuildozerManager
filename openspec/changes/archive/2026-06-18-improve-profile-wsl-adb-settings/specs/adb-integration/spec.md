## ADDED Requirements

### Requirement: User can browse for ADB executable path
The system SHALL provide a Browse button next to the ADB path field that opens a file chooser dialog filtered to `adb.exe`.

#### Scenario: Browse for adb.exe
- **WHEN** the user clicks "Browse" next to the ADB path field
- **THEN** a file chooser dialog opens filtered to `adb.exe`, pre-populated with the current path (if any) or the parent directory of the current path
- **THEN** selecting `adb.exe` fills the text input with its full path

## MODIFIED Requirements

### Requirement: ADB path is configurable
The system SHALL allow the user to specify a custom path to `adb.exe` in the profile settings. The field SHALL have a Browse button to select `adb.exe` via file chooser and a Check button to verify ADB connectivity.

#### Scenario: Use custom ADB path
- **WHEN** the profile has a custom adb_path set
- **THEN** all ADB commands use that path instead of `adb` from PATH

#### Scenario: Browse for adb.exe
- **WHEN** the user clicks "Browse" next to the ADB path field
- **THEN** a file chooser opens filtered to `adb.exe` and the selected path populates the field
