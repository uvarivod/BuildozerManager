## Context

On the main `ActionsScreen`, scenario selection is a Kivy `Spinner` (`scenario_spinner`) backed by `ScenarioStore` + `ScenarioService.get_predefined_scenarios()` merged into `self._scenarios: list[Scenario]`. The Spinner’s `values` are plain names (`[s.name for s in self._scenarios]`) and the dropdown items are generic `SpinnerOption` buttons. There is no hover information — users must select a scenario to see its action chain or open the editor. Kivy has no built-in tooltip widget; existing hover UI is minimal. The task is to surface `Scenario.description` on hover without changing selection or execution behavior.

## Goals / Non-Goals

**Goals:**
- Show `Scenario.description` when hovering over a Scenarios dropdown item on the main page, with a lightweight tooltip that appears after a short hover and hides on leave/selection.

**Non-Goals:**
- No changes to scenario persistence, runner, or editor.
- No tooltip for the profile Spinner or other dropdowns (scoped to `scenario_spinner` only).
- No modification of `Scenario` model.

## Decisions

**1. Custom `SpinnerOption` subclass (`ScenarioSpinnerOption`) for `scenario_spinner`.**
Kivy `Spinner` exposes `option_cls` (default `SpinnerOption`). Subclassing it lets us hook hover without replacing the whole Spinner/DropDown. Alternative of patching `Spinner` internals or using `DropDown` directly is more invasive. Set `option_cls` in `actions_screen.kv` to `ScenarioSpinnerOption`.

**2. Hover detection via `Window.mouse_pos` / `on_enter`–`on_leave` on the option button.**
Kivy `Button` does not have native hover events, but `on_enter` can be derived from `Window.mouse_pos` binding or by using `HoverBehavior` mixin if available. The option will bind to `Window.mouse_pos`, check `collide_point`, and start a `Clock.schedule_once` tooltip after ~0.3–0.5s; cancel on leave. This matches typical desktop tooltip timing and avoids flicker during fast mouse moves.

**3. Tooltip as a transient `Bubble`/`Label` added to `Window` or screen overlay.**
Re-use a simple floating label (semi-transparent background, small padding, auto-sized to `description`) added to the Window and positioned near the hovered option (`to_window` coords + offset). Hidden on `on_leave`, `on_release`, or when the DropDown dismisses. No persistent state needed.

**4. Data lookup via `ActionsScreen._scenarios` name → description map.**
The option’s `text` is the scenario name; on hover, lookup `next((s.description for s in screen._scenarios if s.name == self.text), "")` via a weak reference to the screen. Cache is refreshed in `_refresh_scenarios()` so tooltip stays in sync with the current list. Fallback: hide tooltip if description is empty/whitespace.

**5. Keep `on_scenario_selected` behavior untouched.**
Tooltip is view-only; selection still goes through `on_text` → `on_scenario_selected` which builds the action chain. Tooltip dismissal is independent.

## Risks / Trade-offs

- [Kivy hover support varies by platform / touch devices have no hover] → Mitigation: tooltip is additive; selection still works, and no hover means no tooltip (graceful degradation).
- [Tooltip may overlap dropdown or go off-screen near edges] → Mitigation: position with small offset and clamp to `Window` bounds; keep size modest and single-line wrap.
- [Tooltip linger after DropDown closes] → Mitigation: dismiss on `DropDown.on_dismiss` and `on_leave`; ensure scheduled `Clock` event is cancelled.
- [Multiple rapid hovers create overlapping tooltips] → Mitigation: single global tooltip instance, re-used and repositioned per hover.

## Migration Plan

No data migration. Visual-only change. Rollback: revert `option_cls` to default `SpinnerOption` and remove tooltip helper.

## Open Questions

- None.
