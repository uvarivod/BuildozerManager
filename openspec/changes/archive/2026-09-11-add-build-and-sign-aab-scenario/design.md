## Context

`ScenarioService.get_predefined_scenarios()` currently returns exactly two built-in scenarios ("Full Clean build" and "Rebuild"). The app now has `BUILD_AAB`, `SIGN_APK`, and `PULL_AAB` actions for the release pipeline, but no out-of-the-box scenario composes them. Users must recreate `BUILD_AAB → SIGN_APK → PULL_AAB` manually. The scenario list and runner already support arbitrary actions, stop-on-failure, and skip-mask — adding a third predefined entry requires no infrastructure change.

## Goals / Non-Goals

**Goals:**
- Expose the common release flow as a selectable predefined scenario `Build and Sign AAB` (`BUILD_AAB → SIGN_APK → PULL_AAB`) with `stop_on_failure=true`.

**Non-Goals:**
- No runner or editor changes; existing orchestration handles the new sequence.
- No persistence migration; predefined scenarios are in-memory.
- No modification of the two existing predefined scenarios.

## Decisions

**1. Extend `get_predefined_scenarios()` with a third `Scenario` literal.**
Reuses the same pattern as the existing two entries. Keeps the change local to one file and preserves in-memory read-only semantics. Alternative of adding a persisted user scenario would require store changes and is not desired.

**2. Sequence `BUILD_AAB → SIGN_APK → PULL_AAB` with `stop_on_failure=true`.**
Ensures signing only runs after a successful AAB build, and pulling only after a successful sign. Pulling the final signed artifact in the same scenario matches the user's goal of obtaining the uploadable file in `sourcedir/bin/`. Order follows the user's supplied JSON exactly.

**3. Update the spec from "precisely two" to "three" predefined scenarios.**
Keeps the spec authoritative. All other requirements (run orchestration, skip-mask, read-only editor for predefined scenarios, coexistence with user scenarios) remain unchanged.

## Risks / Trade-offs

- [Any of the three steps fails → scenario stops due to `stop_on_failure`] → Mitigation: consistent with existing scenarios; user sees per-action status and log.
- [User without keystore/certificate will fail at SIGN_APK] → Mitigation: existing validation for `SIGN_APK` reports missing fields; no new failure mode.
- [Spec strictly asserting count could break tests asserting exactly two] → Mitigation: anticipated; tests for `scenario-orchestration` will need update to expect three.

## Migration Plan

No data migration. Existing user scenarios unchanged. Predefined scenarios are not persisted. Rollback: remove the third Scenario literal.

## Open Questions

- None.
