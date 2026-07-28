## MODIFIED Requirements

### Requirement: Back button returns to Actions screen
A "Back" button SHALL navigate to the Actions screen without losing unsaved changes. If unsaved changes exist, the system SHALL prompt the user to save or discard using `show_confirm_dialog()` from the dialog helper module.

#### Scenario: Back with unsaved changes
- **WHEN** the user has unsaved changes
- **WHEN** the user clicks "Back"
- **THEN** a popup asks "Save changes before leaving?"
- **THEN** options: "Save and Leave", "Discard and Leave", "Cancel"
- **THEN** the popup uses consistent dark theme styling from the dialog helper module

### Requirement: Delete removes a user scenario
A "Delete" button SHALL remove the currently selected user scenario after confirmation. Predefined scenarios SHALL NOT have a delete button. The confirmation SHALL use `show_confirm_dialog()` from the dialog helper module.

#### Scenario: Delete user scenario
- **WHEN** the user is editing a user scenario
- **WHEN** the user clicks "Delete"
- **WHEN** the user confirms in the confirmation dialog
- **THEN** the scenario is removed from storage
- **THEN** the editor clears
- **THEN** the scenario list refreshes without the deleted scenario
- **THEN** the popup uses consistent dark theme styling from the dialog helper module

## ADDED Requirements

### Requirement: Duplicate scenario name shows error dialog
When saving a scenario with a name that already exists, the system SHALL display an error dialog using `show_error_dialog()` from the dialog helper module.

#### Scenario: Duplicate scenario name error
- **WHEN** the user tries to save a scenario with name "My Build"
- **WHEN** a scenario named "My Build" already exists
- **THEN** an error dialog appears with message "A scenario named 'My Build' already exists."
- **THEN** the popup uses consistent dark theme styling from the dialog helper module

### Requirement: Missing actions warning shows error dialog
When a scenario references actions that no longer exist, the system SHALL display an error dialog using `show_error_dialog()` from the dialog helper module.

#### Scenario: Missing actions warning on save
- **WHEN** the user tries to save a scenario
- **WHEN** the scenario references missing actions
- **THEN** an error dialog appears with message "Cannot save. Scenario references missing actions."
- **THEN** the popup uses consistent dark theme styling from the dialog helper module

### Requirement: Action in use warning shows error dialog
When trying to delete a custom action that is used in a scenario, the system SHALL display an error dialog using `show_error_dialog()` from the dialog helper module.

#### Scenario: Action in use warning
- **WHEN** the user tries to delete a custom action
- **WHEN** the action is used in one or more scenarios
- **THEN** an error dialog appears with message "Cannot delete 'X'. It is used in: ..."
- **THEN** the popup uses consistent dark theme styling from the dialog helper module

### Requirement: Duplicate custom action name shows error dialog
When creating or editing a custom action with a name that already exists, the system SHALL display an error dialog using `show_error_dialog()` from the dialog helper module.

#### Scenario: Duplicate custom action name error
- **WHEN** the user tries to create or edit a custom action
- **WHEN** an action with the same name already exists
- **THEN** an error dialog appears with message "An action named 'X' already exists."
- **THEN** the popup uses consistent dark theme styling from the dialog helper module

### Requirement: Unsaved changes warning on scenario switch
When switching to a different scenario with unsaved changes, the system SHALL prompt the user using `show_confirm_dialog()` from the dialog helper module.

#### Scenario: Switch scenario with unsaved changes
- **WHEN** the user has unsaved changes in the current scenario
- **WHEN** the user clicks a different scenario in the list
- **THEN** a confirm dialog appears asking "Save changes before switching?"
- **THEN** options: "Save", "Discard", "Cancel"
- **THEN** the popup uses consistent dark theme styling from the dialog helper module
