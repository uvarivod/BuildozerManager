# ADB Integration

## Purpose

Interact with Android devices via ADB — detect connected devices, install APKs, and launch apps using a configurable ADB path.

## ADDED Requirements

### Requirement: User can select a target device when multiple are connected
When multiple ADB devices are connected, the system SHALL prompt the user to select which device to install and launch onto.

#### Scenario: Device selection popup
- **WHEN** the Run action detects 2+ connected devices
- **THEN** a device selection popup lists all connected devices by serial number
- **THEN** the selected device receives the APK installation and launch commands

#### Scenario: Single device skips selection
- **WHEN** exactly one device is connected
- **THEN** the system proceeds without a selection popup

### Requirement: System can launch app using package name from buildozer.spec
The system SHALL use the package name extracted from `buildozer.spec` (via APK discovery service) when launching the app, and SHALL log the full ADB command being executed.

#### Scenario: Launch with extracted package name
- **WHEN** the Run action proceeds to launch
- **THEN** the system extracts the package name from `buildozer.spec`
- **THEN** the system logs the package name and the full ADB command being executed
- **THEN** the system executes `adb shell monkey -p <package> -c android.intent.category.LAUNCHER 1`

#### Scenario: No package name available
- **WHEN** the package name cannot be determined from `buildozer.spec`
- **THEN** the system logs an error and sets the action state to Failed

## MODIFIED Requirements

### Requirement: System can launch app on device via ADB
The system SHALL launch the installed app using the package name from the buildozer.spec. The system SHALL use `adb shell monkey -p <package> 1` when no activity is specified, or `adb shell am start -n <package>/<activity>` when the activity is known. The system SHALL log the full ADB command before execution and the output after.

#### Scenario: Launch app with package name and logging
- **WHEN** the user runs Run and installation succeeds
- **THEN** the system reads the package name from the buildozer.spec
- **THEN** the system logs "Launching <package> on device <serial>..."
- **THEN** the system logs the full ADB command (e.g., `adb -s <serial> shell monkey -p <package> -c android.intent.category.LAUNCHER 1`)
- **THEN** the system runs the ADB command
- **THEN** the system logs the command output

### Requirement: System logs connected devices on Run
The system SHALL log the list of connected ADB devices and their states when the Run action begins.

#### Scenario: Devices logged at start of Run
- **WHEN** the Run action starts
- **THEN** the system runs `adb devices -l`
- **THEN** the system logs each connected device with its serial and state
- **THEN** the system logs the total device count
