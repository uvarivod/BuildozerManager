## 1. Disable Exit-on-Escape

- [x] 1.1 Add `Config.set('kivy', 'exit_on_escape', '0')` to `main.py` in the existing config block, placed after the current `keyboard_mode`/`input` settings and before `src.app` is imported
- [x] 1.2 Confirm the config line executes before any `kivy.core.window` import in the startup sequence

## 2. Test Infrastructure

- [x] 2.1 Add a `kivy.config.Config` mock (MagicMock) to the Kivy mock tree in `tests/conftest.py` and register `kivy.config` in `sys.modules` in `_install_kivy()`
- [x] 2.2 Create `tests/test_main.py` that imports `main.py` and asserts `Config.set` was called with `('kivy', 'exit_on_escape', '0')`

## 3. Behavior Verification Tests

- [x] 3.1 Add a test (in `tests/test_dialog_helper.py`) verifying that pressing Escape (key 27) on an open dialog dismisses it without closing the application
- [x] 3.2 Add a test verifying the Escape key does not trigger any window close request when no dialog is open

## 4. Verification

- [x] 4.1 Run the full test suite (`python -m pytest`) and confirm all tests pass
- [ ] 4.2 Manually verify: launch the app, press Esc (app stays open), open a dialog and press Esc (dialog closes, app stays), close via window X
