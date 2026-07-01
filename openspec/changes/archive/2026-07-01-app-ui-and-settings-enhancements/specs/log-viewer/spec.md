## ADDED Requirements

### Requirement: Log auto-save uses configured log directory
The system SHALL save session log files to the user-configured log directory (from Settings) instead of a hardcoded `logs/` path.

#### Scenario: Auto-save uses configured directory
- **WHEN** the user has configured a custom log directory in Settings
- **THEN** session logs are auto-saved to that directory
- **WHEN** no custom directory is configured
- **THEN** session logs are auto-saved to the default `logs/` directory

### Requirement: Log cleanup runs after execution completes
The system SHALL trigger log directory cleanup after each scenario or action run, respecting the configured max log size.

#### Scenario: Post-execution cleanup
- **WHEN** a scenario or individual action finishes execution
- **THEN** the log cleanup mechanism checks the log directory size
- **THEN** oldest log files are deleted if the size exceeds the configured limit
