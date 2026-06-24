## ADDED Requirements

### Requirement: patch_activity_theme patch exists
The system SHALL register a patch named `patch_activity_theme` via `@register_patch`.
This patch SHALL add or update `android:theme="@style/AppTheme.NoEdgeToEdge"` on the `<activity>` tag that contains `android:name="{{args.android_entrypoint}}"` in each AndroidManifest.tmpl.xml file.
The patch SHALL use regex-based detection: find the target activity by name attribute, log current theme value, and modify only that activity.
If the theme is already `@style/AppTheme.NoEdgeToEdge`, the file SHALL NOT be modified.

#### Scenario: Apply patch to template with different theme
- **WHEN** `patch_activity_theme` runs on a template where the target activity has a different theme
- **THEN** the theme SHALL be changed to `@style/AppTheme.NoEdgeToEdge`

#### Scenario: Apply patch to template with no theme attribute
- **WHEN** `patch_activity_theme` runs on a template where the target activity has no `android:theme`
- **THEN** the theme attribute SHALL be added with value `@style/AppTheme.NoEdgeToEdge`

#### Scenario: Skip when already correct
- **WHEN** `patch_activity_theme` runs on a template where the target activity already has `android:theme="@style/AppTheme.NoEdgeToEdge"`
- **THEN** the file SHALL NOT be modified

### Requirement: Patch applies to all 3 template paths
The patch SHALL iterate all 3 AndroidManifest template paths, same as `patch_back_functionality`.

#### Scenario: Patch iterates all three paths
- **WHEN** `patch_activity_theme` runs
- **THEN** it SHALL attempt to patch all 3 template file paths and log success/failure for each

### Requirement: themes.xml is ensured in build dist
The patch SHALL ensure `themes.xml` (which defines `AppTheme.NoEdgeToEdge`) exists in the buildozer dist output before patching the manifest templates.
The expected destination path SHALL be:
`{wsldir}/.buildozer/android/platform/build-{archs_joined}/dists/{package_name}/res/values/themes.xml`
If the file already exists at the destination, the patch SHALL log a success message and skip copying.
If the file is missing, the patch SHALL log a warning and copy from the project's `android_res/values/themes.xml` (relative to profile.sourcedir).
If the source `android_res/values/themes.xml` is also missing, the patch SHALL log a failure and abort.

#### Scenario: themes.xml exists at destination
- **WHEN** `patch_activity_theme` runs and `themes.xml` already exists at the expected dist path
- **THEN** the patch SHALL log "[SUCCESS]" and skip copying

#### Scenario: themes.xml missing, copied from project source
- **WHEN** `patch_activity_theme` runs and `themes.xml` is missing at the destination but exists at `{sourcedir}/android_res/values/themes.xml`
- **THEN** the patch SHALL log a warning about the missing file
- **AND** copy the project's `android_res/values/themes.xml` to the destination

#### Scenario: themes.xml missing in both locations
- **WHEN** `patch_activity_theme` runs and `themes.xml` is missing at both destination and project source
- **THEN** the patch SHALL log a failure and abort the activity theme patching
