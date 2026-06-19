## 1. WSL Service — Build Prerequisites & Output Parsing

- [x] 1.1 Add `find_spec_in_wsl(profile) -> bool` method that checks if `buildozer.spec` exists in the WSL build directory
- [x] 1.2 Update `exec_buildozer` to prepend `export PATH=$PATH:~/.local/bin/;` to the buildozer command (use `bash -c` wrapper)
- [x] 1.3 Add buildozer output parsing in `exec_buildozer`: classify lines as info/warn/debug based on content patterns

## 2. Action Runner — RUNNING State, Thread Safety, .buildozer Warning

- [x] 2.1 Add `on_state_change` callback parameter to `run_action()`; emit `ActionState.RUNNING` at start of each action
- [x] 2.2 Fix thread-unsafe exclusion list mutation: operate on a copy of `profile.delete_exclusions` instead of in-place append
- [x] 2.3 Add `.buildozer` protection check: before cleaning, check if `.buildozer` is in `profile.delete_exclusions`; if missing, return special signal to trigger UI popup
- [x] 2.4 Integrate `find_spec_in_wsl` check in build pipeline — log warning if spec missing, continue build

## 3. UI — Actions Screen & Log Panel

- [x] 3.1 Wire `on_state_change` callback in `ActionsScreen.run_single_action()` to update `status_label` on RUNNING state
- [x] 3.2 Add `.buildozer` missing popup in `ActionsScreen`: "Continue", "Add to exclusions and continue", "Stop" — pass user choice back to action runner
- [x] 3.3 Add `reset_timer()` and `stop_timer()` methods to `LogPanel`
- [x] 3.4 Call `reset_timer()` before spawning action thread and `stop_timer()` in `_on_action_done()`

## 4. Verify

- [ ] 4.1 Run the app and test Build action: verify RUNNING state shows in UI
- [ ] 4.2 Verify duration timer resets on each action start and stops on completion
- [ ] 4.3 Verify buildozer output is parsed with step names visible
- [ ] 4.4 Verify `.buildozer` missing popup appears and all 3 options work
- [ ] 4.5 Verify `buildozer.spec` missing warning is logged
- [ ] 4.6 Verify PATH export works (buildozer found in WSL)
