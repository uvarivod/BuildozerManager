## Why

Opening the file chooser crashes with `NameError: name 'dp' is not defined` because the `dp()` function from `kivy.metrics` is used directly in `file_chooser_helper.py` without a proper import. This is a regression from the SP/DP unit migration.

## What Changes

- Add a `from kivy.metrics import dp` import at the top of `file_chooser_helper.py`
- Ensure all pixel-based values in the file use the `dp()` function consistently

## Capabilities

### New Capabilities

*(None — this is a bug fix, not a new capability.)*

### Modified Capabilities

- `sp-unit-migration`: The file chooser helper was missed during the SP/DP unit migration. The missing `dp` import must be added to complete the migration for this file.

## Impact

- **File**: `src/screens/file_chooser_helper.py` — add one import line
- **Risk**: Minimal; pure addition of a missing import with no behavioral change
