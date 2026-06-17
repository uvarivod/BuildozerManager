## Context

The profile editor screen displays a Source Directory text input where users type the path manually. Kivy provides `FileChooserIconView` and `FileChooserListView` built-in widgets that can be opened as a popup/dialog for directory selection. The current auto-detect feature scans for `buildozer.spec` when sourcedir changes, which must remain functional.

## Goals / Non-Goals

**Goals:**
- Add a Browse button next to Source Directory that opens a directory picker
- Selected path populates the text input
- Manual typing and copy-paste continue working
- Auto-detect buildozer.spec still fires on text change

**Non-Goals:**
- Not adding FileChooser to other path fields (spec_path, adb_path, wsl_dir)
- No storage or model changes
- No custom file browser styling

## Decisions

1. **FileChooser as Popup** — Use `FileChooserIconView` wrapped in a Kivy `Popup` with `dirselect=True`. This is the simplest approach, no external dependency needed.
2. **Pre-populate with current value** — Set `FileChooser.path` to the current text input value (if non-empty and valid) so the dialog opens at the user's current directory.
3. **Button in the same GridLayout cell** — The Source Directory row gets a horizontal BoxLayout containing the TextInput and a small "Browse" button, replacing the standalone TextInput.

## Risks / Trade-offs

- [FileChooser on Windows may show short paths (8.3)] → Mitigation: The text input stores the selected full path as returned by Kivy, which is the long path.
- [Auto-detect could fire while dialog is open] → Not a concern: auto-detect triggers on text change, which only happens after selection is applied.
