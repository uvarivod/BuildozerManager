## Context

When the window is resized or maximized, `ActionsScreen._on_window_resize()` is called after a 200ms debounce, which calls `_build_action_chain()`. This method destroys all existing `ActionCard`/`PatchCard` widgets via `_clear_action_chain()` and recreates them from scratch. Since execution state (`action_state`) is stored as a `StringProperty` on each card widget, the state is lost when widgets are destroyed.

The same resize handler also binds three separate Window events (`on_resize`, `size`, `system_size`), causing redundant rebuilds on a single resize.

## Goals / Non-Goals

**Goals:**
- Action states (PENDING, RUNNING, SUCCESS, FAILED, CANCELLED, SKIPPED) survive window resize and maximize
- Eliminate redundant resize-triggered rebuilds

**Non-Goals:**
- No change to the model layer (state stays on widgets for now)
- No change to scenario editor resize behavior (it has no execution state)
- No change to how state is initially set or updated during execution

## Decisions

- **Approach: Snapshot and restore** — Before rebuilding, read each card's `action_state` and store it by action index. After recreating cards, apply the saved states. This is the minimal change with lowest risk.
- **Alternative considered: Skip rebuild entirely** — `_refresh_actions_layout()` could just skip the chain rebuild on resize and only refresh the profile spinner. However, the rebuild might be needed for other layout adjustments (e.g., Kivy recalculating container sizes), so snapshot/restore is safer.
- **Alternative considered: Move state to model** — A `ScenarioRun`-like object could track per-action state outside widgets. This is architecturally cleaner but a larger refactor with higher risk. Deferred to a future change.
- **Debounce** — The existing 200ms debounce is sufficient; no change needed.

## Risks / Trade-offs

- **[Low risk] Race condition** — If an action finishes between snapshot and restore, its final state could be overwritten with the snapshot value. Mitigation: snapshot is taken immediately before `clear_widgets`, and execution runs on a background thread (the main thread handles the rebuild synchronously), so no state change can happen during the brief rebuild window.
- **[Low risk] PatchCard patch_states** — `PatchCard` has `patch_states: DictProperty` and per-patch state tracking. The same snapshot/restore pattern must be applied to `patch_states` as well, not just `action_state`. Mitigation: snapshot both `action_state` and `patch_states` together per card index.
