## ADDED Requirements

### Requirement: Dialog dismissal does not exit the application
When a dialog is dismissed via the Escape key, the application SHALL remain running.

#### Scenario: Dismissing a dialog with Escape keeps the app open
- **WHEN** a dialog is open and the user presses Escape
- **THEN** the dialog dismisses
- **THEN** the application remains running
