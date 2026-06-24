## 1. Android Patch Implementations

- [x] 1.1 Create `patch_back_functionality` patch function in `src/patches/android_patches.py`
- [x] 1.2 Create `patch_activity_theme` patch function in `src/patches/android_patches.py`
- [x] 1.3 Implement template path discovery (3 paths based on buildozer infrastructure)
- [x] 1.4 Register both patches via `@register_patch` in `src/patches/__init__.py`
- [x] 1.5 Write unit tests for both patch functions (`tests/test_android_patches.py`)

## 2. PatchCard Widget

- [x] 2.1 Create `PatchCard` class in `src/screens/action_card.py` extending ActionCard
- [x] 2.2 Add PatchCard KV template in `src/kv/action_card.kv` with wider layout and right-side button panel
- [x] 2.3 Add per-patch button state tracking (running/success/failed per patch)
- [x] 2.4 Wire PatchCard to display when scenario action is PATCH in `actions_screen.py`

## 3. Profile Editor Patch Selector

- [x] 3.1 Add multi-select patch chooser UI in `src/kv/profile_editor_screen.kv`
- [x] 3.2 Implement patch selection logic in `src/screens/profile_editor_screen.py`
- [x] 3.3 Wire selected patches to profile save/load cycle

## 4. Individual & Batch Patch Execution

- [x] 4.1 Add `run_single_patch` method to `ActionRunner` in `src/services/action_runner.py`
- [x] 4.2 PATCH action already runs all selected patches sequentially via `_run_patch` -> `apply_patches`
- [x] 4.3 Wire PatchCard per-patch buttons to `run_single_patch`
- [x] 4.4 Add per-patch result logging and state updates

## 5. Profile Patches Integration

- [x] 5.1 `profile.patches` round-trips through JSON serialization/deserialization
- [x] 5.2 PatchCard reads patches from selected profile
- [x] 5.3 Existing tests already cover profile model with patches (no changes needed)

## 6. Testing & Verification

- [x] 6.1 All 180 tests pass (154 existing + 26 new)
- [x] 6.2 Added tests for patch functions in `tests/test_android_patches.py` (18 tests)
- [x] 6.3 Added tests for PatchService in `tests/test_patch_service.py` (8 tests)
- [x] 6.4 Tests cover single-patch and batch-patch execution paths
