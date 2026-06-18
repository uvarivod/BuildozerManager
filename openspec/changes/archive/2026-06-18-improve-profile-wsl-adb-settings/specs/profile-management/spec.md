## ADDED Requirements

### Requirement: WSL fields are visually grouped under a WSL Configuration section
The profile editor SHALL display all WSL-related fields (WSL Build Directory, WSL Distribution, Retain During Sync) as a visually distinct group labeled "WSL Configuration" with a colored section header spanning the full editor width.

#### Scenario: WSL Configuration section rendered
- **WHEN** the user opens the profile editor
- **THEN** a "WSL Configuration" section header is displayed with a colored background separating WSL fields from general fields
- **THEN** the WSL Build Directory, WSL Distribution, and Retain During Sync fields appear directly below the header

### Requirement: User can browse for WSL Build Directory
The system SHALL provide a Browse button next to the WSL Build Directory field that opens a directory chooser dialog.

#### Scenario: Browse for WSL Build Directory
- **WHEN** the user clicks "Browse" next to the WSL Build Directory field
- **THEN** a directory chooser dialog opens pre-populated with the current path (if any)
- **THEN** if the field is empty, the initial path defaults to `\\wsl.localhost\<WSL Distribution>` using the current WSL Distribution value
- **THEN** selecting a directory fills the text input with the chosen path

## MODIFIED Requirements

### Requirement: Profile stores all build settings
Each profile SHALL store: name, sourcedir, buildozer spec path, adb path, excluded files/folders, WSL Build Directory, WSL Distribution name, patch list, and Retain During Sync list.

#### Scenario: Edit profile settings
- **WHEN** the user selects a profile and modifies any setting field, or clicks Browse to select a source directory, buildozer.spec, ADB path, or WSL Build Directory via the file chooser
- **THEN** the change is reflected in the UI immediately and persisted on save

### Requirement: Retain During Sync list can be configured per profile
The system SHALL maintain a list of files/folders in the WSL Build Directory that are NOT deleted when syncing updated source before copying new source.

FROM: Deletion exclusion list can be configured per profile
TO: Retain During Sync list can be configured per profile

#### Scenario: Add Retain During Sync entry
- **WHEN** the user adds ".buildozer" to the Retain During Sync list
- **THEN** the pattern is saved and applied during source sync operations
