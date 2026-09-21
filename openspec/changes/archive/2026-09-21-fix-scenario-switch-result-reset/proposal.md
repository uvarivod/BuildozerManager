## Why

Switching scenarios via the dropdown currently preserves stale per-action results (SUCCESS/FAILED/SKIPPED/etc.) and the aggregate `status_label` ("Scenario: ...") from the previously selected/run scenario. `ActionsScreen._build_action_chain()` indiscriminately restores widget state by index to survive window resizes, so the first N cards of the newly selected scenario inherit the old scenario's visual results even though a different action sequence is now displayed. This misleads users into thinking the new scenario has already been executed.

## What Changes

- Reset all per-action visual results (card `action_state`, `is_completed`, `is_skipped`, `patch_states`) when a different scenario is selected via the dropdown, so the newly built action chain starts in `PENDING`/idle state.
- Reset aggregate result display (`status_label` back to `"Ready"`) on scenario switch, unless a scenario is actively running (guard against interrupting mid-run UI).
- Keep resize-survival behavior intact: window-resize rebuilds SHALL still preserve per-action status for the *current* scenario; scenario-switch rebuilds SHALL NOT preserve old results.
- Change is visual/state reset only; no persistence or runner logic change. If the user re-selects the same scenario without a switch, no unnecessary reset is needed (idempotent).

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `scenario-orchestration`: Add requirement that switching scenarios via the selector resets displayed scenario run results (per-action and aggregate) and distinguishes switch vs. resize rebuild semantics.

## Impact

- Affected code: `src/screens/actions_screen.py` (`on_scenario_selected`, `_build_action_chain`, `_refresh_actions_layout`, `_reset_action_chain_states`, `status_label`), `src/screens/action_card.py` (reset contract), `src/kv/actions_screen.kv` (no KV change expected)
- Tests: `tests/test_actions_screen.py` — new/updated coverage for switch-reset vs. resize-preserve
- Docs/Specs: `openspec/specs/scenario-orchestration/spec.md` delta
- No API or storage format change; no new dependencies. Risk is low and localized to UI state handling; existing `2026-07-16-fix-action-state-reset-on-resize` invariant (status survives resize) must remain green.
