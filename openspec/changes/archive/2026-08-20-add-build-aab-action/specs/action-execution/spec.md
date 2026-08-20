## ADDED Requirements

### Requirement: User can execute the Build AAB action
The system SHALL provide a "Build AAB" action that runs the buildozer release build (`buildozer android release`) in the profile's WSL working directory using the same execution pipeline as the existing Build action (PATH setup, `cd` into the WSL build directory, live output parsing, progress logging, and cancellation support).

#### Scenario: Build AAB runs the release command
- **WHEN** the user runs the Build AAB action with a valid profile (sourcedir, wsl_dir, wsl_distro)
- **THEN** WSL running is verified first
- **THEN** the system checks for `buildozer.spec` in the WSL build directory and logs a warning if it is missing
- **THEN** the system runs `buildozer android release` in the WSL working directory with proper PATH setup
- **THEN** buildozer output is parsed and logged with progress indicators (steps, downloads, percentages)
- **THEN** the action finishes with status Success when the build completes

#### Scenario: Build AAB fails validation if paths are empty
- **WHEN** the profile has empty sourcedir, wsl_dir, or wsl_distro
- **THEN** the action is rejected with a message listing missing fields

#### Scenario: WSL not running stops Build AAB
- **WHEN** WSL is not running and the user starts the Build AAB action
- **THEN** the system logs an error "WSL is not running"
- **THEN** the action is not executed and returns status Failed

#### Scenario: Cancel during Build AAB
- **WHEN** the user cancels the Build AAB action while it is running
- **THEN** the running subprocess is terminated
- **THEN** the action status is set to Cancelled

### Requirement: Build AAB is available in the scenario editor
The system SHALL expose the Build AAB action in the scenario editor action palette so it can be added to scenarios and run as a standalone action, consistent with the other actions.

#### Scenario: Build AAB appears in the action palette
- **WHEN** the user opens the scenario editor
- **THEN** a Build AAB action chip is available in the action palette
- **THEN** adding it to a scenario inserts `Action.BUILD_AAB` into the action sequence

#### Scenario: Build AAB runs separately
- **WHEN** "Allow running separately" is enabled and the user clicks the Build AAB card
- **THEN** the action executes and reports its status (Running / Success / Failed / Cancelled) like any other action card