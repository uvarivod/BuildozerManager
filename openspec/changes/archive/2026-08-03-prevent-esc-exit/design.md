## Context

BuildozerManager is a Kivy 2.3.1 desktop application (Windows). Kivy's SDL2 window provider enables the built-in `exit_on_escape` behavior by default: pressing the Escape key requests the window to close, terminating the app immediately. This is surprising and destructive because users frequently press Esc to dismiss dialogs. The app's dialog helper (`src/screens/dialog_helper.py`) already handles Escape as "dismiss current dialog" (key code 27) by binding `Window.on_key_down`, but when no dialog is open the same keypress closes the whole application.

The application entry point is `main.py`, which already performs Kivy config setup (`Config.set`) at the very top, before any window/screen modules are imported. `kivy.config.Config` reads `exit_on_escape` once at window-import time, so the value must be set before `kivy.core.window` is imported anywhere.

## Goals / Non-Goals

**Goals:**
- The application never terminates when the user presses the Escape key.
- Open dialogs still dismiss on Escape (existing behavior preserved).
- Exiting remains possible via the window close button (X) and programmatic stop.
- Behavior is covered by automated tests consistent with the existing mock-Kivy test approach.

**Non-Goals:**
- Adding an in-app "Quit" button or menu (not requested; window close already works).
- Showing an "Are you sure you want to exit?" confirmation on Escape (out of scope; Esc should simply do nothing).
- Changing Android/back-button behavior beyond what `exit_on_escape` already controls.

## Decisions

### Decision 1: Disable exit on escape via Kivy Config
Set `Config.set('kivy', 'exit_on_escape', '0')` in `main.py`, in the existing config block (after the current `Config.set` calls for `keyboard_mode` and `input`, before `src.app` is imported).

- **Why**: This is the documented, provider-level mechanism. It is read once at import time, and `main.py` configures Kivy before any window is created, so it is guaranteed to take effect.
- **Alternative considered**: Binding `Window.on_key_down` and returning `True` for key 27. Rejected because handler ordering conflicts with the dialog helper's Escape-dismiss: an app-level handler that consumes Escape would block the per-dialog handler (or require a fragile global "is a dialog open" registry) and could break the existing dialog-system requirement.
- **Alternative considered**: Binding `Window.on_request_close` and returning `True` when `source == 'keyboard'`. Rejected as unnecessary — with `exit_on_escape` disabled, the window never receives a keyboard-initiated close request, so the handler would be dead code. Noted as a future safeguard if a provider ignores the config.

### Decision 2: No change to dialog keyboard handling
`src/screens/dialog_helper.py` keeps its existing Escape-dismiss (key 27) logic unchanged. Because exit-on-escape is disabled at the window level, Esc dismisses the open dialog and nothing else happens.

- **Why**: Minimal change, no coordination needed between app-level and dialog-level key handlers.

### Decision 3: Test via config assertion, not a live window
Since Kivy cannot run under the test environment, verify behavior by extending the mock Kivy tree in `tests/conftest.py` with `kivy.config.Config` (a `MagicMock`) and adding `tests/test_main.py` that imports `main.py` and asserts `Config.set` was called with `('kivy', 'exit_on_escape', '0')` before the app module is imported.

- **Why**: Consistent with the existing mock-based test strategy. Importing `main.py` exercises the real startup ordering.

## Risks / Trade-offs

- [Config is read once at import time (kivy issue #1634), so ordering is critical] → Mitigation: the `Config.set` call lives at the top of `main.py` before any `kivy.core.window` import; the new test asserts it is invoked during module import.
- [Some window providers may not honor `exit_on_escape`] → Mitigation: SDL2 (the only desktop provider used here) honors it; if a future provider regresses, add an `on_request_close` handler that ignores keyboard-sourced close requests.
- [Users who rely on Esc-to-quit lose that shortcut] → Mitigation: intentional per the requirement; the window close button (X) and `App.stop()` remain functional.
