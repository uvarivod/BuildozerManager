## ADDED Requirements

### Requirement: WSLService provides sync_src method
The system SHALL provide a `sync_src()` method on WSLService that: deletes all files in the WSL project directory except `.buildozer`, then copies source files from the local sourcedir.

#### Scenario: SyncSRC via WSLService
- **WHEN** `sync_src()` is called with a valid profile
- **THEN** the WSL project directory is cleared of all files except `.buildozer`
- **THEN** source files from `profile.sourcedir` are copied to the WSL project directory

### Requirement: WSLService provides clean_wsl_project method
The system SHALL provide a `clean_wsl_project()` method on WSLService that deletes ALL files in the WSL project directory including `.buildozer`, ignoring the profile exclusion list.

#### Scenario: CleanWSLProject via WSLService
- **WHEN** `clean_wsl_project()` is called with a valid profile
- **THEN** all files in the WSL project directory including `.buildozer` are deleted

## REMOVED Requirements

### Requirement: WSLService provides clean_wsl_dir method
**Reason**: Replaced by `sync_src()` and `clean_wsl_project()` with clearer semantics.
**Migration**: All callers use `sync_src()` (preserves `.buildozer`) or `clean_wsl_project()` (removes `.buildozer`) instead.
