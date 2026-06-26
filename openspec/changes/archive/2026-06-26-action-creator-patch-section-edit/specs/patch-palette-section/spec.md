## ADDED Requirements

### Requirement: Palette has two labeled sections
The right panel of the Scenario Editor SHALL display two sections with headers:
- "Available Actions" — containing built-in Action enum members + custom Action-type actions
- "Available Patches" — containing custom Patch-type actions and references to built-in PatchRegistry entries

Each section SHALL have a bold header label and be visually separated.

#### Scenario: Sections visible
- **WHEN** the user opens the Scenario Editor
- **THEN** they see "Available Actions" header followed by action chips
- **THEN** they see "Available Patches" header followed by patch chips below

### Requirement: Patch-type chips are not draggable
Patch-type action chips in the "Available Patches" section SHALL NOT be draggable to the sequence editor. They exist as visual reference for available patches. Only Action-type chips (built-in or custom) SHALL support drag-and-drop to the sequence.

#### Scenario: Patch chip not draggable
- **WHEN** the user attempts to drag a patch chip from "Available Patches"
- **THEN** the chip does not respond to drag gestures
- **THEN** the chip only responds to click (opens edit dialog)
