## Context

Source Directory already has a FileChooser implemented inline in `_browse_sourcedir()`. The buildozer.spec path field requires manual entry. After selecting a source directory, auto-detect currently silently fills the spec path — the user wants an explicit confirmation popup instead.

## Goals / Non-Goals

**Goals:**
- Add Browse button for buildozer.spec path (file chooser filtered to `buildozer.spec`)
- Show confirmation popup when source dir contains `buildozer.spec` after Browse
- Extract shared FileChooser logic into a reusable helper

**Non-Goals:**
- Not changing the ADB path field behavior
- Not adding multi-file selection
- Not changing the toggle view behavior (Icon/List persist as-is)

## Decisions

1. **Extract `FileChooserHelper` class** — The `_browse_sourcedir` method has grown large. Extract it into `src/screens/file_chooser_helper.py` with a static/show method that accepts a callback, initial path, file filter, and title. This avoids duplicating the 100+ lines of popup/view/toggle/choose logic for the second Browse button.

2. **Confirmation popup** — A simple `Popup` with a `Label` and two buttons (Yes/No), triggered inside `_browse_sourcedir` after the user clicks "Choose". The popup checks `Path(chosen_path / "buildozer.spec").exists()`. On Yes, it assigns to `spec_path_input.text`. On No, it does nothing.

3. **Silent auto-detect removed** — The existing `Auto-detect buildozer.spec` scenario (silent auto-populate on sourcedir change) is removed from specs. The confirmation popup replaces it.

## Risks / Trade-offs

- [No confirmation on manual input] → The popup only fires through the FileChooser. Users who manually type a path are not prompted. This is acceptable since they chose to type manually.
- [Helper refactor risk] → Existing `_browse_sourcedir` is well-tested. The refactor keeps the same logic, just inside a helper. No functional change for source dir browsing (except the popup addition).
