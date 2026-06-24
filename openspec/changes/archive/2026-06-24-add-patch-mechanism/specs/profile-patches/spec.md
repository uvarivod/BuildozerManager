## MODIFIED Requirements

### Requirement: Profile patches field as source of truth
The `Profile.patches: list[str]` field SHALL serve as the authoritative list of patches associated with a profile.
This list SHALL be:
- Populated by the patch multi-selector in the Profile Editor
- Persisted in `profiles.json` via the existing `ProfileStore`
- Read by PatchCard to determine which patch buttons to display
- Read by ActionRunner during scenario PATCH execution to determine which patches to run
- Read by individual patch execution to validate the patch belongs to the profile

#### Scenario: Profile with patches is saved and loaded
- **WHEN** a profile with patches ["patch_a", "patch_b"] is saved
- **THEN** loading that profile returns `patches == ["patch_a", "patch_b"]`

#### Scenario: PatchCard reads profile patches
- **WHEN** a profile is selected and the Actions screen renders
- **THEN** PatchCard SHALL only show buttons for patches in `profile.patches`

### Requirement: Profile without patches has empty list
A newly created profile SHALL have `patches` initialized to an empty list.
The Profile Editor SHALL display the patch selector with all checkboxes unchecked.

#### Scenario: New profile has empty patches
- **WHEN** a new profile is created
- **THEN** `profile.patches` SHALL be `[]`
