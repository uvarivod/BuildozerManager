## Context

The current UI presents Actions (left column) and Scenarios (right column) as peers. Users can trigger any action individually via dedicated buttons or run a scenario. This dual-mode approach is confusing and undermines scenario-level concerns (sequencing, stop-on-failure, skip). The app uses Kivy 2.3.1 with KV declarative UI, a ScreenManager for navigation, BoxLayout-based layouts, and threading for async execution. Actions are defined as an enum (`Action`) and executed via `ActionRunner`. Scenarios are lists of actions executed in order by `ScenarioService`.

The predefined scenario set is reduced from four to two: **Full Clean build** (`CLEAN → SYNC_SRC → BUILD → PATCH → BUILD → PULL_APK → RUN`) and **Rebuild** (`SYNC_SRC → BUILD → PULL_APK → RUN`). Each action also needs a human-readable short description exposed for the action card UI.

## Goals / Non-Goals

**Goals:**
- Make scenario selection the primary entry point for all execution
- Remove standalone action buttons from the main screen
- Replace with a visual action chain showing scenario steps as cards with skip toggles
- Add a configurable flag to allow/disallow running individual actions from the chain
- Support per-action skip during scenario execution in the service layer
- Keep Cancel as a single global button that stops any running operation

**Non-Goals:**
- No changes to the ActionRunner service internals (individual action execution logic stays the same)
- No changes to the ScenarioBuilder screen (custom scenario creation remains as-is)
- No new persistence layer or data model changes
- No changes to profile management or other screens

## Decisions

0. **Action descriptions defined on the Action enum.** Rather than a separate mapping, add a `description` property to the `Action` enum (or a companion dict) holding short descriptions:
   - `SYNC_SRC`: "Sync source files to WSL"
   - `CLEAN`: "Clean WSL working directory"
   - `BUILD`: "Build APK with Buildozer"
   - `PATCH`: "Apply patches to .buildozer"
   - `PULL_APK`: "Download APK from WSL"
   - `RUN`: "Install and run APK on device"
   Descriptions are consumed by `ActionCard` for display in the chain UI.

1. **Action chain as a horizontal ScrollView of custom widgets.** Each action is rendered as a custom `ActionCard` (BoxLayout subclass) containing: a clickable Button (action name + description), a Skip checkbox. Cards are separated by arrow Labels (`→`). The entire row is wrapped in a horizontal ScrollView for overflow.

2. **Skip mask passed to ScenarioService.** Rather than modifying the Scenario model, the UI builds a `set[Action]` (skip set) from checked cards and passes it to `scenario_service.run_scenario(scenario, profile, skip_actions=...)`. This keeps the service backward-compatible and the model unchanged.

3. **"Allow running actions separately" as a BooleanProperty on ActionsScreen.** A Checkbox at the top. When unchecked, clicking an action card button is a no-op (or shows a tooltip/popup). This avoids adding conditional permission logic in the service layer.

4. **Single Cancel button.** The existing Cancel button in ActionRunner already uses a `threading.Event`. No changes needed — Cancel already works for both individual actions and scenario sequences. The button just calls `action_runner.cancel()`.

5. **Scenario dropdown at the top of the screen.** Replaces the current layout. A `Spinner` widget populated with predefined + custom scenarios. Selecting a scenario populates the action chain below and becomes the current "active" scenario for Run/Cancel.

6. **Running an action from a card button bypasses `stop_on_failure` and skip mask.** When clicking an individual card button, the UI runs that single action via `action_runner.run_action()` directly (not through the scenario runner). This is the same as current individual action execution, just triggered from the card UI.

## Risks / Trade-offs

- **Card layout overflow** → Wrap in horizontal ScrollView; if many actions, user scrolls. Consider vertical stacking as fallback if horizontal is too cramped.
- **Per-action skip vs stop-on-failure interaction** → If an action fails and stop-on-failure is on, remaining actions are skipped regardless of their individual skip checkbox state. Document this in the UI (maybe gray out remaining skip checkboxes after failure).
- **"Allow running actions separately" off + user wants to run just one action** → User must temporarily toggle the checkbox, or run the full scenario (which may include skip-checked actions). Acceptable trade-off since the whole point is to discourage individual execution.
