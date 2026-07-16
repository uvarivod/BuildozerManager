## Why

Resizing or maximizing the window causes all action execution states (In Progress, Passed, Failed) to reset to "Not Run". This makes it impossible to monitor build progress after any window resize, which happens frequently during development.

## What Changes

- Preserve per-action execution state so it survives widget recreation on window resize
- Stop rebuilding the entire action chain on every resize; instead, just re-layout existing widgets
- If rebuilding is required, snapshot and restore action states from old widgets to new ones

## Capabilities

### New Capabilities

*(None — this is a bug fix within existing capabilities.)*

### Modified Capabilities

- `action-execution`: Add requirement that action execution states SHALL persist across window resize/maximize events. The current spec covers RUNNING state emission but not state durability across UI lifecycle events.
- `scenario-orchestration`: Add requirement that scenario run per-action status SHALL survive UI rebuilds triggered by window resize.

## Impact

- **File**: `src/screens/actions_screen.py` — modify `_on_window_resize`/`_refresh_actions_layout`/`_build_action_chain` to preserve or avoid losing state
- **File**: `src/screens/action_card.py` — potentially add a method to snapshot/restore state if preservation approach is chosen
- **Risk**: Minimal; window resize logic is already debounced and isolated
