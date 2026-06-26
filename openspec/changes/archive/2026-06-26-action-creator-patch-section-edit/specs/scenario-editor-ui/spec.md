## MODIFIED Requirements

### Requirement: Scenario Editor has three-panel layout
The system SHALL provide a Scenario Editor screen with three visual panels: a scenario list panel on the left, an action sequence editor in the center, and an available actions palette on the right.

**MODIFIED**: The right panel SHALL contain two labeled sections ("Available Actions" and "Available Patches") instead of a single list.

#### Scenario: Three panels displayed with section split
- **WHEN** the user opens the Scenario Editor
- **THEN** they see a scenario list panel (left), an action sequence editor (center), and an actions palette (right)
- **THEN** the palette shows "Available Actions" and "Available Patches" headers
- **THEN** each panel is separated by a visible divider

### Requirement: Action palette shows available actions
The right panel SHALL display all Action enum values as draggable chips. Actions already in the sequence SHALL still appear in the palette (adding a duplicate is allowed, matching the "Full Clean build" pattern with two BUILD steps).

**MODIFIED**: The palette SHALL additionally load custom actions from `CustomActionStore`. Action-type custom actions SHALL appear in "Available Actions" as draggable chips. Patch-type custom actions SHALL appear in "Available Patches" as non-draggable chips.

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
**ADDED**: Clicking any palette chip (built-in or custom) SHALL open an edit dialog showing the action's properties. The dialog SHALL be read-only for built-in actions and editable for custom actions.

#### Scenario: Click to edit
- **WHEN** the user clicks a palette chip
- **THEN** a popup opens displaying the action's Name, Description, Type, and Logic
