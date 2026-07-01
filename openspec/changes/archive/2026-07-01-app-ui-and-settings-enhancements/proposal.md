## Why

The app lacks scalable text sizing (uses hardcoded pixel values instead of `sp`), has no inline help for users to understand the interface or the SHIFT+click log selection feature, and provides no way to configure log storage location or automatic log cleanup — leading to uncontrolled log folder growth.

## What Changes

- Convert all font sizes across all KV files and Python code to use `sp` units instead of fixed pixel values for proper DPI scaling
- Add a help popup (question-mark button) to each screen explaining that screen's purpose and controls
- Add a dedicated help popup explaining SHIFT+click text selection in the log panel
- Add a new Settings screen where users can configure:
  - Log directory path
  - Maximum log folder size in MB (auto-cleanup oldest logs when exceeded)
- Add a bottom-nav button to access the Settings screen
- Implement automatic log rotation/cleanup based on the configured size limit

## Capabilities

### New Capabilities
- `help-popups`: Contextual help overlay for each screen explaining purpose and controls, plus a specific popup for log text selection via SHIFT+click
- `settings-page`: New screen for configuring log directory path and maximum log folder size in MB
- `log-cleanup`: Automatic removal of oldest log files when the log directory exceeds the configured size limit
- `sp-unit-migration`: Audit and convert all font size declarations across KV and Python to use `sp` instead of fixed pixel values

### Modified Capabilities
- `log-viewer`: Requirements changed to support configurable log directory path and automatic cleanup behavior

## Impact

- `src/app.py`: Add new SettingsScreen import and navigation; update screen registration
- `src/kv/main.kv`: Add Settings button to bottom nav
- `src/kv/log_panel.kv` and `src/screens/log_panel.py`: Auto-save path to come from settings; integrate with cleanup logic
- `src/kv/*.kv` and relevant `.py` files: All font_size declarations updated from `px`/`dp`/bare int to `sp`
- New file: `src/screens/settings_screen.py`
- New file: `src/kv/settings_screen.kv`
- New or updated service: `src/services/log_cleanup_service.py` or integrate into `LogService`
- `src/services/storage_service.py` / `SettingsStore`: Add keys for log_dir and max_log_size_mb
