# Action Execution

## Purpose

Execute build pipeline actions (Clean, Build, Pull APK, Run) with real-time status, cancellation support, and validation of required profile fields before execution.

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

### Requirement: User can execute the Pull APK action
The system SHALL locate the built APK in the WSL `bin/` directory (project-level bin, not `.buildozer/bin/`) by matching the expected filename from `buildozer.spec` and copy it to `sourcedir/bin` on Windows with detailed logging at each step.

#### Scenario: Pull APK after build
- **WHEN** the user runs Pull APK after a successful build
- **THEN** the system reads `buildozer.spec` to derive the expected APK name
- **THEN** the system searches `wsl_dir/bin/` for matching `*.apk` files
- **THEN** the system logs count and names of found APKs and which is selected
- **THEN** the system copies it to `sourcedir/bin/`
- **THEN** the system logs the copied APK filename, source WSL path, and destination path

#### Scenario: No buildozer.spec found
- **WHEN** the `buildozer.spec` file does not exist in the local sourcedir
- **THEN** the system logs an error: "buildozer.spec not found"
- **THEN** the action stops immediately with status Failed

#### Scenario: No matching APK found
- **WHEN** no APK file matching the spec name is found in `wsl_dir/bin/`
- **THEN** the system logs the search path and expected filename pattern
- **THEN** the system returns an empty result and sets action status to Failed

### Requirement: Run action uses package name for launch
The Run action SHALL extract the package name from the `buildozer.spec` and pass it to the ADB launch command. The Run action SHALL install the APK from the local `sourcedir/bin/` directory (copied there by Pull APK), not from WSL.

#### Scenario: Run with package name
- **WHEN** the user runs Run after Pull APK
- **THEN** the system reads `buildozer.spec` from the local sourcedir
- **THEN** the system logs the extracted package name
- **THEN** the system finds the APK in `sourcedir/bin/` matching the spec name
- **THEN** the system installs the APK via ADB
- **THEN** the system launches using `adb shell monkey -p <package> -c android.intent.category.LAUNCHER 1`
- **THEN** the system logs the ADB commands being executed

#### Scenario: spec not found stops Run
- **WHEN** the `buildozer.spec` is not found in the local sourcedir
- **THEN** the system logs an error: "buildozer.spec not found — cannot determine package name"
- **THEN** the action stops immediately with status Failed

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
