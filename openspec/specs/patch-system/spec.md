# Patch System

## Purpose

Define and apply Python-based patches to the Buildozer `.buildozer` directory after source copy, with per-profile patch selection and failure isolation.

## Requirements

### Requirement: User can define patches as Python callables
The system SHALL allow defining patches as decorated Python functions that modify files in the `.buildozer` directory.

#### Scenario: Register a patch via decorator
- **WHEN** a function is decorated with `@register_patch(name="disable_ads", description="Disables ad SDK init")`
- **THEN** the patch appears in the profile's patch list with that name and description

### Requirement: Patches receive the .buildozer directory path
The system SHALL pass the Path to the `.buildozer` directory inside WSL to each patch function when applied.

#### Scenario: Patch modifies a file
- **WHEN** a patch function receives the .buildozer Path
- **THEN** it can read, modify, and write files inside that directory

### Requirement: User can select which patches to apply per profile
Each profile SHALL maintain a list of enabled patches that are applied during Patch action execution.

#### Scenario: Enable patches for profile
- **WHEN** the user checks patches in the profile editor
- **THEN** those patches are associated with the profile and applied during Patch action

### Requirement: Patches are applied after source copy
The system SHALL apply all enabled patches to the `.buildozer` directory in WSL after source has been copied.

#### Scenario: Apply patches after build copy
- **WHEN** a scenario executes "Build and Patch"
- **THEN** after Build completes, each enabled patch function is called sequentially with the .buildozer path
- **THEN** each patch result (success/failure) is logged

### Requirement: Patch failure does not block other patches
If one patch fails, the system SHALL log the error and continue with the next patch.

#### Scenario: Partial patch failure
- **WHEN** patch "A" succeeds and patch "B" raises an exception
- **THEN** the system logs patch "A" as success and patch "B" as failed
- **THEN** the Patch action continues to subsequent patches
- **THEN** the overall Patch action status is "Partial Success"
