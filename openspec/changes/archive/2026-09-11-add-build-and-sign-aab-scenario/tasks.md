## 1. Add predefined scenario

- [x] 1.1 Add third `Scenario` entry to `src/services/scenario_service.py:get_predefined_scenarios()` with `name="Build and Sign AAB"`, `description="Build AAB, signs and copy to src/bin file which you can send to Google Play."`, `action_sequence=[Action.BUILD_AAB, Action.SIGN_APK, Action.PULL_AAB]`, `stop_on_failure=True`, `is_predefined=True`
- [x] 1.2 Verify no import changes needed (`Action` already imported)

## 2. Tests

- [x] 2.1 Add or update tests in `tests/test_scenario_service.py` to assert `get_predefined_scenarios()` returns three scenarios and the third has `name="Build and Sign AAB"` with sequence `[BUILD_AAB, SIGN_APK, PULL_AAB]` and `stop_on_failure=True`
- [x] 2.2 Run the full test suite and verify no regressions

## 3. Manual verification

- [x] 3.1 Launch the app, open the scenario selector, and confirm "Build and Sign AAB" appears alongside "Full Clean build" and "Rebuild" and runs `BUILD_AAB → SIGN_APK → PULL_AAB` with stop-on-failure
