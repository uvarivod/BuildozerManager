## Why

Users who build release AABs must currently assemble the `BUILD_AAB → SIGN_APK → PULL_AAB` chain manually in the Scenario Editor. Offering this common release flow as a built-in predefined scenario makes it one-click: build the AAB, sign it with the configured keystore, and copy the signed artifact to `sourcedir/bin/` for upload to Google Play.

## What Changes

- Add a third predefined scenario **"Build and Sign AAB"** to `ScenarioService.get_predefined_scenarios()`:
  - `name`: `Build and Sign AAB`
  - `description`: `Build AAB, signs and copy to src/bin file which you can send to Google Play.`
  - `action_sequence`: `[BUILD_AAB, SIGN_APK, PULL_AAB]`
  - `stop_on_failure`: `true`
  - `is_predefined`: `true`
- No changes to the scenario runner, editor, or persistence — the new scenario is read-only and runs like the existing two.

## Capabilities

### New Capabilities

### Modified Capabilities
- `scenario-orchestration`: Predefined scenario set grows from two to three to include the new release flow. The requirement that precisely two built-ins exist is updated.

## Impact

- `src/services/scenario_service.py` — add third `Scenario` entry in `get_predefined_scenarios()`
- `openspec/specs/scenario-orchestration/spec.md` — delta spec updating the built-in scenario count and documenting the new scenario
