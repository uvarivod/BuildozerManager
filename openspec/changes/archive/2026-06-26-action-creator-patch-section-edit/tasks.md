## 1. Model & Storage Layer

- [x] 1.1 Create `CustomAction` dataclass in `src/models/custom_action.py` with fields: `id`, `name`, `description`, `type` (Action/Patch), `logic` (str), `is_builtin` (bool, default False)
- [x] 1.2 Create `CustomActionStore` in `src/services/storage_service.py` with `load_all()`, `save()`, `delete()` methods persisting to `data/custom_actions.json`
- [x] 1.3 Add `CUSTOM_SCRIPT` member to `Action` enum in `src/models/action.py` for dispatching custom script execution

## 2. Action Execution for Custom Scripts

- [x] 2.1 Add `_run_custom_script()` method to `ActionRunner` that resolves the script path and executes `.bat`/`.sh` via subprocess
- [x] 2.2 Update `ActionRunner.run_action()` to dispatch `Action.CUSTOM_SCRIPT` to `_run_custom_script()`, passing the custom action's logic path from the profile/scenario context

## 3. Palette Rebuild with Section Split

- [x] 3.1 Refactor `ScenarioEditorScreen._build_palette()` to load custom actions from `CustomActionStore` and render two sections: "Available Actions" header + GridLayout for Action-type chips, then "Available Patches" header + GridLayout for Patch-type chips
- [x] 3.2 Add "New Action" button above the palette sections
- [x] 3.3 Update `ActionChip` to accept `CustomAction | Action` union and support read-only/click-only mode for patch-type chips (no drag)
- [x] 3.4 Prevent drag initiation on Patch-type chips in the palette

## 4. Edit & Create Dialogs

- [x] 4.1 Implement `_show_create_action_dialog()` method — Popup with Name (TextInput), Description (TextInput), Type (Spinner: Action/Patch), Logic (TextInput + Browse button for Action-type), Save/Cancel buttons
- [x] 4.2 Implement `_show_edit_dialog(chip_data)` method — Popup showing same fields as create dialog, but read-only for built-in actions, editable Name/Description/Logic for custom actions; "Delete" button for custom actions only
- [x] 4.3 Wire click handler on palette chips (both Action and Patch type) to open edit dialog instead of immediately adding to sequence
- [x] 4.4 Click-to-add still works when drag threshold is not exceeded for Action-type chips (add to sequence at end) — preserve existing behavior

## 5. Integration & Cleanup

- [x] 5.1 Ensure custom actions are loaded on app/scenario-editor startup and available in palette
- [x] 5.2 Update `Scenario._build_action_chain()` in `actions_screen.py` to handle custom action rendering (basic ActionCard with custom name/description)
- [x] 5.3 Verify built-in actions remain immutable: no delete, no type change, read-only dialog
- [x] 5.4 Verify Patch-type chips appear in palette but are not draggable
- [x] 5.5 Run `pytest` to ensure existing tests pass with Action enum addition
