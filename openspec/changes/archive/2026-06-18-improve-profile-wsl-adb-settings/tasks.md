## 1. KV Layout — Restructure Profile Editor Form

- [x] 1.1 Add "WSL Configuration" full-width section header label above WSL fields, with colored background
- [x] 1.2 Move `delete_exclusions_input` row into the WSL section (below WSL Distribution)
- [x] 1.3 Add Browse button next to ADB path field (same pattern as sourcedir/spec_path)
- [x] 1.4 Add Check button next to ADB path Browse button
- [x] 1.5 Add Browse button next to WSL Build Directory field (same pattern as sourcedir)
- [x] 1.6 Update field labels: "WSL directory" → "WSL Build Directory", "WSL distro" → "WSL Distribution", "Delete exclusions (comma-sep)" → "Retain During Sync"

## 2. Screen Methods — Add Browse & Check Handlers

- [x] 2.1 Add `_browse_adb_path()` method using FileChooserHelper (file chooser, filtered to `adb.exe`)
- [x] 2.2 Add `_check_adb()` method that runs `subprocess.run([adb_path, "version"], timeout=10)` and shows result popup
- [x] 2.3 Add `_browse_wsl_dir()` method using FileChooserHelper (directory chooser, default to `\\wsl.localhost\<distro>` if empty)
- [x] 2.4 Wire new KV button `on_release` events to the new screen methods

## 3. Verify

- [ ] 3.1 Run the app and verify all fields render correctly with new labels and section header
- [ ] 3.2 Test ADB Browse selects `adb.exe` and fills the field
- [ ] 3.3 Test ADB Check with valid and invalid paths
- [ ] 3.4 Test WSL Build Directory Browse opens chooser with correct default path
- [ ] 3.5 Save a profile and verify all new/existing fields persist correctly
