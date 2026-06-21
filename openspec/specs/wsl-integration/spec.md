# WSL Integration

## Purpose

Integrate with Windows Subsystem for Linux to copy source files, execute Buildozer commands, and clean working directories within a configured WSL distribution.

## Requirements

### Requirement: System can copy source files from Windows to WSL
The system SHALL copy all files from the profile's sourcedir to the WSL working directory, excluding configured patterns.

#### Scenario: Copy source to WSL
- **WHEN** the user runs Build on a profile with sourcedir "C:\Projects\MyApp"
- **THEN** the system copies all non-excluded files to the WSL working directory
- **THEN** the system logs each copied file or a summary count

#### Scenario: Respect exclusion patterns during copy
- **WHEN** copying with exclusions "*.pyc" and ".git"
- **THEN** no .pyc files or .git directory are copied

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

### Requirement: WSLService provides sync_src method
The system SHALL provide a `sync_src()` method on WSLService that deletes all files in the WSL project directory except `.buildozer` (hardcoded) and the profile's Retain During Sync items, then copies source files from the local sourcedir.

#### Scenario: SyncSRC preserves .buildozer and user exclusions
- **WHEN** `sync_src()` is called with a valid profile
- **THEN** the WSL project directory is cleared of all files except `.buildozer` and items in the profile's Retain During Sync list
- **THEN** source files from `profile.sourcedir` are copied to the WSL project directory

### Requirement: WSLService provides clean_wsl_project method
The system SHALL provide a `clean_wsl_project()` method on WSLService that deletes ALL files in the WSL project directory including `.buildozer`, ignoring all exclusions.

#### Scenario: CleanWSLProject removes everything
- **WHEN** `clean_wsl_project()` is called with a valid profile
- **THEN** all files in the WSL project directory including `.buildozer` are deleted

### Requirement: System reports WSL connectivity status
The system SHALL check if the configured WSL distribution is running before executing any WSL commands.

#### Scenario: WSL not running
- **WHEN** WSL is not running and the user starts an action
- **THEN** the system shows an error message: "WSL distribution '<name>' is not running. Please start it."
- **THEN** the action is not executed

#### Scenario: WSL is running
- **WHEN** WSL is running
- **THEN** the system proceeds with the requested action
