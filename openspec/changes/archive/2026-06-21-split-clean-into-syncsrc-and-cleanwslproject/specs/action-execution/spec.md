## MODIFIED Requirements

### Requirement: User can execute the Clean action
The system SHALL delete all files and folders in the WSL working directory, including `.buildozer`, ignoring any profile exclusions.

#### Scenario: Clean removes everything
- **WHEN** the user runs Clean on a profile
- **THEN** the WSL working directory is completely emptied including `.buildozer`
- **THEN** the system logs each deleted file and the total operation duration

### Requirement: User can execute the Build action
The system SHALL: sync source files (preserving `.buildozer`), copy source to WSL, then run the buildozer build command with parsed output in the WSL working directory.

#### Scenario: Full build cycle with automatic .buildozer preservation
- **WHEN** the user runs Build on an active profile
- **THEN** the system runs SyncSRC (deletes WSL working directory except `.buildozer`, copies source from sourcedir)
- **THEN** the system runs buildozer in WSL with proper PATH setup and parsed output logging
- **THEN** the system shows build duration on completion

## REMOVED Requirements

### Requirement: User is warned if .buildozer is unprotected
**Reason**: SyncSRC always preserves `.buildozer`, making the warning unnecessary.
**Migration**: The `.buildozer` protection popup is removed. Build action always preserves `.buildozer` without prompting.

### Requirement: Build with unprotected .buildozer
**Reason**: Replaced by SyncSRC which unconditionally preserves `.buildozer`.
**Migration**: No equivalent scenario. Build now always preserves `.buildozer` silently.
