## Why

Users need to define custom actions beyond the 6 built-in buildozer steps (sync, clean, build, patch, pull_apk, run). Common use cases include running arbitrary batch scripts before/after builds, applying custom file operations, or integrating external tools. The current fixed Action enum makes this impossible, forcing users to manually run steps outside the app.

## What Changes

1. **Action Creator** — Add a "New Action" button in the scenario editor palette. Clicking it opens a dialog to define a custom action with fields: Name, Description, Type (Action / Patch), and Logic (file path for .bat/.sh, or built-in name for built-in actions). User-created actions have a Delete button; built-in actions cannot be modified or deleted.

2. **Patch Section** — Split the palette into two labeled sections: "Available Actions" (built-in + custom Action-type) and "Available Patches" (built-in + custom Patch-type). Patch-type actions remain selectable in scenario sequences via the PATCH action — they are NOT draggable independently to the edit pane.

3. **Edit Action Dialog** — Clicking any action chip in the palette opens an edit popup where the user can modify the action's properties (except for built-in actions which are read-only). Drag-and-drop from palette to edit pane works as before (for both Action and Patch-type chips that can be added to a scenario).

## Capabilities

### New Capabilities
- `action-creator`: UI and model for creating, editing, and deleting custom actions with Name, Description, Type (Action/Patch), and Logic fields
- `patch-palette-section`: Split palette in scenario editor showing "Available Actions" and "Available Patches" sections
- `action-edit-dialog`: Popup dialog for viewing/editing action properties triggered by clicking a palette chip

### Modified Capabilities
- `scenario-editor-ui`: Update the palette section to support dual sections (actions + patches), click-to-edit interaction, and custom action chips alongside built-in Action enum entries

## Impact

- **src/models/action.py**: Replace Action enum with a flexible model that supports both built-in and user-defined actions. Built-in actions remain as enum-like constants.
- **src/screens/scenario_editor_screen.py**: Add "New Action" button, edit dialog, palette section split, custom action persistence integration.
- **src/screens/action_card.py** / **actions_screen.py**: Update action card rendering to handle custom action types and patch-type metadata.
- **src/services/storage_service.py**: Add CustomActionStore for persisting user-defined actions (JSON).
- **New file**: `src/models/custom_action.py` for the custom action data model.
- All UI changes are pure Kivy (KV + Python), no new dependencies.
