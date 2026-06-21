## MODIFIED Requirements

### Requirement: System provides predefined scenarios
The system SHALL include these built-in scenarios: "Build", "Clean Build", "Clean Build + Patch", "Build and Run".

#### Scenario: Build
- **WHEN** the user selects "Build"
- **THEN** the system runs SyncSRC (preserves `.buildozer`, replaces all other files)
- **THEN** the system runs buildozer build

#### Scenario: Clean Build
- **WHEN** the user selects "Clean Build"
- **THEN** the system runs CleanWSLProject (deletes everything including `.buildozer`)
- **THEN** the system runs SyncSRC (copies fresh source)
- **THEN** the system runs buildozer clean
- **THEN** the system runs buildozer build

#### Scenario: Clean Build + Patch
- **WHEN** the user selects "Clean Build + Patch"
- **THEN** the system runs CleanWSLProject
- **THEN** the system runs SyncSRC
- **THEN** the system runs buildozer clean
- **THEN** the system runs buildozer build
- **THEN** the system applies all active patches to .buildozer
