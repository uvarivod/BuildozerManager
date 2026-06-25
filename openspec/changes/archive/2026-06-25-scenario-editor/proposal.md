## Why

The current ScenarioBuilderScreen provides only a rudimentary add/remove/move-up/move-down interface with no drag-and-drop, no undo/redo, no visual editing, and no distinction between predefined (read-only) and user-defined scenarios. Users need a full-featured Scenario Editor to compose and reorder action sequences intuitively.

## What Changes

- Replace the existing `ScenarioBuilderScreen` with a full Scenario Editor accessible via a "Scenarios" button on the Actions screen
- New Scenario Editor page with three UI areas: scenario list panel, action sequence editor (with "->" separators), and available actions palette
- Drag-and-drop for adding actions to the sequence, reordering within the sequence, and removing actions (via drag to trash or delete button)
- Undo/Redo support for all editing operations
- Predefined scenarios are locked: not editable, not deletable, visually distinct
- Rename scenario (summary/description field) and reorder/remove actions for user-defined scenarios
- Scenario model gets a `description: str` field in addition to `name` and `action_sequence`
- Load/save user scenarios via existing `ScenarioStore` (`data/scenarios.json`)

## Capabilities

### New Capabilities

- `scenario-editor-ui`: Full scenario editing screen with list panel, action palette, drag-and-drop sequence editor, undo/redo toolbar, and trash zone for removal
- `scenario-editor-storage`: Extended ScenarioStore with CRUD operations (create, read, update, delete) and predefined scenario protection
- `scenario-model`: Extended Scenario model with `description` field; predefined scenario flag

### Modified Capabilities

- `scenario-orchestration`: Scenario model changes (new `description` field) require updating the existing spec; user scenarios loaded from `ScenarioStore` instead of only predefined

## Impact

- Rewrite `src/screens/scenario_builder_screen.py` → `src/screens/scenario_editor_screen.py`
- Rewrite `src/kv/scenario_builder_screen.kv` → `src/kv/scenario_editor_screen.kv`
- Update `src/models/scenario.py` — add `description` and `is_predefined` fields
- Update `src/services/storage_service.py` — enhance `ScenarioStore` with CRUD methods
- Update `src/app.py` — register new screen, wire navigation
- Update `src/kv/actions_screen.kv` — add "Scenarios" button nav
- Update `src/services/scenario_service.py` — support user-defined scenarios from storage
- Remove old `scenario_builder_screen.py` / `.kv` files
