## 1. Tooltip option for Scenarios dropdown

- [x] 1.1 Create `ScenarioSpinnerOption` subclass of `SpinnerOption` with hover handling (`Window.mouse_pos` binding, hover delay via `Clock.schedule_once`, lookup `Scenario.description` by option `text` from `ActionsScreen._scenarios`, show/hide floating tooltip label) in `src/screens/actions_screen.py` (or `src/screens/tooltip.py` helper)
- [x] 1.2 Add lightweight tooltip widget (floating `Bubble`/`Label` with semi-transparent background, padding, auto-size, positioned near hovered option via `to_window` + offset, clamped to `Window` bounds) and ensure it is dismissed on `on_leave`, `on_release`, and `DropDown.on_dismiss`
- [x] 1.3 Wire `scenario_spinner.option_cls = ScenarioSpinnerOption` in Python or KV (`src/kv/actions_screen.kv` — `option_cls: 'ScenarioSpinnerOption'`) and provide description map from `ActionsScreen._refresh_scenarios()` so options can resolve `text → description`

## 2. Tests and verification

- [x] 2.1 Add unit tests for `ScenarioSpinnerOption` hover logic (mocked `Window`/`Clock`): description lookup by name returns correct text, empty description shows no tooltip, hide on leave/release is called
- [x] 2.2 Add integration test or manual verification step: open main page, open Scenarios dropdown, hover each scenario name and confirm tooltip appears with its description and hides on leave/selection; verify no regression for profile spinner or other dropdowns
- [x] 2.3 Run full test suite (`python -m pytest -q`) and verify no regressions
