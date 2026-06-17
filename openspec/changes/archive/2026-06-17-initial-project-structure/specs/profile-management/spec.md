## ADDED Requirements

### Requirement: User can create a new profile
The system SHALL allow the user to create a new build profile with a unique name and default settings.

#### Scenario: Create profile with unique name
- **WHEN** the user clicks "New Profile" and enters name "MyApp"
- **THEN** a new profile named "MyApp" is created with default values

#### Scenario: Create profile with duplicate name
- **WHEN** the user clicks "New Profile" and enters a name that already exists
- **THEN** the system SHALL show an error message and refuse to create

### Requirement: Profile stores all build settings
Each profile SHALL store: name, sourcedir, buildozer spec path, adb path, excluded files/folders, WSL working directory, WSL distribution name, patch list, and deletion exclusion list.

#### Scenario: Edit profile settings
- **WHEN** the user selects a profile and modifies any setting field
- **THEN** the change is reflected in the UI immediately and persisted on save

#### Scenario: Auto-detect buildozer.spec
- **WHEN** the user sets sourcedir to a path containing `buildozer.spec`
- **THEN** the buildozer spec path field auto-populates with that file path

#### Scenario: Auto-detect ADB
- **WHEN** the user has Android SDK or platform-tools on PATH
- **THEN** the adb_path field auto-populates with the detected ADB executable location

### Requirement: User can delete a profile
The system SHALL allow deletion of any profile with a confirmation prompt.

#### Scenario: Delete profile with confirmation
- **WHEN** the user clicks "Delete Profile" and confirms
- **THEN** the profile is permanently removed

#### Scenario: Cancel profile deletion
- **WHEN** the user clicks "Delete Profile" and cancels the confirmation
- **THEN** the profile is not deleted

### Requirement: User can select the active profile
The system SHALL maintain a single active profile whose settings are used for all actions.

#### Scenario: Select profile from list
- **WHEN** the user clicks a profile in the profiles list
- **THEN** that profile becomes active and its settings are displayed in the editor

### Requirement: Excluded files/folders can be configured per profile
The system SHALL maintain a list of file/folder patterns excluded when copying source to WSL.

#### Scenario: Add exclusion pattern
- **WHEN** the user adds a pattern "*.pyc" to the exclusion list
- **THEN** the pattern is saved and applied during WSL copy

#### Scenario: Remove exclusion pattern
- **WHEN** the user removes a pattern from the exclusion list
- **THEN** the pattern is no longer excluded during copy

### Requirement: Deletion exclusion list can be configured per profile
The system SHALL maintain a list of files/folders in the WSL working directory that are NOT deleted during Clean.

#### Scenario: Add deletion exclusion
- **WHEN** the user adds ".buildozer" to the deletion exclusion list
- **THEN** the pattern is saved and Applied during Clean operations
