# Action Creator

## Purpose

TBD

## Requirements

### Requirement: Custom action model with Name, Description, Type, Logic
Users SHALL be able to create custom actions. Each custom action SHALL have the following fields:
- `name`: A unique string identifier (1-50 characters, alphanumeric with spaces)
- `description`: A short description of what the action does
- `type`: Either `Action` or `Patch` — determines which palette section the action appears in
- `logic`: For `Action`-type, a file path to a `.bat` (Windows) or `.sh` (WSL) script. For `Patch`-type, a reference to a built-in PatchRegistry entry.

#### Scenario: Create custom Action-type action
- **WHEN** the user clicks "New Action" in the palette
- **THEN** a dialog opens with fields: Name, Description, Type (dropdown: Action/Patch), Logic (file chooser for Action, text input for Patch)
- **WHEN** the user fills in Name="Deploy to Play Store", Description="Upload APK to Google Play", Type="Action", Logic="C:\scripts\deploy.bat"
- **WHEN** the user clicks "Save"
- **THEN** the new action is persisted
- **THEN** it appears in the "Available Actions" section of the palette

#### Scenario: Create custom Patch-type action
- **WHEN** the user fills in Name="Custom Theme Patch", Type="Patch", Logic="patch_activity_theme"
- **WHEN** the user clicks "Save"
- **THEN** the action appears in the "Available Patches" section of the palette

### Requirement: Custom actions persist via CustomActionStore
Custom actions SHALL be persisted to `data/custom_actions.json` using a `CustomActionStore` class. On app startup, all custom actions SHALL be loaded and available in the palette.

#### Scenario: Persistence across restart
- **WHEN** the user creates a custom action "Deploy to Play Store"
- **WHEN** the user closes and reopens the app
- **THEN** "Deploy to Play Store" appears in the palette

### Requirement: Custom actions can be deleted
User-created custom actions SHALL have a "Delete" button in their edit dialog. Deleting a custom action SHALL remove it from storage and from the palette immediately.

#### Scenario: Delete custom action
- **WHEN** the user opens the edit dialog for a custom action
- **WHEN** the user clicks "Delete"
- **WHEN** the user confirms deletion
- **THEN** the action is removed from storage
- **THEN** it disappears from the palette

### Requirement: Built-in actions cannot be deleted or modified
The 6 built-in Action enum values (SYNC_SRC, CLEAN, BUILD, PATCH, PULL_APK, RUN) SHALL NOT have a delete button. Their edit dialog SHALL show all fields as read-only.

#### Scenario: Built-in action read-only
- **WHEN** the user clicks a built-in action chip (e.g., BUILD)
- **THEN** the edit dialog displays Name, Description, Type, Logic as read-only
- **THEN** no Delete button is shown

### Requirement: New Action button in palette header
A "New Action" button SHALL be displayed above the palette sections. Clicking it SHALL open the Create Action dialog.

#### Scenario: New Action button visible
- **WHEN** the user opens the Scenario Editor
- **THEN** a "New Action" button is visible above the palette
