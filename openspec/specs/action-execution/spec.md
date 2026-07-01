# Action Execution

## Purpose

Execute build pipeline actions (Clean, Build, Pull APK, Run) with real-time status, cancellation support, and validation of required profile fields before execution.

## Requirements

### Requirement: User can execute the Clean action
The system SHALL delete ALL files and folders in the WSL working directory, including `.buildozer`.

#### Scenario: Clean with exclusions
- **WHEN** the user runs Clean
- **THEN** the WSL working directory is completely emptied, including .buildozer
- **THEN** the system logs each deleted file and the total operation duration

#### Scenario: Clean fails validation if paths are empty
- **WHEN** the profile has empty wsl_dir or wsl_distro
- **THEN** the action is rejected with a message listing missing fields

### Requirement: User can execute the Build action
The system SHALL: sync source to WSL (via SyncSRC), then run the buildozer build command with parsed output in the WSL working directory.

#### Scenario: Full build cycle
- **WHEN** the user runs Build
- **THEN** the system syncs source files from sourcedir to WSL working directory excluding excluded_files
- **THEN** the system runs buildozer in WSL with proper PATH setup and parsed output logging
- **THEN** the system shows build duration on completion

#### Scenario: Build fails validation if paths are empty
- **WHEN** the profile has empty sourcedir, spec_path, wsl_dir, or wsl_distro
- **THEN** the action is rejected with a message listing missing fields

### Requirement: User can execute the Pull APK action
The system SHALL locate the built APK in the WSL `bin/` directory (project-level bin, not `.buildozer/bin/`) by matching the expected filename from `buildozer.spec` and copy it to `sourcedir/bin` on Windows with detailed logging at each step. The search is performed via the Windows network path (`\\wsl$\<distro>\<dir>\bin`), not via a WSL command.

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

### Requirement: Build action does not check .buildozer protection
The Build action does NOT check whether `.buildozer` is in the exclusions list and does NOT show a confirmation popup. The SyncSRC step always preserves `.buildozer` regardless.

### Requirement: Action execution emits RUNNING state
The system SHALL emit ActionState.RUNNING when an action begins execution. The UI SHALL update the status label to reflect the current running state in real time.

#### Scenario: Build shows running status
- **WHEN** the user triggers an action (via card click or scenario run)
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
- **WHEN** the user clicks Cancel during a Build action (triggered from card or scenario)
- **THEN** the running subprocess is terminated
- **THEN** the action status is set to "Cancelled"
- **THEN** the timer stops and duration is logged with the cancellation

### Requirement: Action execution is gated by "Allow running separately" flag
The system SHALL only allow individual action execution when the "Allow running actions separately" checkbox is enabled. Action cards in the chain show clickable buttons only when this flag is checked.

### Requirement: Individual action execution honors the "allow separately" flag
When a single action is triggered from an action card, the system SHALL check the "Allow running actions separately" flag. If disabled, the action SHALL NOT execute.

#### Scenario: Action blocked when separate execution disabled
- **WHEN** "Allow running actions separately" is unchecked
- **WHEN** the user clicks an action card's button
- **THEN** the action is not executed
