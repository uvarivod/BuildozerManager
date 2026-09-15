## Why

The Scenarios dropdown on the main page lists scenario names only. Users cannot distinguish what each scenario does without selecting it and inspecting the action chain or opening the Scenario Editor. This is especially confusing for the three predefined scenarios and user-created ones with opaque names. A hover tooltip showing the scenario description gives instant context and reduces trial-and-error.

## What Changes

- Add a hover tooltip to each item in the **Scenarios** `Spinner` dropdown on the main `ActionsScreen`.
  - On hover over a dropdown option, show a tooltip/bubble containing `Scenario.description` for that scenario name.
  - Tooltip appears with a short hover delay and disappears on leave or selection.
  - Falls back to no tooltip or "No description" when `description` is empty.
- No change to dropdown selection behavior, scenario execution, or persistence.
- Visual style consistent with existing help popups and tooltips.

## Capabilities

### New Capabilities
- `scenario-dropdown-tooltip`: Hover tooltip on the main-page Scenarios dropdown items showing the scenario description.

### Modified Capabilities

## Impact

- `src/screens/actions_screen.py` — add custom `SpinnerOption` subclass with hover handling; map `scenario.name → description` for `_scenarios` and update tooltip content on refresh.
- `src/kv/actions_screen.kv` — set `option_cls` for the `scenario_spinner` to the new tooltip option class.
- `src/screens/tooltip.py` — new small helper (or inline bubble) for showing/hiding the tooltip label near the hovered option, reusing existing UI patterns.
- `openspec/specs/scenario-orchestration/spec.md` — not modified; tooltip is a presentation addition, not orchestration logic.
