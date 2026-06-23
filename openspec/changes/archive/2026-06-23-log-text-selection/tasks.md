## 1. Create `SelectableLogInput` in `log_panel.py`

- [x] 1.1 Add `SelectableLogInput(TextInput)` class above `LogPanel` in `src/screens/log_panel.py`
- [x] 1.2 Add instance variables in `__init__`: `_sel_anchor: int | None = None`
- [x] 1.3 Override `on_touch_down(self, touch)`:
  - If touch does not collide with self → return `super().on_touch_down(touch)`
  - If `'shift' in Window.modifiers`:
    - Disable Kivy's double-tap word selection temporarily to prevent hijacking
    - Call `super().on_touch_down(touch)` to update cursor/focus
    - Call `self.select_text(anchor, current_index)` using the `_sel_anchor` (or 0 if unset)
    - Return `True` (consume)
  - Else (plain click):
    - Call `super().on_touch_down(touch)` to let native TextInput handle normal selection
    - Record `self._sel_anchor = self.cursor_index()`
    - Return `res`

## 2. Update `log_panel.kv` to use `SelectableLogInput`

- [x] 2.1 In `src/kv/log_panel.kv`, replace `TextInput:` with `SelectableLogInput:` inside the `ScrollView`
- [x] 2.2 Keep all existing properties unchanged (`id`, `readonly`, `font_name`, `font_size`, `size_hint_y`, `height`, `padding`, `background_color`, `foreground_color`)
- [x] 2.3 Ensure `SelectableLogInput` is importable in the KV context — add `#:import SelectableLogInput src.screens.log_panel` at the top of the KV file, or confirm it is registered via the `LogPanel` module load

## 3. Verification

- [x] 3.1 Launch the app, trigger a build to populate the log with 50+ lines
- [x] 3.2 **Plain drag selection**: click and drag within visible viewport — confirm native text selection still works
- [x] 3.3 **SHIFT+click selection**: click at line 10 (anchor), then SHIFT+click at line 80 — confirm all text between them is selected
- [x] 3.4 **SHIFT+click resets on plain click**: plain-click anywhere → SHIFT+click elsewhere — confirm only the new range is selected
- [x] 3.5 **Copy works**: after any selection method, press Ctrl+C and paste into an editor — confirm correct text is copied
- [x] 3.6 **Auto-scroll not broken**: while no drag is in progress, new log lines still auto-scroll to the bottom as before
