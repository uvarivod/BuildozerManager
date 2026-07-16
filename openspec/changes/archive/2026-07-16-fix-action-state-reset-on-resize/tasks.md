## 1. Snapshot and Restore Action States

- [x] 1.1 In `_build_action_chain()`, snapshot `action_state` (and `patch_states` for PatchCard) from existing `_action_cards` before `_clear_action_chain()`
- [x] 1.2 After creating new cards, restore saved states by index using `card.set_state()` for ActionCard and restoring `patch_states` dict for PatchCard

## 2. Reduce Redundant Resize Bindings

- [x] 2.1 Audit the three Window event bindings (`on_resize`, `size`, `system_size`) in `ActionsScreen.on_pre_enter()` and remove duplicates so only one resize event triggers a rebuild
