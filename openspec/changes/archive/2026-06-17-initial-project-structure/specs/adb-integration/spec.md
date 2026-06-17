## ADDED Requirements

### Requirement: System can detect connected ADB devices
The system SHALL run `adb devices` to list connected Android devices and display the status.

#### Scenario: List connected devices
- **WHEN** the user opens the ADB panel or runs a Run action
- **THEN** the system executes `adb devices -l` and displays the device list
- **THEN** each device is shown with its serial number and state (device/unauthorized/offline)

#### Scenario: No devices connected
- **WHEN** no devices are connected
- **THEN** the system shows "No devices connected" message

### Requirement: System can install APK on connected device via ADB
The system SHALL install the downloaded APK onto the first connected device using `adb install -r`.

#### Scenario: Install APK successfully
- **WHEN** the user runs the Run action and a device is connected
- **THEN** the system executes `adb install -r <path-to-apk>`
- **THEN** the system logs the installation output
- **THEN** the system reports "Install successful"

#### Scenario: Install failure
- **WHEN** APK installation fails (e.g., incompatible architecture)
- **THEN** the system logs the error output from ADB
- **THEN** the action status is set to "Failed"

### Requirement: System can launch app on device via ADB
The system SHALL launch the installed app using `adb shell am start -n <package>/<activity>`.

#### Scenario: Launch app
- **WHEN** the user runs Run and installation succeeds
- **THEN** the system runs `adb shell monkey -p <package> 1` or `adb shell am start -n <package>/<activity>`
- **THEN** the system logs the launch command and output

### Requirement: ADB path is configurable
The system SHALL allow the user to specify a custom path to `adb.exe` in the profile settings.

#### Scenario: Use custom ADB path
- **WHEN** the profile has a custom adb_path set
- **THEN** all ADB commands use that path instead of `adb` from PATH
