## Why

The current profile editor has WSL fields scattered without visual grouping, the ADB path lacks a file chooser or validation, and field names are unclear about their purpose. This makes profile configuration confusing and error-prone — users can't visually distinguish WSL-specific settings, have no way to pick ADB/wsl paths visually, and have no way to verify ADB connectivity from the editor.

## What Changes

### WSL Section Grouping
- Group all WSL-related fields under a visually distinct "WSL Configuration" section in the profile editor
- Move `wsl_dir`, `wsl_distro`, and `delete_exclusions` into this section

### Field Renaming
- `WSL directory` → `WSL Build Directory`: clearer that this is the project's working directory *on* WSL  
- `WSL distro` → `WSL Distribution`: accurately reflects this is the distribution *name* (passed as `wsl.exe --distribution <name>`), not a distributive package
- `Delete exclusions (comma-sep)` → `Retain During Sync`: describes files/folders to preserve in the WSL build directory when deleting old source before copying new source

### ADB Path Enhancement
- Add a **Browse** button next to the ADB path field, opening a file chooser (filtered to `adb.exe`) — identical pattern to the buildozer.spec file chooser
- Add a **Check** button next to the ADB path field that opens a popup showing the result of `adb devices` to verify ADB works

### WSL Build Directory Folder Chooser
- Add a **Browse** button next to the WSL Build Directory field, opening a directory chooser — identical pattern to the Source Directory folder chooser
- If the field is empty and user opens the chooser, default to `\\wsl.localhost\<WSL Distribution>` (e.g., `\\wsl.localhost\Ubuntu-22.04`) using the current WSL Distribution field value

## Capabilities

### New Capabilities
- `adb-path-validation`: Browse for `adb.exe` via file chooser and verify ADB connectivity inline

### Modified Capabilities
- `profile-management`: WSL fields are visually grouped under a "WSL Configuration" section; field labels are renamed for clarity; WSL Build Directory gets a folder chooser with smart defaults
- `wsl-integration`: WSL field labels updated in the UI to match new naming (no spec-level behavior changes)
- `adb-integration`: ADB path field gains a Browse button (file chooser) and a Check button (inline validation popup)

## Impact

- **`src/kv/profile_editor_screen.kv`**: restructured layout with WSL section group; new Browse/Check buttons for ADB path; new Browse button for WSL Build Directory
- **`src/screens/profile_editor_screen.py`**: new methods `_browse_adb_path()`, `_check_adb()`, `_browse_wsl_dir()`; field references updated to new names
- **No model changes**: `Profile` dataclass field names stay the same (`wsl_dir`, `wsl_distro`, `delete_exclusions`); only UI labels change
- **No service changes**: WSL service and ADB service remain unchanged
