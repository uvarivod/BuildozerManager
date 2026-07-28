## Why

The application contains 20+ dialog popups built ad-hoc across 5 screen files with no shared dialog system. This leads to duplicated boilerplate code, inconsistent sizing/styling, missing dismiss buttons on some popups, and no keyboard support. Users encounter popups that cannot be closed (no OK button), inconsistent confirmation flows, and no Escape/Enter key handling. A centralized dialog system will reduce code duplication, enforce consistency, and improve usability.

## What Changes

- Create a reusable dialog helper module with factory functions for common dialog patterns (info, confirm, error, success, form)
- Add centralized dialog styling (colors, fonts, spacing, sizes) following the existing dark theme conventions
- Add keyboard support (Escape to dismiss, Enter to confirm) to all dialogs
- Add toast/snackbar component for transient notifications (replacing full popup for success messages)
- Fix missing dismiss buttons on profile editor error/ADB popups
- Standardize popup sizes across all screens
- Set `auto_dismiss=False` on all confirmation dialogs to prevent accidental dismissal

## Capabilities

### New Capabilities

- `dialog-system`: Centralized dialog helper module providing reusable factory functions for info, confirm, error, success, and form dialogs with consistent styling, keyboard support, and the dark theme

### Modified Capabilities

- `help-popups`: Will use the new dialog system instead of raw Popup construction
- `action-edit-dialog`: Will use the new dialog system for the action edit/create/delete confirmation dialogs
- `scenario-editor-ui`: Will use the new dialog system for all scenario-related dialogs (unsaved changes, delete confirmation, duplicate name errors, etc.)

## Impact

- **Files to create**: `src/screens/dialog_helper.py` (new centralized dialog module), `src/kv/dialog_helper.kv` (optional KV styling)
- **Files to modify**: `src/screens/actions_screen.py`, `src/screens/profile_editor_screen.py`, `src/screens/scenario_editor_screen.py`, `src/screens/settings_screen.py`, `src/screens/log_panel.py`, `src/screens/help_popup.py`
- **Dependencies**: No new dependencies; uses existing Kivy Popup, BoxLayout, Button, Label widgets
