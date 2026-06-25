## 1. Model & Storage Layer

- [x] 1.1 Add `description` and `is_predefined` fields to `Scenario` dataclass in `src/models/scenario.py`
- [x] 1.2 Extend `ScenarioStore.load_all()` to parse `description` field and return `list[Scenario]` (typed, not dicts)
- [x] 1.3 Extend `ScenarioStore.save_all()` to serialize `Scenario` objects with all fields
- [x] 1.4 Add `ScenarioStore.save(scenario)` for individual create/update
- [x] 1.5 Add `ScenarioStore.delete(name)` for removal
- [x] 1.6 Add `ScenarioStore.get(name)` for lookup by name
- [x] 1.7 Handle missing/corrupt `data/scenarios.json` gracefully (return `[]`)
- [x] 1.8 Update `ScenarioService.get_predefined_scenarios()` to set `is_predefined=True`
- [x] 1.9 Write unit tests for model changes and new CRUD methods

## 2. Scenario Editor Screen — Layout & Navigation

- [x] 2.1 Create `src/screens/scenario_editor_screen.py` with three-panel `BoxLayout` (list panel, editor panel, palette panel)
- [x] 2.2 Create `src/kv/scenario_editor_screen.kv` with the three-panel layout
- [x] 2.3 Register `ScenarioEditorScreen` in `src/app.py` ScreenManager and load its KV file
- [x] 2.4 Add "Scenarios" button to `src/kv/actions_screen.kv` that navigates to the editor screen
- [x] 2.5 Add "Back" button on editor screen returning to actions screen with unsaved-changes prompt
- [x] 2.6 Remove old `ScenarioBuilderScreen` references (screen, KV, import in app.py)

## 3. Scenario List Panel

- [x] 3.1 Load all scenarios (predefined + user) into the left panel on enter
- [x] 3.2 Display predefined scenarios with lock icon and distinct visual style
- [x] 3.3 Display user scenarios with delete button on select
- [x] 3.4 Handle scenario selection: load into editor panel, enable/disable controls based on `is_predefined`

## 4. Action Sequence Editor (Center Panel)

- [x] 4.1 Display selected scenario's action sequence as cards with "->" separators between them
- [x] 4.2 Render name and description as editable text inputs (disabled for predefined)
- [x] 4.3 Implement drag-to-reorder within the sequence using Kivy `on_touch_move`
- [x] 4.4 Implement visual insertion indicator line during drag
- [x] 4.5 Add remove (X) button on each action card for user-defined scenarios
- [x] 4.6 Add "Trash" drop zone at the bottom for drag-to-delete
- [x] 4.7 Disable all drag/reorder/remove controls when editing a predefined scenario

## 5. Action Palette (Right Panel)

- [x] 5.1 Display all `Action` enum values as draggable chips with name and description
- [x] 5.2 Implement drag from palette to sequence (add action at insertion point)
- [x] 5.3 Palette shows all actions regardless of whether they're already in the sequence

## 6. Undo / Redo

- [x] 6.1 Implement command-pattern undo stack (record action, data pairs on mutation)
- [x] 6.2 Support undo for: add action, remove action, reorder action, rename, update description
- [x] 6.3 Support redo (replay undone operations in forward order)
- [x] 6.4 Add Ctrl+Z (undo) and Ctrl+Shift+Z (redo) keyboard bindings
- [x] 6.5 Add Undo/Redo toolbar buttons that disable when no actions available
- [x] 6.6 Cap undo stack at 50 operations
- [x] 6.7 Clear undo stack on save

## 7. Save, Delete, and Scenario List Refresh

- [x] 7.1 Implement "Save" button: persist current scenario via `ScenarioStore.save()`, clear undo stack, refresh list
- [x] 7.2 Implement "Delete" button with confirmation popup for user-defined scenarios only
- [x] 7.3 Refresh scenario list panel after save/delete operations
- [x] 7.4 Update `ActionsScreen` scenario spinner when returning from editor (refresh scenarios)

## 8. Testing & Verification

- [x] 8.1 Write unit tests for new `ScenarioStore` CRUD methods
- [x] 8.2 Write unit tests for undo/redo command stack
- [x] 8.3 Write unit tests for scenario model changes (description, is_predefined, serialization)
- [x] 8.4 Write tests for merge behavior (user scenario with same name as predefined)
- [x] 8.5 Run full test suite and fix any regressions
