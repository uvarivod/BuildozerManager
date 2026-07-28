## ADDED Requirements

### Requirement: Dialog helper module provides factory functions
The system SHALL provide a `dialog_helper.py` module with factory functions for creating common dialog types: info, confirm, error, success, and form dialogs.

#### Scenario: Import dialog helpers
- **WHEN** a screen module imports from `dialog_helper`
- **THEN** the module exports `show_info_dialog()`, `show_confirm_dialog()`, `show_error_dialog()`, `show_success_dialog()`, `show_form_dialog()`, and `show_toast()`

### Requirement: Info dialog displays message with OK button
The `show_info_dialog()` function SHALL create a Popup with a message Label and an OK Button that dismisses the popup.

#### Scenario: Show info dialog
- **WHEN** a screen calls `show_info_dialog(title="Help", message="Click OK to continue")`
- **THEN** a Popup opens with title "Help", body text "Click OK to continue", and an OK button
- **THEN** clicking OK dismisses the popup

### Requirement: Confirm dialog displays message with Cancel and Confirm buttons
The `show_confirm_dialog()` function SHALL create a Popup with a message Label, a Cancel Button, and a Confirm Button. The Confirm button SHALL invoke a callback before dismissing.

#### Scenario: Show confirm dialog with callback
- **WHEN** a screen calls `show_confirm_dialog(title="Delete?", message="Are you sure?", on_confirm=my_callback)`
- **THEN** a Popup opens with "Cancel" and "Delete" buttons
- **THEN** clicking "Delete" calls `my_callback()` and dismisses the popup
- **THEN** clicking "Cancel" dismisses the popup without calling the callback

### Requirement: Error dialog displays error message with OK button
The `show_error_dialog()` function SHALL create a Popup styled with red accent displaying an error message and an OK button.

#### Scenario: Show error dialog
- **WHEN** a screen calls `show_error_dialog(title="Error", message="Something went wrong")`
- **THEN** a Popup opens with red-themed styling and an OK button

### Requirement: Success dialog displays success message with OK button
The `show_success_dialog()` function SHALL create a Popup styled with green accent displaying a success message and an OK button.

#### Scenario: Show success dialog
- **WHEN** a screen calls `show_success_dialog(title="Saved", message="Settings saved successfully")`
- **THEN** a Popup opens with green-themed styling and an OK button

### Requirement: Form dialog displays form fields with Save and Cancel buttons
The `show_form_dialog()` function SHALL create a Popup with dynamic form fields (labels + text inputs), a Save Button, and a Cancel Button. The Save button SHALL collect field values and invoke a callback.

#### Scenario: Show form dialog with fields
- **WHEN** a screen calls `show_form_dialog(title="Edit Action", fields=["Name", "Description"], on_save=my_callback)`
- **THEN** a Popup opens with two labeled TextInput fields
- **THEN** clicking "Save" calls `my_callback({"Name": "...", "Description": "..."})` and dismisses
- **THEN** clicking "Cancel" dismisses without calling the callback

### Requirement: Toast auto-dismisses after timeout
The `show_toast()` function SHALL create a small Popup at bottom-center that auto-dismisses after 2 seconds without user interaction.

#### Scenario: Show toast notification
- **WHEN** a screen calls `show_toast(message="Settings saved")`
- **THEN** a small popup appears at bottom-center with text "Settings saved"
- **THEN** the popup automatically dismisses after 2 seconds

### Requirement: All dialogs use consistent dark theme styling
All dialogs created by the dialog helper module SHALL use consistent dark theme colors: dark gray background, light gray text, green for positive actions, red for destructive actions.

#### Scenario: Dialog styling matches app theme
- **WHEN** any dialog is displayed
- **THEN** the background color is dark gray (0.15, 0.15, 0.15, 1)
- **THEN** text color is light gray (0.85, 0.85, 0.85, 1)
- **THEN** positive buttons use green (0.2, 0.6, 0.2, 1)
- **THEN** destructive buttons use red (0.8, 0.2, 0.2, 1)

### Requirement: All dialogs support keyboard dismiss
All dialogs SHALL support keyboard shortcuts: Escape to dismiss, Enter to confirm (for dialogs with a confirm/save button).

#### Scenario: Escape key dismisses dialog
- **WHEN** a dialog is open and the user presses Escape
- **THEN** the dialog dismisses

#### Scenario: Enter key confirms dialog
- **WHEN** a confirm/form dialog is open and the user presses Enter
- **THEN** the confirm/save callback is invoked and the dialog dismisses

### Requirement: Confirmation dialogs prevent accidental dismissal
Confirm, error, and form dialogs SHALL set `auto_dismiss=False` to prevent dismissal by clicking outside the popup.

#### Scenario: Clicking outside confirm dialog does not dismiss
- **WHEN** a confirm dialog is open and the user clicks outside the popup
- **THEN** the popup remains open

### Requirement: Dialog sizes are standardized by type
The dialog helper SHALL use standardized sizes: info (0.4, 0.25), confirm (0.45, 0.3), error (0.5, 0.3), success (0.4, 0.25), form (0.6, 0.5).

#### Scenario: Dialog uses correct size
- **WHEN** `show_error_dialog()` is called
- **THEN** the popup size is (0.5, 0.3) relative to parent
