## ADDED Requirements

### Requirement: System checks buildozer.spec exists before building
The system SHALL verify that `buildozer.spec` exists in the WSL build directory before running the buildozer command, and log a clear warning if it is missing.

#### Scenario: buildozer.spec exists
- **WHEN** the Build action reaches the buildozer execution phase
- **THEN** the system checks for `buildozer.spec` in the WSL build directory
- **THEN** if found, the build proceeds normally

#### Scenario: buildozer.spec missing
- **WHEN** the Build action checks and `buildozer.spec` is not found in the WSL build directory
- **THEN** the system logs a warning: "buildozer.spec not found in WSL build directory"
- **THEN** the build continues (buildozer will report its own error)

## MODIFIED Requirements

### Requirement: System can execute Buildozer commands in WSL
The system SHALL run `buildozer` commands inside the configured WSL distribution within the working directory, with the user's local bin PATH exported.

#### Scenario: Run buildozer build
- **WHEN** the user runs Build
- **THEN** the system exports PATH to include `~/.local/bin`
- **THEN** the system executes `buildozer android debug` inside the WSL build directory
- **THEN** stdout and stderr are streamed in real-time to the log viewer with parsed step information

#### Scenario: Use configured distribution
- **WHEN** the profile has WSL distribution "Ubuntu-22.04"
- **THEN** the system uses `wsl.exe --distribution Ubuntu-22.04` for all WSL commands

### Requirement: System can clean the WSL working directory
The system SHALL delete all files and folders inside the WSL working directory, respecting the Retain During Sync list.

#### Scenario: Clean WSL directory with Retain During Sync
- **WHEN** the user runs Clean or the clean phase of Build
- **THEN** all files in the WSL build directory are deleted except those in the Retain During Sync list
- **THEN** the system logs the cleaning operation

FROM: deleting those in the deletion exclusion list
TO: deleting those NOT in the Retain During Sync list
