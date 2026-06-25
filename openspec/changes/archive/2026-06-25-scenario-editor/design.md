## Context

The existing `ScenarioBuilderScreen` provides a minimal add/remove/move-up/move-down interface for creating custom action sequences. Predefined scenarios ("Full Clean build", "Rebuild") are hardcoded in `ScenarioService.get_predefined_scenarios()` and cannot be edited or deleted. User scenarios are persisted as raw dicts via `ScenarioStore` with no CRUD abstraction. The UI lacks drag-and-drop, undo/redo, and visual feedback.

The Actions screen (`actions_screen.kv`) currently has no dedicated "Scenarios" button; scenario selection is via a Spinner.

## Goals / Non-Goals

**Goals:**
- Replace `ScenarioBuilderScreen` with a full Scenario Editor (`ScenarioEditorScreen`)
- Three-panel layout: scenario list (left), action sequence editor (center), action palette (right)
- Drag-and-drop for: adding actions from palette to sequence, reordering within sequence, removing by drag to trash
- Undo/Redo stack for all editing operations (50-deep)
- Predefined scenarios visually locked (cannot edit, cannot delete)
- CRUD-style `ScenarioStore` methods (create, read, update, delete)
- `Scenario` model gains `description` and `is_predefined` fields
- Navigation: "Scenarios" button on Actions screen opens the editor; "Back" returns

**Non-Goals:**
- Nested scenario composition (scenarios within scenarios)
- Scenario import/export
- Scenario sharing between users
- Real-time collaboration
- Keyboard shortcut customization beyond basic undo/redo (Ctrl+Z, Ctrl+Shift+Z)

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Drag-and-drop approach | Kivy `on_touch_move` events (no external drag-drop library) | Avoids new dependencies; the action palette and sequence are custom layouts, not list widgets that support DnD natively |
| Undo/Redo implementation | Command pattern: record `(action, data)` pairs on mutation, replay in reverse for undo | Simple, testable, 50-deep bounded stack prevents memory leaks |
| Predefined scenario protection | Flag `is_predefined: bool` on `Scenario` plus UI-level guards (locked icon, disabled buttons, grayed out) | Defense-in-depth — model signals intent, UI enforces it |
| Scenario storage format | JSON via `data/scenarios.json` (existing `ScenarioStore`), but with typed models | Matches existing pattern; change adds proper CRUD methods and model validation |
| Trash zone for deletion | A fixed "Trash" area (drop target) at the bottom of the editor panel + a delete icon on each action | User preference: some prefer drag-to-trash, others want a click-to-delete affordance |
| Screen navigation | New `ScenarioEditorScreen` added to `ScreenManager`, navigated via `manager.current` | Consistent with Profile Editor pattern |

## Risks / Trade-offs

- **[Drag-and-drop on mobile/touch]** Kivy `on_touch_move` works on desktop but may need tuning for touch-only devices → Mitigation: test on target devices early; fall back to tap-to-select + up/down arrows for mobile
- **[Undo state after save]** Undoing after saving may leave `scenarios.json` inconsistent → Mitigation: snapshot before save, or clear undo stack on save
- **[Predefined scenario drift]** Hardcoded predefined scenarios in `ScenarioService` could differ from locked copies in storage → Mitigation: always use `ScenarioService` as source of truth for predefined; storage only holds user scenarios
