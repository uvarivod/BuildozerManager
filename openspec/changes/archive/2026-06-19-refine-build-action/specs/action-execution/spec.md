## ADDED Requirements

### Requirement: Action execution emits RUNNING state
The system SHALL emit ActionState.RUNNING when an action begins execution. The UI SHALL update the status label to reflect the current running state in real time.

#### Scenario: Build shows running status
- **WHEN** the user clicks Build
- **THEN** the status label immediately changes to "Running: BUILD"
- **THEN** the UI remains responsive during the build

### Requirement: Duration timer resets per action
The duration timer SHALL reset to 00:00:00 when any action starts and stop when the action completes, showing the total elapsed time for that action.

#### Scenario: Duration shows action time
- **WHEN** the user clicks Build and the action runs for 30 seconds
- **THEN** the duration display increments from 00:00:00 to 00:00:30
- **THEN** when the action completes (success/fail/cancel), the timer stops

### Requirement: Buildozer output is parsed for progress
The system SHALL parse buildozer output lines to show meaningful progress indications instead of raw output.

#### Scenario: Build steps are visible
- **WHEN** buildozer outputs step headers like `# Install platform`
- **THEN** they are logged as info-level messages with source "buildozer"
- **WHEN** buildozer outputs `[INFO]:` lines
- **THEN** they are logged as info-level messages
- **WHEN** buildozer outputs `[WARN]:` lines
- **THEN** they are logged as warning-level messages

### Requirement: User is warned if .buildozer is unprotected
Before cleaning the WSL build directory, if `.buildozer` is not in the Retain During Sync list, the system SHALL show a confirmation popup with options.

#### Scenario: Missing .buildozer protection
- **WHEN** the user clicks Build and `.buildozer` is not in Retain During Sync
- **THEN** a popup appears: "Warning: .buildozer is not protected. This will trigger a clean build."
- **THEN** the user can choose: "Continue", "Add to exclusions and continue", or "Stop"

## MODIFIED Requirements

### Requirement: User can execute the Build action
The system SHALL: warn if .buildozer is unprotected, clean (respecting Retain During Sync), copy source to WSL, then run the buildozer build command with parsed output in the WSL working directory.

#### Scenario: Full build cycle with protections
- **WHEN** the user runs Build on an active profile with .buildozer in Retain During Sync
- **THEN** the system cleans the WSL working directory (preserving Retain During Sync items)
- **THEN** the system copies source files from sourcedir to WSL working directory excluding excluded_files
- **THEN** the system runs buildozer in WSL with proper PATH setup and parsed output logging
- **THEN** the system shows build duration on completion

#### Scenario: Build with unprotected .buildozer
- **WHEN** the user runs Build and .buildozer is NOT in Retain During Sync
- **THEN** a confirmation popup is shown before the action proceeds
- **THEN** the user can choose to stop, continue, or add to exclusions

#### Scenario: Build fails validation if paths are empty
- **WHEN** the profile has empty sourcedir, spec_path, wsl_dir, or wsl_distro
- **THEN** the action is rejected with a message listing missing fields

### Requirement: Action execution shows real-time status
The system SHALL display the current action name and RUNNING state during execution, and reset the duration timer on each new action.

#### Scenario: Action progress display
- **WHEN** an action is running
- **THEN** the UI shows the action name and "Running" status
- **THEN** the duration timer shows elapsed time for this action
- **THEN** the UI remains responsive (non-blocking)

### Requirement: User can cancel a running action
The system SHALL allow cancellation of any running action via a Cancel button and log the cancellation with duration.

#### Scenario: Cancel during build
- **WHEN** the user clicks Cancel during a Build action
- **THEN** the running subprocess is terminated
- **THEN** the action status is set to "Cancelled"
- **THEN** the timer stops and duration is logged with the cancellation
