# Action Execution

## Purpose

Execute build pipeline actions (Clean, Build, Download) with real-time status, cancellation support, and validation of required profile fields before execution.

## Requirements

### Requirement: User can execute the Clean action
The system SHALL delete all files and folders in the WSL working directory, except those in the deletion exclusion list.

#### Scenario: Clean with exclusions
- **WHEN** the user runs Clean on a profile with ".buildozer" excluded
- **THEN** the WSL working directory is emptied except for the .buildozer directory
- **THEN** the system logs each deleted file and the total operation duration

#### Scenario: Clean fails validation if paths are empty
- **WHEN** the profile has empty wsl_dir or wsl_distro
- **THEN** the action is rejected with a message listing missing fields

### Requirement: User can execute the Build action
The system SHALL: clean (except .buildozer), copy source to WSL, then run the buildozer build command in the WSL working directory.

#### Scenario: Full build cycle
- **WHEN** the user runs Build on an active profile
- **THEN** the system cleans the WSL working directory (preserving .buildozer)
- **THEN** the system copies source files from sourcedir to WSL working directory
- **THEN** the system executes `buildozer android debug` in the WSL working directory
- **THEN** the system streams real-time buildozer output to the log viewer
- **THEN** the system shows build duration on completion

#### Scenario: Build fails validation if paths are empty
- **WHEN** the profile has empty sourcedir, spec_path, wsl_dir, or wsl_distro
- **THEN** the action is rejected with a message listing missing fields

### Requirement: User can execute the Download action
The system SHALL locate the built APK in the WSL `.buildozer` directory and copy it to `sourcedir/bin` on Windows.

#### Scenario: Download APK after build
- **WHEN** the user runs Download after a successful build
- **THEN** the system finds the APK file in the WSL .buildozer directory
- **THEN** the system copies it to sourcedir/bin
- **THEN** the system logs the APK filename and destination path

### Requirement: Action execution shows real-time status
The system SHALL display the current action name and status label during execution.

#### Scenario: Action progress display
- **WHEN** an action is running
- **THEN** the UI shows the action name and status
- **THEN** the UI remains responsive (non-blocking)

### Requirement: User can cancel a running action
The system SHALL allow cancellation of any running action via a Cancel button.

#### Scenario: Cancel during build
- **WHEN** the user clicks Cancel during a Build action
- **THEN** the running subprocess is terminated
- **THEN** the action status is set to "Cancelled"
- **THEN** the system logs the cancellation event with duration
