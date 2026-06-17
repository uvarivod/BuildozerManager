## Why

Manually typing the source directory path is error-prone and inconvenient, especially for Windows paths with spaces or long directory trees. A FileChooser button next to the Source Directory field lets users browse and select the folder visually, while keeping the ability to type or paste paths manually for power users.

## What Changes

- Add a "Browse" button next to the Source Directory text input on the profile editor screen
- Clicking Browse opens a Kivy FileChooser dialog (directory mode) pre-populated with the current text value
- Selecting a directory fills the text input with the chosen path
- Manual typing and copy-paste continue to work as before
- The change is UI-only — no storage or model changes needed

## Capabilities

### New Capabilities

- (none — this is a UI enhancement to existing capability)

### Modified Capabilities

- `profile-management`: Source Directory field gains a Browse button with FileChooser dialog

## Impact

- **src/kv/profile_editor_screen.kv**: Add Browse button in the Source Directory row
- **src/screens/profile_editor_screen.py**: Add `_browse_sourcedir()` method that opens FileChooser and populates the text input
