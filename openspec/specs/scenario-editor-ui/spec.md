# Scenario Editor UI

## Purpose

TBD

## Requirements

### Requirement: Scenario Editor has three-panel layout
The system SHALL provide a Scenario Editor screen with three visual panels: a scenario list panel on the left, an action sequence editor in the center, and an available actions palette on the right. The right panel SHALL contain two labeled sections ("Available Actions" and "Available Patches") instead of a single list.

#### Scenario: Three panels displayed with section split
- **WHEN** the user opens the Scenario Editor
- **THEN** they see a scenario list panel (left), an action sequence editor (center), and an actions palette (right)
- **THEN** the palette shows "Available Actions" and "Available Patches" headers
- **THEN** the palette sections have bold headers but no visible divider between panels

### Requirement: Scenario list panel shows all scenarios
The left panel SHALL list all scenarios (predefined and user-defined). Predefined scenarios SHALL show a `[R]` prefix and be visually distinct (dimmer background color). User scenarios SHALL show a delete button on hover/select.

#### Scenario: Scenario list with predefined and user scenarios
- **WHEN** the user opens the Scenario Editor
- **THEN** the left panel shows all scenarios by name
- **THEN** predefined scenarios display a `[R]` prefix and have a dimmer background
- **THEN** user scenarios show a delete (X) button when selected

### Requirement: Selecting a scenario loads it for editing
Clicking a scenario in the list SHALL load its name, description, and action sequence into the editor panels. Predefined scenarios SHALL display in read-only mode (no drag, no add/remove/delete, no reorder).

#### Scenario: Select user-defined scenario
- **WHEN** the user clicks a user-defined scenario in the list
- **THEN** the center panel displays its action sequence with "->" separators
- **THEN** the right panel shows available actions not yet in the sequence
- **THEN** the name and description fields are editable

#### Scenario: Select predefined scenario
- **WHEN** the user clicks a predefined scenario in the list
- **THEN** the sequence is displayed but all controls are disabled
- **THEN** the name and description fields are read-only
- **THEN** the delete button is hidden

### Requirement: Action palette shows available actions
The right panel SHALL display all Action enum values as draggable chips. Actions already in the sequence SHALL still appear in the palette (adding a duplicate is allowed, matching the "Full Clean build" pattern with two BUILD steps). The palette SHALL additionally load custom actions from `CustomActionStore`. Action-type custom actions SHALL appear in "Available Actions" as draggable chips. Patch-type custom actions SHALL appear in "Available Patches" as non-draggable chips.

#### Scenario: Actions shown in palette
- **WHEN** the user opens the Scenario Editor
- **THEN** the right panel shows chips for all Action values: SYNC_SRC, CLEAN, BUILD, PATCH, PULL_APK, RUN
- **THEN** each chip shows the action name and description

#### Scenario: Custom action chip in palette
- **WHEN** the user has created a custom action named "Deploy to Play Store" with type Action
- **WHEN** the user opens the Scenario Editor
- **THEN** a "Deploy to Play Store" chip appears in "Available Actions"
- **THEN** the chip supports drag-and-drop to the sequence

#### Scenario: Patch chip in palette (non-draggable)
- **WHEN** the user has created a custom Patch-type action
- **WHEN** the user opens the Scenario Editor
- **THEN** the patch chip appears in "Available Patches"
- **THEN** the chip does NOT respond to drag gestures

### Requirement: Click chip to open edit dialog
Clicking any palette chip (built-in or custom) SHALL open an edit dialog showing the action's properties. The dialog SHALL be read-only for built-in actions and editable for custom actions.

#### Scenario: Click to edit
- **WHEN** the user clicks a palette chip
- **THEN** a popup opens displaying the action's Name, Description, Type, and Logic

### Requirement: Drag-and-drop adds actions to sequence
The user SHALL be able to drag an action chip from the palette and drop it at a specific position in the sequence editor. A ghost button follows the cursor during drag.

#### Scenario: Drag action from palette to sequence
- **WHEN** the user drags a "BUILD" chip from the palette to between positions 2 and 3 in the sequence
- **WHEN** the user releases the drag
- **THEN** a BUILD action is inserted at position 3
- **THEN** the sequence display updates with the new "->" separator

### Requirement: Drag-and-drop reorders actions within sequence
The user SHALL be able to drag an action card within the sequence to a new position. The card SHALL visually lift during drag.

#### Scenario: Reorder action in sequence
- **WHEN** the user drags the action at position 4 to position 1
- **THEN** all actions shift to accommodate the move
- **THEN** the sequence display updates with new order

### Requirement: Actions can be removed from sequence
The user SHALL be able to remove an action from the sequence either by dragging it to a "Trash" drop zone at the bottom of the center panel or by clicking a remove (X) button on each action card.

#### Scenario: Remove action by drag to trash
- **WHEN** the user drags an action card to the Trash zone
- **THEN** the action is removed from the sequence
- **THEN** the sequence display updates

#### Scenario: Remove action by delete button
- **WHEN** the user clicks the X button on an action card
- **THEN** the action is removed from the sequence
- **THEN** the sequence display updates

### Requirement: Undo and Redo for all editing operations
All editing operations (add, remove, reorder, rename, update description) SHALL support undo and redo via toolbar buttons. The undo stack SHALL hold up to 50 operations. The toolbar buttons SHALL disable when no undo/redo actions are available.

#### Scenario: Undo an action addition
- **WHEN** the user adds a BUILD action to the sequence
- **WHEN** the user clicks the Undo toolbar button
- **THEN** the BUILD action is removed (sequence reverts to prior state)

#### Scenario: Redo after undo
- **WHEN** the user undoes an action addition
- **WHEN** the user clicks the Redo toolbar button
- **THEN** the BUILD action is re-added to the sequence

### Requirement: Scenario name and description are editable
The center panel SHALL show editable text fields for scenario name and description. Changes to these fields SHALL be part of the undo/redo stack.

#### Scenario: Edit scenario name
- **WHEN** the user changes the scenario name from "My Build" to "My Custom Build"
- **WHEN** the user clicks Undo
- **THEN** the name reverts to "My Build"

### Requirement: Save persists the scenario
A "Save" button SHALL persist the current scenario (name, description, action sequence) via `ScenarioStore`. After save, the undo stack SHALL be cleared. The scenario list SHALL refresh to reflect the saved state.

#### Scenario: Save new scenario
- **WHEN** the user fills in a name, description, and action sequence
- **WHEN** the user clicks "Save"
- **THEN** the scenario is persisted via ScenarioStore
- **THEN** the scenario list refreshes showing the new entry
- **THEN** the undo stack is cleared

#### Scenario: Save updates existing scenario
- **WHEN** the user modifies a scenario and clicks "Save"
- **THEN** the existing scenario is updated in storage
- **THEN** the scenario list refreshes

### Requirement: Delete removes a user scenario
A "Delete" button SHALL remove the currently selected user scenario after confirmation. Predefined scenarios SHALL NOT have a delete button.

#### Scenario: Delete user scenario
- **WHEN** the user is editing a user scenario
- **WHEN** the user clicks "Delete"
- **WHEN** the user confirms in the confirmation dialog
- **THEN** the scenario is removed from storage
- **THEN** the editor clears
- **THEN** the scenario list refreshes without the deleted scenario

### Requirement: Back button returns to Actions screen
A "Back" button SHALL navigate to the Actions screen without losing unsaved changes. If unsaved changes exist, the system SHALL prompt the user to save or discard.

#### Scenario: Back with unsaved changes
- **WHEN** the user has unsaved changes
- **WHEN** the user clicks "Back"
- **THEN** a popup asks "Save changes before leaving?"
- **THEN** options: "Save and Leave", "Discard and Leave", "Cancel"
