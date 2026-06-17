## Why

The buildozer.spec path field currently requires manual typing — error-prone and slow. Users already browse for the source directory via a FileChooser; the same convenience should exist for the spec file. Additionally, when a user picks a source directory that contains `buildozer.spec`, the app should proactively offer to use it rather than silently auto-filling.

## What Changes

- Add a "Browse" button next to the `buildozer.spec path` field that opens a file chooser limited to `buildozer.spec` files
- Extract the FileChooser logic into a reusable helper to avoid duplication (currently embedded in `_browse_sourcedir`)
- When the Source Directory FileChooser confirms a path that contains `buildozer.spec`, show a confirmation popup offering to populate the spec path; on "Yes" set it, on "No" dismiss
- Remove the silent auto-detect behavior from the Source Directory FileChooser (replaced by the explicit popup)

## Capabilities

### New Capabilities
- *(none — existing profile-management capability is modified)*

### Modified Capabilities
- `profile-management`: Modify "Browse for source directory" scenario (replace silent auto-detect with confirmation popup), add new "Browse for buildozer.spec" scenario

## Impact

- `src/screens/profile_editor_screen.py`: Refactor `_browse_sourcedir` into a reusable file chooser helper; add `_browse_spec_path`; add confirmation popup logic
- `src/kv/profile_editor_screen.kv`: Add Browse button next to the `spec_path_input` text field
- Potentially new file: `src/screens/file_chooser_helper.py` for shared FileChooser logic
