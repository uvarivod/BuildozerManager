# Escape Key Behavior

## Purpose

Ensure the Escape key never exits the application; the app SHALL only exit through an explicit user close action such as the window close button.

## Requirements

### Requirement: Escape key does not close the application
The application SHALL remain running when the user presses the Escape key, regardless of whether a dialog is open.

#### Scenario: Pressing Escape with no dialog open
- **WHEN** the user presses Escape while no dialog is open
- **THEN** the application continues running

#### Scenario: Pressing Escape with a dialog open
- **WHEN** the user presses Escape while a dialog is open
- **THEN** the dialog dismisses
- **THEN** the application continues running

### Requirement: Exit requires explicit user action
The application SHALL exit only through an explicit close action such as the window close button, never via the Escape key.

#### Scenario: Window close button still exits
- **WHEN** the user clicks the window close button
- **THEN** the application exits

#### Scenario: Escape never triggers exit
- **WHEN** the user presses Escape
- **THEN** the application stays open without an exit prompt

### Requirement: Exit-on-escape disabled before window creation
The application SHALL set the Kivy config option `exit_on_escape` to `0` before the application window is created.

#### Scenario: Config applied at startup
- **WHEN** the application starts
- **THEN** `Config.set('kivy', 'exit_on_escape', '0')` is invoked before any window is created
