# Action Edit Dialog

## Purpose

TBD

## Requirements

### Requirement: Clicking a palette chip opens edit dialog
Clicking (touch-up within 10px of touch-down, no drag) on any palette chip SHALL open a Popup dialog showing the action's properties. The dialog title SHALL be the action name.

#### Scenario: Click open edit dialog
- **WHEN** the user clicks on the "BUILD" chip in the palette
- **THEN** a popup titled "BUILD" appears showing Name, Description, Type, Logic fields

### Requirement: Edit dialog is read-only for built-in actions
For built-in Action enum members, the edit dialog SHALL display all fields as disabled/read-only text inputs. No save or delete buttons SHALL appear.

#### Scenario: Built-in dialog read-only
- **WHEN** the dialog opens for a built-in action
- **THEN** all TextInput fields are disabled
- **THEN** no "Save" or "Delete" buttons are shown
- **THEN** only a "Close" button is available

### Requirement: Edit dialog is editable for custom actions
For custom actions, the edit dialog SHALL allow editing Name and Description fields. The Type field SHALL be read-only after creation. The Logic field SHALL be editable (file path for Action-type, text for Patch-type). A "Save" button SHALL persist changes. A "Delete" button SHALL remove the action after confirmation.

#### Scenario: Edit custom action fields
- **WHEN** the dialog opens for a custom action
- **WHEN** the user changes Name from "Deploy to Play Store" to "Deploy to Google Play"
- **WHEN** the user clicks "Save"
- **THEN** the action is updated in storage
- **THEN** the palette chip shows the new name

### Requirement: Edit dialog shows file chooser for Action-type Logic
For custom Action-type actions, the Logic field SHALL have a "Browse" button that opens a file chooser (`.bat`, `.sh`, or any file filter). The selected path SHALL populate the Logic text field.

#### Scenario: Browse for script file
- **WHEN** the user is editing a custom Action-type action
- **WHEN** the user clicks "Browse" next to the Logic field
- **THEN** a file chooser dialog opens filtered to `.bat`, `.sh`
- **WHEN** the user selects a file
- **THEN** the file path appears in the Logic field
