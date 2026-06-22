## 1. Service Layer — Add skip mask to ScenarioService

- [x] 1.1 Add `skip_actions: set[Action] | None = None` parameter to `ScenarioService.run_scenario()`
- [x] 1.2 In the action loop, check if current action is in `skip_actions`; if so, record as `ActionState.SKIPPED` (add SKIPPED to ActionState enum) and `continue` to next action
- [x] 1.3 Update `run.per_action_status` to include the skipped status
- [x] 1.4 Ensure cancel_check still works with skip logic (skipped actions should not affect stop-on-failure)
- [x] 1.5 Replace the current four predefined scenarios with the two new ones in `get_predefined_scenarios()`:
  - "Full Clean build": `[CLEAN, SYNC_SRC, BUILD, PATCH, BUILD, PULL_APK, RUN]`
  - "Rebuild": `[SYNC_SRC, BUILD, PULL_APK, RUN]`

## 2. Data Model — Add SKIPPED state to ActionState enum and descriptions to Action enum

- [x] 2.1 Add `SKIPPED = "skipped"` to ActionState enum in `src/models/action.py`
- [x] 2.2 Update any existing code that assumes only IDLE/RUNNING/SUCCESS/FAILED/CANCELLED
- [x] 2.3 Add a `description` property to the `Action` enum in `action.py`:
  - `SYNC_SRC`: `"Sync source files to WSL"`
  - `CLEAN`: `"Clean WSL working directory"`
  - `BUILD`: `"Build APK with Buildozer"`
  - `PATCH`: `"Apply patches to .buildozer"`
  - `PULL_APK`: `"Download APK from WSL"`
  - `RUN`: `"Install and run APK on device"`

## 3. UI Component — Create ActionCard widget

- [x] 3.1 Create `src/screens/action_card.py` with `ActionCard` class (subclass of `BoxLayout`)
- [x] 3.2 Add Kivy properties: `action_name` (StringProperty), `description` (StringProperty, populated from `Action.description`), `is_skipped` (BooleanProperty, default False), `allow_click` (BooleanProperty, default False)
- [x] 3.3 Add a Button bound to `action_name` (clicking it triggers a callback via `on_action_click`)
- [x] 3.4 Add a Label for `description` text
- [x] 3.5 Add a Checkbox for "Skip action" that toggles `is_skipped`
- [x] 3.6 Create `src/kv/action_card.kv` template rendering the card layout
- [x] 3.7 Register the kv file in main.kv or the app

## 4. UI Component — Create ActionChain layout (in ActionsScreen)

- [x] 4.1 In `actions_screen.kv`, replace the right-column scenario panel with: scenario Spinner dropdown + "Allow running actions separately" Checkbox
- [x] 4.2 Add a horizontal ScrollView section for the action chain between the controls and the LogPanel
- [x] 4.3 Add a `chain_container` BoxLayout (horizontal, inside the ScrollView) that will hold ActionCard widgets
- [x] 4.4 Add arrow labels (`→`) between consecutive cards inside the chain container
- [x] 4.5 Add "Run Scenario" button (green) and "Cancel" button (red) below the chain

## 5. Screen Logic — Rewrite ActionsScreen class

- [x] 5.1 Add `allow_separate_execution` BooleanProperty (default False) bound to the checkbox
- [x] 5.2 Add `_current_scenario` ObjectProperty to track the selected scenario
- [x] 5.3 Update `_refresh_scenarios()` to also trigger chain rebuild on selection
- [x] 5.4 Add `_build_action_chain(scenario: Scenario)` method: clear chain_container, create ActionCards for each action, add arrow separators, bind on_action_click
- [x] 5.5 Update `run_scenario()`: collect skip_actions from card `is_skipped` states, pass to `_scenario_service.run_scenario()`
- [x] 5.6 Add `_on_action_card_click(action: Action)` method: checks `allow_separate_execution`, if allowed runs the single action via `_runner.run_action()`, otherwise shows a hint popup
- [x] 5.7 Remove `run_single_action()` string-based dispatch method (or simplify to accept an Action enum directly)
- [x] 5.8 Wire scenario_spinner `on_text` to rebuild the action chain

## 6. KV Template — Remove standalone action buttons, add new layout

- [x] 6.1 In `actions_screen.kv`, remove the left-column GridLayout with individual action buttons (Sync SRC, Clean, Build, Patch, Pull APK, Run)
- [x] 6.2 Remove the Cancel button from the left column (keep only the single Cancel)
- [x] 6.3 Replace the left/right split with a single vertical flow: profile toolbar → scenario dropdown + allow-separate checkbox → action chain (ScrollView) → Run Scenario / Cancel buttons → LogPanel
- [x] 6.4 Keep the profile toolbar (spinner, Delete, Edit, New) unchanged

## 7. Verification

- [x] 7.1 Run the application and verify scenario dropdown shows exactly two predefined scenarios: "Full Clean build" and "Rebuild" (plus any custom scenarios)
- [x] 7.2 Select a scenario and verify action chain renders with correct cards and arrows
- [x] 7.3 Toggle skip checkboxes and run scenario — verify skipped actions are not executed
- [x] 7.4 Toggle "Allow running actions separately" off — verify card button clicks do nothing
- [x] 7.5 Toggle "Allow running actions separately" on — verify card button click runs single action
- [x] 7.6 Verify Cancel button stops any running operation (single action or scenario)
- [x] 7.7 Verify no standalone action buttons exist on the main screen
