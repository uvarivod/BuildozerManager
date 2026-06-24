## ADDED Requirements

### Requirement: patch_back_functionality patch exists
The system SHALL register a patch named `patch_back_functionality` via `@register_patch`.
This patch SHALL add or update `android:enableOnBackInvokedCallback="false"` on the first `<application>` tag in each AndroidManifest.tmpl.xml file across all 3 buildozer template paths.
The patch SHALL use the same regex-based approach as the reference script: find all `<application>` tags, log their current value, and modify only the first one.
If the attribute already exists and is `"false"`, the file SHALL NOT be modified.

#### Scenario: Apply patch to template with no existing attribute
- **WHEN** `patch_back_functionality` runs on a template without `android:enableOnBackInvokedCallback`
- **THEN** the attribute SHALL be added to the first `<application>` tag with value `"false"`

#### Scenario: Apply patch to template with existing true attribute
- **WHEN** `patch_back_functionality` runs on a template where `android:enableOnBackInvokedCallback="true"`
- **THEN** the value SHALL be changed to `"false"`

#### Scenario: Skip when already correct
- **WHEN** `patch_back_functionality` runs on a template where `android:enableOnBackInvokedCallback="false"`
- **THEN** the file SHALL NOT be modified

### Requirement: Patch applies to all 3 template paths
The patch SHALL iterate all 3 AndroidManifest template paths derived from buildozer infrastructure:
1. `python-for-android/bootstraps/_sdl_common/build/templates/AndroidManifest.tmpl.xml`
2. `build-{archs}/build/bootstrap_builds/sdl2/templates/AndroidManifest.tmpl.xml`
3. `build-{archs}/dists/{package}/templates/AndroidManifest.tmpl.xml`

#### Scenario: Patch iterates all three paths
- **WHEN** `patch_back_functionality` runs
- **THEN** it SHALL attempt to patch all 3 template file paths and log success/failure for each
