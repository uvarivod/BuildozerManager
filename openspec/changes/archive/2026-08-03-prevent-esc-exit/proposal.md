## Why

Pressing the Escape key while no dialog is open immediately closes the entire application, causing accidental data loss when a user reflexively hits Esc (e.g., after dismissing a dialog). The application should never exit via the Escape key; users should exit only through an explicit close action.

## What Changes

- Disable Kivy's built-in `exit_on_escape` behavior in `main.py` (set before the window is created) so the window is never closed by the Escape key.
- Preserve the existing Escape-to-dismiss behavior for open dialogs (unchanged dialog helper keyboard handling).
- Exit remains possible via the window close button and programmatic `App.stop()`.
- Add tests verifying the Kivy config is applied before window creation and that dialog Escape-dismiss still works.

## Capabilities

### New Capabilities
- `escape-key-behavior`: The application SHALL NOT close when the user presses the Escape key. Open dialogs SHALL still dismiss on Escape, and an explicit user confirmation SHALL be required to exit the application via keyboard.

### Modified Capabilities
- `dialog-system`: The existing "Escape key dismisses dialog" requirement remains valid, but the scope note SHALL be updated to clarify that Escape dismisses the dialog without exiting the application.

## Impact

- `main.py`: Kivy `Config.set('kivy', 'exit_on_escape', '0')` added before window creation (config must be set before `kivy.core.window` is imported).
- `src/app.py`: `BuildozerManagerApp` binds a window key handler and an `on_request_close` handler.
- `src/screens/dialog_helper.py`: No behavioral change; existing Escape-dismiss is kept and compatible.
- `tests/`: New test module for escape-key behavior (app-level close prevention and dialog coexistence).
- No new runtime dependencies.
