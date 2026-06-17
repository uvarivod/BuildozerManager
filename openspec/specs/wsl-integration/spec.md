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

### Requirement: System can execute Buildozer commands in WSL
The system SHALL run `buildozer` commands inside the configured WSL distribution within the working directory.

#### Scenario: Run buildozer build
- **WHEN** the user runs Build
- **THEN** the system executes `buildozer android debug` inside the WSL working directory
- **THEN** stdout and stderr are streamed in real-time to the log viewer

#### Scenario: Use configured distribution
- **WHEN** the profile has WSL distribution "Ubuntu-22.04"
- **THEN** the system uses `wsl.exe --distribution Ubuntu-22.04` for all WSL commands

### Requirement: System can clean the WSL working directory
The system SHALL delete all files and folders inside the WSL working directory, respecting the deletion exclusion list.

#### Scenario: Clean WSL directory
- **WHEN** the user runs Clean
- **THEN** all files in the WSL working directory are deleted except those in the exclusion list
- **THEN** the system logs the cleaning operation

### Requirement: System reports WSL connectivity status
The system SHALL check if the configured WSL distribution is running before executing any WSL commands.

#### Scenario: WSL not running
- **WHEN** WSL is not running and the user starts an action
- **THEN** the system shows an error message: "WSL distribution '<name>' is not running. Please start it."
- **THEN** the action is not executed

#### Scenario: WSL is running
- **WHEN** WSL is running
- **THEN** the system proceeds with the requested action
