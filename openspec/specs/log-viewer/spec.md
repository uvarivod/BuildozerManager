# Log Viewer

## Purpose

Display real-time build and action logs with color-coded levels, timestamps, execution duration, save-to-file, and clear functionality.

## Requirements

### Requirement: Log viewer shows real-time output
The system SHALL display log output in a scrollable text view that auto-scrolls to the newest entry.

#### Scenario: Real-time log streaming
- **WHEN** a build action is running
- **THEN** each new log line appears in the log viewer immediately
- **THEN** the view auto-scrolls to show the latest line

### Requirement: Log entries are color-coded by level
The system SHALL color log lines: INFO (white/gray), WARN (yellow), ERROR (red), DEBUG (blue), SUCCESS (green).

#### Scenario: Color-coded log display
- **WHEN** a WARN message is logged
- **THEN** it appears in yellow text
- **WHEN** an ERROR message is logged
- **THEN** it appears in red text

### Requirement: Each log entry has a timestamp
The system SHALL prepend each log line with `[YYYY-MM-DD HH:MM:SS]` timestamp.

#### Scenario: Timestamped entries
- **WHEN** a log entry is created
- **THEN** it is displayed as `[2026-06-17 11:30:00] Starting build...`

### Requirement: Execution duration is shown
The system SHALL display the elapsed time since the current action/scenario started, updated every 0.5 seconds.

#### Scenario: Duration display
- **WHEN** an action has been running for 2 minutes 30 seconds
- **THEN** the UI shows "Duration: 00:02:30"

### Requirement: Log can be saved to a file
The system SHALL allow saving the current session log to a text file.

#### Scenario: Save log to file
- **WHEN** the user clicks "Save Log"
- **THEN** a file save dialog opens
- **THEN** all log entries are written to the chosen file with timestamps

### Requirement: Log viewer can be cleared
The system SHALL allow clearing the current log display.

#### Scenario: Clear log
- **WHEN** the user clicks "Clear Log"
- **THEN** all log entries are removed from the display

### Requirement: Text selection with SHIFT+click range-select
The system SHALL support selecting log text by click-drag within the viewport and by SHIFT+click range selection across arbitrarily distant lines.

#### Scenario: SHIFT+click range selection
- **WHEN** the user clicks a line in the log panel to set an anchor
- **AND** then SHIFT+clicks a different visible line
- **THEN** all text between the anchor and the clicked line is selected

#### Scenario: Plain click resets anchor
- **WHEN** the user plain-clicks a new line after a previous selection
- **THEN** the selection anchor is reset to the new click position
- **THEN** a subsequent SHIFT+click selects from the new anchor

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
