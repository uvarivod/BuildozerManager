## Context

BuildozerManager is a Kivy desktop application with screen-based navigation (ScreenManager), using KV language for layout and Python for screen logic. Text sizing currently uses a mix of bare integers, `dp`, and `sp` units inconsistently across KV files and Python. Log storage auto-saves to a hardcoded `logs/` directory with no cleanup mechanism. There is no help or onboarding UI.

Three user-facing changes are requested: DPI-safe text sizing, contextual help popups, and a settings page with log path/size configuration and automatic log cleanup.

## Goals / Non-Goals

**Goals:**
- All font sizes in KV and Python use `sp` units for proper DPI scaling
- Each screen has a help button that opens a popup explaining that screen's purpose and controls
- A dedicated popup explains SHIFT+click range selection in the log panel
- A new Settings screen lets users configure log directory path and max folder size in MB
- Automatic cleanup removes oldest log files when the log folder exceeds the configured size

**Non-Goals:**
- Not changing the log viewer's real-time streaming, color-coding, or timestamp format
- Not adding user authentication or multi-user support
- Not changing the profile or scenario storage mechanisms
- Not adding internationalization (though `sp` migration lays groundwork)

## Decisions

### 1. `sp` Migration Strategy
- **Decision**: Audit all `.kv` files and Python `font_size=` assignments, replace any value not in `sp` with equivalent `sp` value (1:1 numeric conversion for `dp` and bare ints)
- **Rationale**: Kivy's `sp` scales with system font DPI, `dp` scales with display density but not font preferences, bare pixels scale with nothing. Migration is mechanical and low-risk.
- **Alternatives considered**: Using `dp` throughout — rejected because `sp` respects user font size settings.

### 2. Help Popups
- **Decision**: Add a small `?` `Button` to each screen's top bar. On click, open a `Popup` with screen-specific help text describing the available controls and their purpose. The log help popup additionally explains SHIFT+click selection mechanics.
- **Rationale**: Popups are already used in the app (confirm delete, save log). This follows existing patterns (`kivy.uix.popup.Popup`).
- **Alternatives considered**: Tooltip on hover — Kivy has limited tooltip support; bottom status bar text — less discoverable.

### 3. Settings Page
- **Decision**: New `SettingsScreen` added to `ScreenManager`, accessible via a new "Settings" button in the bottom nav bar. Uses `SettingsStore` for persistence.
- **Rationale**: Follows the existing screen pattern (ActionsScreen, ProfileEditorScreen, ScenarioEditorScreen). `SettingsStore` already handles JSON persistence.
- **Alternatives considered**: Modal dialog — harder to extend; separate window — adds complexity.

### 4. Log Directory Configuration
- **Decision**: Store `log_dir` and `max_log_size_mb` in `SettingsStore` (persisted to `data/settings.json`). Log panel reads `log_dir` on init for auto-save path. Default: `log_dir = "logs"`, `max_log_size_mb = 100`.
- **Rationale**: Reuses existing settings persistence; no new storage layer needed.

### 5. Log Cleanup Mechanism
- **Decision**: After each build scenario/action completes, check the total size of the configured log directory. If it exceeds `max_log_size_mb`, delete oldest log files (by modification time) until size is under the limit.
- **Rationale**: Simple, predictable, and triggered post-execution so it doesn't interfere with running builds.
- **Alternatives considered**: Background watchdog — overengineered; on-app-start cleanup — less timely.

## Risks / Trade-offs

- [Cleanup timing] If the user sets a very small limit and runs many builds, logs from the same session may be deleted while the app is still running → Mitigation: Only clean up files that are not currently open/written to by the app.
- [sp migration misses] Some font sizes may be set dynamically in Python (e.g., `Label(font_size=...)`) and could be missed in audit → Mitigation: Grep for `font_size` across all `.py` files and review each occurrence.
- [Path validation] User could input an invalid log directory path → Mitigation: Validate path on save; if invalid, show error and keep previous value.
