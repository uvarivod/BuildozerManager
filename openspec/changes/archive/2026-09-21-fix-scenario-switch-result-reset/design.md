## Context

`ActionsScreen` shows a `Spinner` (`scenario_spinner`) backed by `src/screens/actions_screen.py`. Selecting a scenario calls `on_scenario_selected(text)` → `_build_action_chain(scenario)` which (re)creates `ActionCard`/`PatchCard` widgets for `scenario.action_sequence`.

To fix `2026-07-16-fix-action-state-reset-on-resize`, `_build_action_chain` snapshots `_action_cards[*].action_state/is_completed/is_skipped/patch_states` before `_clear_action_chain()` and restores by index after rebuilding. This is invoked from two paths:

- **Resize**: `_refresh_actions_layout()` → `_build_action_chain(self._current_scenario)` — must preserve status (spec `Scenario run per-action status survives UI rebuilds`).
- **Switch**: `on_scenario_selected()` → `_build_action_chain(scenario)` — currently also preserves, incorrectly leaking stale results (e.g. Full Clean build 7 cards with SUCCESS → Rebuild 4 cards shows SUCCESS on first 4).

Additional stale state: `status_label` (`"Scenario: SUCCESS"` / `"Scenario: Failed"` / `is_running` side-effects) is not cleared on switch; `_reset_action_chain_states()` exists but is only called in `run_scenario()`.

Stakeholders: ActionsScreen UI, scenario orchestration spec, users relying on accurate per-scenario feedback. Constraint: must not regress resize-preserve invariant; no model/storage change.

## Goals / Non-Goals

**Goals:**
- On dropdown switch to a different scenario, the action chain displays in initial state (all `PENDING`, not completed/skipped) and aggregate label resets to `"Ready"` (or appropriate idle state).
- Preserve existing resize behavior for the *same* scenario.
- Minimal, localized change to `actions_screen.py`; no new dependencies or persistence changes.

**Non-Goals:**
- Moving widget state to `ScenarioRun`/model layer (deferred; out of scope).
- Changing scenario runner (`ScenarioService.run_scenario`) skip/stop-on-failure semantics.
- Clearing `LogService`/log panel on switch (log cleanup stays tied to run end via `cleanup_logs`).
- Editing predefined scenario definitions or `scenario-orchestration` runner sequences.

## Decisions

**Decision 1: Add `preserve_state` flag to `_build_action_chain` (default `False` for safety) over separate methods.**
- Why: Single method currently serves both call sites with opposite semantics. A boolean makes intent explicit at call site, keeps snapshot/restore code in one place, avoids duplication.
- Alternatives considered:
  - *Call `_reset_action_chain_states()` after build in `on_scenario_selected`* — would double-rebuild; still leaves index-restore in place (needs suppression).
  - *Split into `_build_action_chain` + `_rebuild_action_chain_preserve()`* — more code, same effect; flag is simpler and easier to grep.
  - *Store state in `ScenarioRun` instead of widgets* — correct long-term but larger refactor, explicitly deferred in prior fix's trade-offs.

**Decision 2: Reset `status_label` and ensure not running on switch.**
- Why: Aggregate result (`_on_scenario_done` sets `"Scenario: {status}"`) is per-run, not per-scenario-definition; showing it for a never-run scenario is misleading.
- Implementation: In `on_scenario_selected`, before/after building chain, set `status_label = "Ready"` when not `is_running`; guard with `if not self.is_running` to avoid clobbering mid-run if scenario is switched while running (edge case — Spinner is disabled during run via `_disable_controls`, but guard is defensive).

**Decision 3: Identify "switch" vs. "resize" at the caller, not by comparing scenario identity inside `_build_action_chain`.**
- Why: Keeps `_build_action_chain` pure on flag; callers express intent: `_refresh_actions_layout` passes `preserve_state=True` (resize/enter), `on_scenario_selected` passes `False` (or default). `on_enter` refresh that reloads same scenario also preserves.
- Alternative: Compare `scenario == _current_scenario` inside method — fragile if same-name different object (predefined vs user) and hides intent.

**Decision 4: Handle `Select scenario` / empty selection same as switch — clear chain and reset label.**
- Already does `_clear_action_chain()`; add label reset for consistency.

## Risks / Trade-offs

- [Risk] **Regressing resize-preserve spec** → Mitigation: `_refresh_actions_layout` and `on_enter` explicitly pass `preserve_state=True`; add regression test that simulates `_build_action_chain` after setting cards to SUCCESS then triggering resize path and asserting state retained.
- [Risk] **Index-based restore elsewhere reintroduced** → Mitigation: Keep restore block guarded by `if preserve_state and saved_states`; `preserve_state=False` skips it entirely rather than resetting after. Greppability: flag appears at all call sites.
- [Risk] **Switch during active run** → Mitigation: Spinner is disabled via `_disable_controls` while `is_running`; defensive guard leaves `status_label` alone if `is_running` is True, and `on_scenario_selected` should early-return or defer reset if running. Choose to allow reset only when not running.
- [Risk] **PatchCard `patch_states` not fully cleared** → Mitigation: Reset uses `card.reset_state()` contract which for `PatchCard` resets `patch_states` to all PENDING; verify `ActionCard`/`PatchCard` reset covers all stored keys (checked in `action_card.py`).
- Trade-off: Widget-owned state remains — short-term fix keeps tech debt (state on view). Long-term move to `ScenarioRun` would eliminate class of bugs but out of scope for this fix.

## Migration Plan

- No data migration. Change is in-memory UI state only.
- Deploy: update `actions_screen.py` and specs; no config change.
- Rollback: revert flag and call-site arguments; previous behavior (leak) returns but no data loss.

## Open Questions

- Should switching scenario also clear the log panel (`log_panel.clear` or similar)? Current decision: No — logs are historical; users can manually Clear. Can be revisited if UX testing says log should reset with results.
- Should re-selecting the *same* scenario name preserve or reset? Decision: Reset is idempotent and harmless; re-selecting same entry will reset to PENDING. If product wants preserve on same-scenario re-select, add `if text == _current_scenario.name: preserve=True` branch — currently not needed.
