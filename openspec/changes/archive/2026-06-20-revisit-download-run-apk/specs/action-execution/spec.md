# Action Execution

## Purpose

Execute build pipeline actions (Clean, Build, Pull APK, Run) with real-time status, cancellation support, and validation of required profile fields before execution.

## ADDED Requirements

### Requirement: User can execute the Pull APK action
The system SHALL locate the built APK in the WSL `bin/` directory (project-level bin, not `.buildozer/bin/`) by matching the expected filename from `buildozer.spec`, copy it to `sourcedir/bin` on Windows, and return the destination path for downstream use. The system SHALL show detailed logs at each step.

#### Scenario: Pull APK after build
- **WHEN** the user runs Pull APK after a successful build
- **THEN** the system reads `buildozer.spec` from WSL to derive the expected APK name
- **THEN** the system searches `wsl_dir/bin/` for matching `*.apk` files
- **THEN** the system logs how many APK files were found, their names, and which one was selected
- **THEN** the system copies it to `sourcedir/bin/`
- **THEN** the system returns the destination path
- **THEN** the system logs the copied filename, source WSL path, and local destination path

#### Scenario: No buildozer.spec found
- **WHEN** the `buildozer.spec` file does not exist in the WSL working directory
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
- **THEN** the system reads `buildozer.spec` from the WSL working directory
- **THEN** the system logs the extracted package name
- **THEN** the system finds the APK in `sourcedir/bin/` matching the spec name
- **THEN** the system installs the APK via ADB
- **THEN** the system launches using `adb shell monkey -p <package> -c android.intent.category.LAUNCHER 1`
- **THEN** the system logs the ADB commands being executed

#### Scenario: spec not found stops Run
- **WHEN** the `buildozer.spec` is not found in the WSL working directory
- **THEN** the system logs an error: "buildozer.spec not found — cannot determine package name"
- **THEN** the action stops immediately with status Failed

## MODIFIED Requirements

### Requirement: User can execute the Download action
**FROM:** User can execute the Download action
**TO:** User can execute the Pull APK action

The system SHALL locate the built APK in the WSL `bin/` directory (project-level bin, not `.buildozer/bin/`) by matching the expected filename from `buildozer.spec` and copy it to `sourcedir/bin` on Windows with detailed logging at each step.

#### Scenario: Pull APK after build
- **WHEN** the user runs Pull APK after a successful build
- **THEN** the system reads `buildozer.spec` to derive the expected APK name
- **THEN** the system searches `wsl_dir/bin/` for matching `*.apk` files
- **THEN** the system logs count and names of found APKs and which is selected
- **THEN** the system copies it to `sourcedir/bin/`
- **THEN** the system logs the copied APK filename, source WSL path, and destination path
