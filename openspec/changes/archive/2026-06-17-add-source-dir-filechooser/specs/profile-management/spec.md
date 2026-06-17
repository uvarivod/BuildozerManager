## MODIFIED Requirements

### Requirement: Profile stores all build settings
Each profile SHALL store: name, sourcedir, buildozer spec path, adb path, excluded files/folders, WSL working directory, WSL distribution name, patch list, and deletion exclusion list.

#### Scenario: Edit profile settings
- **WHEN** the user selects a profile and modifies any setting field, or clicks Browse to select a source directory via the file chooser
- **THEN** the change is reflected in the UI immediately and persisted on save

#### Scenario: Browse for source directory
- **WHEN** the user clicks "Browse" next to the Source Directory field
- **THEN** a directory chooser dialog opens pre-populated with the current path (if any)
- **THEN** selecting a directory fills the text input with the chosen path
- **THEN** auto-detect buildozer.spec fires on the new path

#### Scenario: Auto-detect buildozer.spec
- **WHEN** the user sets sourcedir to a path containing `buildozer.spec`
- **THEN** the buildozer spec path field auto-populates with that file path

#### Scenario: Auto-detect ADB
- **WHEN** the user has Android SDK or platform-tools on PATH
- **THEN** the adb_path field auto-populates with the detected ADB executable location
