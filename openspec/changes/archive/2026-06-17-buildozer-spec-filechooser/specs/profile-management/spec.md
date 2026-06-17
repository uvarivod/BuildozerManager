## MODIFIED Requirements

### Requirement: Profile stores all build settings
Each profile SHALL store: name, sourcedir, buildozer spec path, adb path, excluded files/folders, WSL working directory, WSL distribution name, patch list, and deletion exclusion list.

#### Scenario: Edit profile settings
- **WHEN** the user selects a profile and modifies any setting field, or clicks Browse to select a source directory or buildozer.spec via the file chooser
- **THEN** the change is reflected in the UI immediately and persisted on save

#### Scenario: Browse for source directory
- **WHEN** the user clicks "Browse" next to the Source Directory field
- **THEN** a directory chooser dialog opens pre-populated with the current path (if any)
- **THEN** selecting a directory fills the text input with the chosen path
- **THEN** if the chosen directory contains `buildozer.spec`, a confirmation popup asks "We found buildozer.spec in the folder you chose. Do you want to use it?"
- **THEN** if the user clicks "Yes", the buildozer spec path field is populated with the path to that file
- **THEN** if the user clicks "No", the popup closes with no further action

#### Scenario: Browse for buildozer.spec
- **WHEN** the user clicks "Browse" next to the buildozer.spec path field
- **THEN** a file chooser dialog opens filtered to `buildozer.spec` files, pre-populated with the current source directory path (if any)
- **THEN** selecting `buildozer.spec` fills the text input with its full path
