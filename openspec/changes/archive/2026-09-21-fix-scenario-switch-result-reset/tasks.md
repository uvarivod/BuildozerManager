## 1. Core Fix — Reset on Scenario Switch

- [x] 1.1 Update `ActionsScreen._build_action_chain()` signature to `(_build_action_chain(self, scenario: Scenario | None = None, preserve_state: bool = False))` and guard snapshot/restore with `if preserve_state and saved_states`
- [x] 1.2 Update `ActionsScreen.on_scenario_selected()` to build with `preserve_state=False` (explicit) and reset `status_label` to `"Ready"` when not `is_running`; handle placeholder/empty path (`"Select scenario"`) to clear chain and reset label
- [x] 1.3 Update `ActionsScreen._refresh_actions_layout()` to call `_build_action_chain(self._current_scenario, preserve_state=True)` so resize keeps prior behavior
- [x] 1.4 Audit `on_enter()` scenario reload path: ensure reload of same `_current_scenario` after store refresh preserves state (`preserve_state=True`), not reset
- [x] 1.5 Verify `ActionCard.reset_state()` / `PatchCard` reset covers `action_state`, `is_completed`, `is_skipped`, `patch_states` (no extra clearing needed); confirm new cards start PENDING without needing explicit `_reset_action_chain_states()` call

## 2. Edge Cases & Guards

- [x] 2.1 Guard switch-reset when `is_running == True` (Spinner disabled during run via `_disable_controls`, but add defensive check before resetting `status_label`)
- [x] 2.2 Ensure `_clear_action_chain()` path for placeholder does not leave stale `_action_cards` state that future `preserve_state=True` could restore
- [x] 2.3 Manual check: Full Clean (7) → Rebuild (4) → Build and Sign AAB (3) switches show zero inherited SUCCESS/FAILED; each N-card chain starts PENDING

## 3. Tests

- [x] 3.1 Extend `tests/test_actions_screen.py::TestOnScenarioSelected` — add test: run scenario mock sets first cards to SUCCESS/FAILED/SKIPPED, switch dropdown to different scenario, assert all new cards are PENDING/not completed/not skipped and `status_label == "Ready"`
- [x] 3.2 Add test: switching to "Select scenario" clears chain and resets label
- [x] 3.3 Add regression test: simulate resize via `_refresh_actions_layout()` after setting states to SUCCESS/RUNNING, assert states preserved (covers `preserve_state=True` path)
- [x] 3.4 Add test for placeholder/empty input and missing custom-action early-return (ensure no unintended reset/build)
- [x] 3.5 Run existing suite `pytest tests/test_actions_screen.py tests/test_scenario_service.py` and fix any failures

## 4. Verification & Docs

- [x] 4.1 Run `openspec status --change fix-scenario-switch-result-reset` and `openspec validate --change fix-scenario-switch-result-reset --strict` (or `openspec status --strict` if validate unavailable)
- [x] 4.2 Manual UI smoke: launch app, run a scenario (or mock run), switch via dropdown, confirm visual reset; resize window, confirm preserve
- [x] 4.3 Final check: `git diff` only touches `actions_screen.py` (+ tests) and spec delta; no storage/runner changes
