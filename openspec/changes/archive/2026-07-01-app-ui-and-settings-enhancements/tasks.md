## 1. sp Unit Migration

- [x] 1.1 Audit all `.kv` files in `src/kv/` for `font_size` declarations and convert bare integers/`dp` to `sp`
- [x] 1.2 Audit all `.py` files in `src/screens/` and `src/` for `font_size=` keyword arguments and convert to `sp` strings
- [x] 1.3 Audit all `.py` files for dynamic `font_size` assignment (e.g., `widget.font_size = N`) and convert using `sp()` or `"Nsp"`

## 2. Settings Screen

- [x] 2.1 Create `src/screens/settings_screen.py` with `SettingsScreen` class (extends `Screen`)
- [x] 2.2 Create `src/kv/settings_screen.kv` with layout: Log Directory text input, Max Log Size (MB) text input, Save button, Back button
- [x] 2.3 Add `SettingsScreen` to `ScreenManager` in `src/app.py` with name `"settings"`
- [x] 2.4 Add "Settings" button to bottom navigation bar in `src/kv/main.kv`
- [x] 2.5 Wire save logic: read fields, validate, persist via `SettingsStore`
- [x] 2.6 Add `log_dir` and `max_log_size_mb` keys to `SettingsStore.save()` calls with defaults

## 3. Help Popups

- [x] 3.1 Create reusable help popup helper function (takes title and body text, returns `Popup`)
- [x] 3.2 Add help button (?) and popup to Actions screen explaining profile/scenario selection, action chain, run controls, and log panel
- [x] 3.3 Add help button and popup to Profile Editor screen explaining fields and save/delete
- [x] 3.4 Add help button and popup to Scenario Builder screen explaining scenario editing
- [x] 3.5 Add help button and popup to Settings screen explaining settings fields
- [x] 3.6 Add dedicated help popup for log panel explaining SHIFT+click text selection

## 4. Log Directory Integration

- [x] 4.1 Update `LogPanel.__init__` to read `log_dir` from `SettingsStore.load()` for auto-save path
- [x] 4.2 Ensure `logs/` directory creation uses the configured path instead of hardcoded `Path("logs")`
- [x] 4.3 Update "Save Log" dialog default path to use configured log directory

## 5. Log Cleanup Service

- [x] 5.1 Create `src/services/log_cleanup_service.py` with function `cleanup_logs(log_dir: str, max_size_mb: int)`
- [x] 5.2 Implement size calculation: sum file sizes in the log directory
- [x] 5.3 Implement deletion: if size exceeds limit, delete oldest files (by modification time) until under limit
- [x] 5.4 Skip currently-open auto-save file from deletion candidates
- [x] 5.5 Trigger cleanup after each scenario/action completes in `ActionsScreen`
