## Context

The profile editor (`profile_editor_screen.py` + `profile_editor_screen.kv`) currently displays WSL fields as flat rows mixed with non-WSL fields, and the ADB path is a plain TextInput with no browser or validation. This design describes the UI/UX changes to improve profile configuration without altering the data model or backend services.

## Goals / Non-Goals

**Goals:**
- Visually group WSL fields under a "WSL Configuration" section
- Rename field labels for clarity (WSL Build Directory, WSL Distribution, Retain During Sync)
- Add file/folder chooser (Browse) to ADB path and WSL Build Directory
- Add ADB connectivity check button with result popup
- Smart default for WSL Build Directory chooser based on WSL Distribution value

**Non-Goals:**
- No changes to the `Profile` dataclass or JSON persistence schema
- No changes to `wsl_service.py` or `adb_service.py` business logic
- No changes to the WSL integration spec (labels only)
- No ADB auto-detection enhancement (existing auto-detect on PATH remains as-is)

## Decisions

### 1. WSL Section — Use a Full-Width Header Label Spanning Both GridColumns
- **Decision**: Insert a `Label` with `text: 'WSL Configuration'` styled with bold text and a colored background, spanning both columns (`cols: 2` grid). The label will use `size_hint_x: 1` and `canvas.before.Color` + `Rectangle` for visual separation.
- **Rationale**: Simplest approach within the existing `GridLayout(cols:2)` structure. No nested layouts needed. Matches Kivy patterns already used elsewhere.
- **Alternative considered**: Wrapping WSL fields in a nested `BoxLayout` — would break the 2-column grid alignment consistency.

### 2. ADB Check — Run `adb version` via Subprocess
- **Decision**: The Check button calls a new `_check_adb()` method that executes `subprocess.run([adb_path, "version"])` with the current ADB path, then shows a popup with the version string on success or an error message on failure.
- **Rationale**: `adb version` only checks the executable exists and runs, without requiring a connected Android device. Simpler and faster than `adb devices -l`.

### 3. ADB Path Browse — File Chooser Filtered to `adb.exe`
- **Decision**: Use `FileChooserHelper.show_file_chooser()` with `target_filename="adb.exe"`, identical pattern to `_browse_spec_path()`.
- **Rationale**: Reuses existing `FileChooserHelper` with zero new UI code.

### 4. WSL Build Directory Browse — Directory Chooser with Smart Default
- **Decision**: Use `FileChooserHelper.show_dir_chooser()`. If the field is empty, compute initial path as `\\wsl.localhost\<WSL Distribution>` using the current value from `wsl_distro_input.text`.
- **Rationale**: The user explicitly requested this default path behavior. Resolves correctly even if the WSL distro name has been changed.

### 5. Field Renames — KV Labels Only, No Python Changes
- **Decision**: Change only `text:` attributes in the KV file. Keep Python property names (`adb_path_input`, `wsl_dir_input`, `wsl_distro_input`, `delete_exclusions_input`) unchanged.
- **Rationale**: The `Profile` dataclass and `_build_profile()` method reference these widget IDs, not labels. No code changes needed for renaming.

## Risks / Trade-offs

- **WSL section header breaks 2-column alignment**: The header spans full width via `canvas.before`. If the grid layout resizes, the header background may not stretch correctly. Mitigation: Test with various window sizes and set `canvas.before` dimensions to match the label size.
- **ADB Check button introduces transient popup UI**: If ADB hangs, the popup may show stale/delayed results. Mitigation: Use a 10-second timeout on the version check subprocess call.
- **`\\wsl.localhost\...` default path may not exist**: If the user enters a non-existent WSL distro name, the directory won't exist. This is acceptable — the chooser will show an empty/nonexistent path, and the user can navigate manually.
