## Why

The current patch system supports a flat list of patches applied in bulk with no per-patch control. Users need the ability to run individual patches selectively, see patch-specific UI in the action chain, and configure per-profile patch selection. Additionally, two critical Android patches are needed: restoring Back button functionality for Android 16+ and disabling EdgeToEdge display mode.

## What Changes

- Add `PatchCard` widget variant in Actions screen with individual run buttons per patch
- Make PATCH action cards wider with patch-name buttons on the right side (scrollable if needed)
- Add patch multi-selector in Profile Editor (dropdown/multichoose)
- Store selected patches per profile in `profile.patches`
- When running a scenario with PATCH action, all selected patches run sequentially
- Each patch button on the card can trigger its own patch independently
- Implement `patch_back_functionality` patch for Android Back compatibility
- Implement `patch_activity_theme` patch to disable EdgeToEdge
- Patch service must apply patches to the 3 AndroidManifest template paths defined in buildozer infrastructure

## Capabilities

### New Capabilities
- `patch-selector-profile`: Multi-select patch chooser in Profile Editor screen
- `patch-card-ui`: PatchCard widget with per-patch run buttons in Actions screen
- `patch-back-functionality`: Android Back button compatibility patch for Android 16+
- `patch-disable-edge-to-edge`: Disable EdgeToEdge theme patch

### Modified Capabilities
- `patch-execution`: PATCH action now supports running selected patches sequentially on scenario run; individual patches can be triggered independently from the card UI
- `profile-patches`: Profile model's `patches` field becomes the source of truth for which patches are available per profile, wired into the patch selector and patch card UI

## Impact

- `src/screens/actions_screen.py` — new PatchCard handling, per-patch execution
- `src/screens/action_card.py` — new PatchCard widget class
- `src/screens/profile_editor_screen.py` — multi-select patch control
- `src/kv/actions_screen.kv` — PatchCard layout changes
- `src/kv/action_card.kv` — PatchCard KV template
- `src/kv/profile_editor_screen.kv` — patch selector UI
- `src/services/patch_service.py` — support single-patch execution
- `src/services/action_runner.py` — wire per-patch execution
- `src/patches/example_patches.py` — add two new patches (or new file `android_patches.py`)
- `src/models/profile.py` — patches field already exists, may need enhancement
- `src/patches/__init__.py` — register new patches
