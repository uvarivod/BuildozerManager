## Context

The app currently has a fixed `Action` enum (SYNC_SRC, CLEAN, BUILD, PATCH, PULL_APK, RUN) and a decorator-based `PatchRegistry` for predefined source-level patches. The scenario editor palette lists all enum values as draggable chips in a single "Available Actions" section. Custom actions cannot be created, patches are only manageable from profile editor checkboxes, and palette chips have no edit interaction — only drag-to-add.

## Goals / Non-Goals

**Goals:**
- Allow users to create custom actions with Name, Description, Type (Action/Patch), and Logic (file path for scripts, or "built-in" identifier)
- Split the palette into "Available Actions" and "Available Patches" sections
- Clicking any palette chip opens an edit dialog showing action properties (read-only for built-in, editable for custom)
- Drag-and-drop from palette to edit pane continues working for both action types
- Custom actions persist across app restarts via JSON storage
- Built-in actions remain immutable (no edit/delete)

**Non-Goals:**
- Custom action execution engine changes (existing ActionRunner handles the run dispatch, custom actions will just call the script path)
- No batch script editor — only file path selection via a file chooser
- No reordering of palette sections
- No drag-to-pane for Patch-type actions independently of a PATCH action in the sequence

## Decisions

### Decision 1: CustomAction model separate from Action enum
The existing `Action` enum is used extensively as a type-safe value (in model comparisons, KV bindings, action_runner dispatch). Extending it with dynamic values would break type checks everywhere. Instead, introduce a `CustomAction` dataclass and unify the palette to use an `ActionItem` union type (`Action | CustomAction`).

- **Why**: Minimum refactoring of existing Action enum usage. ActionRunner already dispatches on Action enum — custom actions of type `Action` will map to a new `CUSTOM_SCRIPT` enum member internally, while custom actions of type `Patch` will reuse `PATCH`.
- **Trade-off**: Slightly more complex dispatch in ActionRunner (needs to check if it's a built-in vs custom to decide execution path).

### Decision 2: Palette uses a unified list with section labels
The palette `GridLayout` will be replaced with a `BoxLayout` containing two `GridLayout` children, separated by section header labels ("Available Actions" and "Available Patches"). The existing `_build_palette` method iterates over `Action` enum — this will be extended to also iterate over loaded `CustomAction` items, filtering by type.

- **Why**: Minimal layout change. KV and screen Python code can stay mostly intact.
- **Trade-off**: Patch-type custom actions appear in the palette but are NOT independently draggable to the sequence (they serve as visual reference/documentation only). Only Action-type custom actions can be dropped into a scenario.

### Decision 3: Edit dialog on click
Clicking a chip (touch_up without drag > 10px threshold) opens a `Popup` with the action's fields. Built-in actions show read-only fields. Custom actions allow editing Name, Description, Type (disabled after creation), and Logic. A "Delete" button appears for custom actions only.

- **Why**: Reuses existing Kivy Popup pattern already used in the codebase (confirm dialogs, etc.).
- **Trade-off**: Popup vs inline editing — popup is simpler and doesn't disrupt the palette layout.

### Decision 4: CustomAction persistence
Custom actions stored in `data/custom_actions.json` via a new `CustomActionStore` class following the pattern of `ScenarioStore` / `ProfileStore` / `SettingsStore`.

- **Why**: Consistent with existing persistence approach (JSON files in `data/`).

## Risks / Trade-offs

- **Custom script execution** → Custom `Action`-type actions need to run a user-specified `.bat`/`.sh` file. This adds a new execution path in `ActionRunner` that must handle file-not-found, permission errors, and timeout. Mitigation: validate file exists when saving, show error popup if missing at run time.
- **Action enum dispatch coupling** → Mapping custom actions to `CUSTOM_SCRIPT` means `ActionRunner.run_action()` needs to branch on whether the action is custom or built-in. Mitigation: keep the branch clean in a single method.
- **Patch-type actions in palette** → Users might expect to drag Patch-type chips into the sequence directly, but patches must only run via the PATCH action. Mitigation: clear visual labeling and disable drag on Patch-type chips.
