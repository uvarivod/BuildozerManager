# Profile Management

## Purpose

Manage build profiles — create, edit, delete, select active profile, and configure per-profile settings including source directory, WSL paths, exclusion lists, and patches.

## Requirements

### Requirement: User can create a new profile
The system SHALL provide a "New Profile" button on the Profiles screen. Clicking it navigates to the editor with empty fields, where the user can configure settings before saving.

#### Scenario: Create new profile
- **WHEN** the user clicks "New Profile"
- **THEN** an empty profile editor is shown where the user can fill in fields and click Save to create the profile

### Requirement: Profile stores all build settings
Each profile SHALL store: name, sourcedir, buildozer spec path, adb path, excluded files/folders, WSL Build Directory, WSL Distribution name, patch list, and delete_exclusions list (items preserved during SyncSRC).

#### Scenario: Edit profile settings
- **WHEN** the user selects a profile and modifies any setting field, or clicks Browse to select a source directory, buildozer.spec, ADB path, or WSL Build Directory via the file chooser
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

### Requirement: WSL fields are visually grouped under a WSL Configuration section
The profile editor SHALL display all WSL-related fields (WSL Build Directory, WSL Distribution) as a visually distinct group labeled "WSL Related Configuration" with a colored section header spanning the full editor width.

#### Scenario: WSL Configuration section rendered
- **WHEN** the user opens the profile editor
- **THEN** a "WSL Related Configuration" section header is displayed with a colored background separating WSL fields from general fields
- **THEN** the WSL Build Directory and WSL Distribution fields appear directly below the header

### Requirement: User can browse for WSL Build Directory
The system SHALL provide a Browse button next to the WSL Build Directory field that opens a directory chooser dialog.

#### Scenario: Browse for WSL Build Directory
- **WHEN** the user clicks "Browse" next to the WSL Build Directory field
- **THEN** a directory chooser dialog opens pre-populated with the current path (if any)
- **THEN** if the field is empty, the initial path defaults to `\\wsl.localhost\<WSL Distribution>` using the current WSL Distribution value
- **THEN** selecting a directory fills the text input with the chosen path

### Requirement: User can delete a profile
The system SHALL allow deletion of the currently selected profile with a confirmation prompt.

#### Scenario: Delete current profile
- **WHEN** the user clicks "Delete" and confirms
- **THEN** the profile is permanently removed

### Requirement: User can select the active profile
The system SHALL maintain a single active profile whose settings are used for all actions. The user SHALL select the active profile from a dropdown (Spinner) at the top of the Actions screen.

#### Scenario: Select profile from dropdown
- **WHEN** the user opens the profile dropdown and clicks a profile name
- **THEN** that profile becomes active and its settings are used for all actions

### Requirement: Excluded files/folders can be configured per profile
The system SHALL maintain a list of file/folder patterns excluded when copying source to WSL.

#### Scenario: Add exclusion pattern
- **WHEN** the user adds a pattern "*.pyc" to the exclusion list
- **THEN** the pattern is saved and applied during WSL copy

#### Scenario: Remove exclusion pattern
- **WHEN** the user removes a pattern from the exclusion list
- **THEN** the pattern is no longer excluded during copy

### Requirement: delete_exclusions list can be configured per profile
The system SHALL maintain a `delete_exclusions` list of files/folders in the WSL Build Directory that are preserved during the SyncSRC operation. The `.buildozer` directory is always preserved regardless of this list.

#### Scenario: Add delete_exclusions entry
- **WHEN** the user adds "custom_cache" to the delete_exclusions list
- **THEN** the pattern is saved and applied during source sync operations — the file is not deleted when SyncSRC runs
