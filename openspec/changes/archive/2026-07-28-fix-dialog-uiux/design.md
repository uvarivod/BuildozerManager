## Context

The BuildozerManager app (Kivy 2.3.1) has 20+ dialog popups scattered across 5 screen files. Each screen builds popups inline with duplicated boilerplate: create BoxLayout, add Label, add Button row, create Popup, call .open(). This leads to:

- **No shared dialog system**: Same error popup pattern implemented 3+ times differently
- **Missing dismiss buttons**: `profile_editor_screen.py` has 2 popups with no OK button
- **Inconsistent sizing**: Error popups use sizes ranging from (0.35, 0.18) to (0.5, 0.3)
- **No keyboard support**: Users must click buttons; no Escape/Enter handling
- **Accidental dismissal**: Most popups allow dismiss on outside click
- **Transient notifications use full popups**: "Settings saved" requires clicking OK

The app uses a dark theme with green (0.2, 0.6, 0.2) for positive actions and red (0.8, 0.2, 0.2) for destructive actions. All styling is hardcoded RGBA tuples.

## Goals / Non-Goals

**Goals:**
- Create `dialog_helper.py` with factory functions for info, confirm, error, success, and toast dialogs
- Centralize styling constants (colors, fonts, sizes) in one module
- Add keyboard support (Escape to dismiss, Enter to confirm) to all dialogs
- Add toast/snackbar component for transient notifications
- Fix missing dismiss buttons on all popups
- Standardize popup sizes by dialog type
- Set `auto_dismiss=False` on confirmation dialogs
- Migrate all existing screens to use the new dialog system

**Non-Goals:**
- Refactoring `scenario_editor_screen.py` into smaller files (separate change)
- Adding animations or transitions between dialogs
- Supporting mobile touch gestures beyond existing Kivy behavior
- Changing the overall app layout or screen navigation
- Adding new dialog types not currently used in the app

## Decisions

### Decision 1: Module-based factory functions (not class hierarchy)

**Choice**: Use standalone factory functions (`show_info_dialog()`, `show_confirm_dialog()`, etc.) in a single `dialog_helper.py` module.

**Rationale**: The current codebase uses inline Popup construction everywhere. A module with functions is the simplest migration path—screens import and call a function instead of building popups manually. A class hierarchy (e.g., `BaseDialog`, `ErrorDialog`, `ConfirmDialog`) adds complexity without benefit since dialogs are fire-and-forget.

**Alternatives considered**:
- *Subclass Popup*: More OOP, but adds boilerplate and doesn't match existing patterns
- *Builder pattern*: Over-engineered for simple popups

### Decision 2: Styling constants in dialog_helper.py

**Choice**: Define color tuples, font sizes, and size constants at module level in `dialog_helper.py`.

```python
# Colors
COLOR_BG = (0.15, 0.15, 0.15, 1)
COLOR_TEXT = (0.85, 0.85, 0.85, 1)
COLOR_BTN_POSITIVE = (0.2, 0.6, 0.2, 1)
COLOR_BTN_DESTRUCTIVE = (0.8, 0.2, 0.2, 1)
COLOR_BTN_NEUTRAL = (0.3, 0.3, 0.3, 1)

# Sizes
DIALOG_SIZE_INFO = (0.4, 0.25)
DIALOG_SIZE_CONFIRM = (0.45, 0.3)
DIALOG_SIZE_ERROR = (0.5, 0.3)
DIALOG_SIZE_FORM = (0.6, 0.5)
TOAST_SIZE = (0.3, 0.08)
```

**Rationale**: Centralizes the dark theme. Currently colors like `(0.2, 0.6, 0.2, 1)` are duplicated across 5 files. One module makes theme changes trivial.

**Alternatives considered**:
- *KV file for styling*: Kivy-idiomatic but adds another file; Python constants are simpler for this use case
- *Config file*: Over-engineered for a single-project app

### Decision 3: Keyboard binding via on_key_down

**Choice**: Bind `on_key_down` on each Popup to handle Escape (dismiss) and Enter (confirm).

```python
def _on_key_down(popup, window, key, scancode, codepoint, modifiers):
    if key == 27:  # Escape
        popup.dismiss()
    elif key == 13:  # Enter
        if popup._confirm_callback:
            popup._confirm_callback()
            popup.dismiss()
```

**Rationale**: Kivy's Window.bind('on_key_down', ...) is the standard way to add keyboard shortcuts. Each popup stores its confirm callback as an attribute.

**Alternatives considered**:
- *Focus-based Enter*: Would require managing focus states; too complex for fire-and-forget dialogs
- *Button keyboard shortcut*: Kivy buttons don't natively support accelerator keys

### Decision 4: Toast as auto-dismissing Popup (not Overlay)

**Choice**: Implement toast as a small Popup that auto-dismisses after 2 seconds using Kivy Clock.

**Rationale**: Kivy doesn't have a built-in snackbar/toast. A small Popup with `auto_dismiss=True` and `Clock.schedule_once(popup.dismiss, 2)` is the simplest approach. The toast uses `size_hint=(0.3, 0.08)` and positions at bottom-center.

**Alternatives considered**:
- *Canvas overlay*: More performant but requires custom widget and drawing logic
- *Animation-based*: Flashier but adds complexity

### Decision 5: auto_dismiss=False for confirmation dialogs

**Choice**: All confirmation dialogs (confirm, error, form) use `auto_dismiss=False`. Info dialogs use `auto_dismiss=True` for quick dismissal.

**Rationale**: Confirmation dialogs require explicit user action. Accidental outside-click dismissal loses context (e.g., unsaved changes dialog). Info popups are read-only and can be dismissed easily.

## Risks / Trade-offs

- **Migration effort**: 20+ inline popups across 5 files need updating. Mitigation: Do screen-by-screen; each screen is independent.
- **Toast timing**: 2-second auto-dismiss may be too fast for long messages. Mitigation: Allow custom duration parameter.
- **Kivy version constraints**: Toast auto-dismiss relies on Clock; should work in Kivy 2.3.1. Mitigation: Test on target version.
- **Breaking existing behavior**: Changing popup sizes/positions may surprise users. Mitigation: Keep sizes close to current averages; use standardized values.
