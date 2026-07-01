## ADDED Requirements

### Requirement: Log cleanup runs after build completion
The system SHALL check the configured log directory size after each scenario/action run and delete oldest log files if the size exceeds the configured maximum.

#### Scenario: Cleanup triggered after scenario completes
- **WHEN** a scenario or action finishes executing
- **THEN** the system calculates the total size of the configured log directory
- **WHEN** the total size exceeds `max_log_size_mb`
- **THEN** the oldest log files (by modification time) are deleted until the total size is below the limit

#### Scenario: Cleanup not triggered when under limit
- **WHEN** a scenario or action finishes executing
- **AND** the log directory size is below `max_log_size_mb`
- **THEN** no files are deleted

### Requirement: Currently open log files are skipped during cleanup
The system SHALL NOT delete log files that are currently being written to by the application.

#### Scenario: Active session log is preserved
- **WHEN** cleanup is triggered during a running session
- **THEN** the current session's auto-save log file is excluded from deletion
- **THEN** only previously completed session logs are candidates for deletion

### Requirement: Cleanup respects user-configured log directory
The system SHALL clean up files only within the user-configured log directory path.

#### Scenario: Custom log directory cleanup
- **WHEN** the user has configured a custom log directory
- **THEN** cleanup operates on that directory, not the default `logs/` directory
