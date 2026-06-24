## ADDED Requirements

### Requirement: Profile Editor shows patch multi-selector
The Profile Editor screen SHALL display a multi-select control listing all registered patches from `PatchRegistry.list_patches()`.
The user SHALL be able to check/uncheck individual patches to associate them with the profile.
The selected patches SHALL be persisted in `profile.patches` and round-trip correctly through save/load.

#### Scenario: Profile Editor shows all registered patches
- **WHEN** user opens the Profile Editor for a new or existing profile
- **THEN** the patch selector SHALL display all patches from the registry with checkboxes

#### Scenario: User selects patches and saves profile
- **WHEN** user checks 2 patches and saves the profile
- **THEN** `profile.patches` SHALL contain the names of those 2 patches

#### Scenario: Loading a profile restores previous patch selection
- **WHEN** user loads a profile that previously had patches A and B selected
- **THEN** checkboxes for A and B SHALL be checked in the patch selector

### Requirement: Patch list comes from PatchRegistry
The multi-selector SHALL dynamically populate its list from `PatchRegistry.list_patches()` at render time.
No hardcoded patch list SHALL exist in the UI layer.

#### Scenario: Removing a registered patch
- **WHEN** a patch is unregistered from PatchRegistry
- **THEN** the corresponding checkbox SHALL disappear from the selector on next render
