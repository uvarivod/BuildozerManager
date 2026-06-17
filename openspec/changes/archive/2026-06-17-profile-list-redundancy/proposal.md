## Why

The profile list and editor are currently split across two separate screens with redundant navigation. A dedicated list screen adds no value — selecting a profile is a simple one-choice action that belongs in a dropdown, not a full screen with navigation.

## What Changes

- Remove `ProfileListScreen` and `ProfileEditorScreen` entirely
- Create a single `ProfilesScreen` with a profile **Spinner** (dropdown) at the top and the editor form below
- Selecting a profile from the dropdown loads its settings into the form
- Auto-save when switching profiles
- "New Profile" and "Delete" buttons in the form area
- **BREAKING**: Two old screens replaced by one; nav bar drops from 4 to 3 buttons

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `profile-management`: Profile list is replaced by a dropdown selector. The editor form is the main content of the screen.

## Impact

- Delete `screens/profile_list_screen.py`, `screens/profile_editor_screen.py`, and their KV files
- Create `screens/profiles_screen.py` + `kv/profiles_screen.kv` with Spinner + form
- Update `app.py` to register the merged screen
- Update `kv/main.kv` to remove "Editor" nav button
