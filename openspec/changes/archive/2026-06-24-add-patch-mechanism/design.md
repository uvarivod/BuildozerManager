## Context

BuildozerManager uses a flat patch registry (`PatchRegistry`) where patches are registered by name and applied in bulk. Profiles have a `patches: list[str]` field but there is no per-patch UI control in the Actions screen — the PATCH action runs all selected patches together. The Android patches needed (Back functionality for Android 16+, EdgeToEdge disable) require modifying AndroidManifest.tmpl.xml files across 3 buildozer template paths. The reference Python script demonstrates the exact regex-based patching logic.

## Goals / Non-Goals

**Goals:**
- PatchCard widget with individual patch run buttons in the Actions screen
- Per-profile patch selection via multi-chooser in Profile Editor
- Scenario-run PATCH action executes all selected patches sequentially
- Individual patches can be triggered independently from PatchCard buttons
- Implement `patch_back_functionality` (android:enableOnBackInvokedCallback="false")
- Implement `patch_activity_theme` (android:theme="@style/AppTheme.NoEdgeToEdge")
- Patches apply to all 3 AndroidManifest template paths

**Non-Goals:**
- Real-time patch status streaming (simple log output is sufficient)
- UI for creating custom patches at runtime
- Patch versioning or rollback

## Decisions

- **Decision: PatchCard as a subclass of ActionCard** — The existing ActionCard is a BoxLayout with action_name, description, state colors. PatchCard extends it, adding a right-side ScrollView with per-patch buttons. Reuses all existing state rendering (PENDING/RUNNING/SUCCESS/FAILED colors) while adding patch-specific UI.
- **Decision: Patch registry lookup determines available buttons** — Available patches for a profile are stored in `profile.patches`. The PatchCard queries `PatchRegistry.list_patches()` filtered by `profile.patches` to render buttons. This avoids duplicating patch metadata.
- **Decision: Individual patch execution reuses ActionRunner threading** — Each patch button click spawns the same threading pattern as other actions. A new method `run_single_patch(patch_name)` in ActionRunner calls `PatchService.apply_patches([patch_name], ...)`.
- **Decision: Multi-select in Profile Editor uses a RecycleView of CheckBoxes** — Kivy lacks a native multiselect dropdown. A RecycleView listing all registered patches as labeled checkboxes, matching the existing UI patterns in scenario_builder_screen.kv.
- **Decision: Android patches implemented as separate registered functions** — Each patch is a standalone function decorated with `@register_patch`. They use `patch_build`-like logic to iterate the 3 template paths. The user can choose either, both, or neither via profile settings.
- **Decision: Patch functions accept `buildozer_path: Path` (existing contract)** — The PatchService already passes Path objects. The new patches receive the .buildozer path and construct the 3 template file paths dynamically, reusing the `parse_buildozer_spec` pattern from the reference.

## Risks / Trade-offs

- [Risk] Template paths may differ across buildozer versions → Use glob fallback if exact paths not found
- [Risk] Per-patch UI buttons may overflow card height → ScrollView handles this naturally
- [Risk] Running individual patches outside a scenario run may leave partial state → Document that patches are idempotent (each checks current state before modifying)
- [Risk] Kivy RecycleView for multi-select may feel clunky → Acceptable for this use case; alternative would be a custom dropdown widget
