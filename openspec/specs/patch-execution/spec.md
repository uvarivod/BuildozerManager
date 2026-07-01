# Patch Execution

## Purpose

Define how PATCH actions execute patches sequentially during scenario runs and provide individual patch execution via ActionRunner.

## Requirements

### Requirement: Scenario PATCH action runs all selected patches
The PATCH action in a scenario SHALL execute all patches associated with the current profile (`profile.patches`) sequentially.
Each patch SHALL be applied via `PatchService.apply_patches([patch_name], ...)`.
If `profile.patches` is empty, the PATCH action SHALL be skipped with a log message.
The overall PATCH action result (success/failure) SHALL be reported in the scenario run results.

#### Scenario: PATCH action in scenario with 3 patches
- **WHEN** a scenario with a PATCH action runs against a profile with 3 patches selected
- **THEN** all 3 patches SHALL execute sequentially
- **AND** the scenario run SHALL log each patch start/end with success/failure
- **AND** the overall PATCH action state is SUCCESS if all patches succeed, FAILED if any patch fails

#### Scenario: PATCH action with no patches selected
- **WHEN** a scenario with a PATCH action runs against a profile with an empty patches list
- **THEN** the action SHALL be skipped and logged as "No patches selected for this profile"

### Requirement: Individual patch execution via ActionRunner
The system SHALL expose `ActionRunner.run_single_patch(patch_name, profile, log_callback)` to execute a single patch independently.
This SHALL be used by PatchCard buttons and SHALL follow the same threading/cancellation pattern as other actions.

#### Scenario: Running a single patch
- **WHEN** `run_single_patch` is called with a valid patch name
- **THEN** the patch SHALL execute via `PatchService.apply_patches`
- **AND** the result SHALL be returned with success/failure status
