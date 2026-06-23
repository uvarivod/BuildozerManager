## Context

The log panel (`LogPanel`) is a Kivy `BoxLayout` defined in `src/screens/log_panel.py` and `src/kv/log_panel.kv`. It contains a `ScrollView` wrapping a readonly `TextInput` (`id: log_label`) that displays build output. The `TextInput` uses `readonly: True` and is sized with `height: max(self.minimum_height, log_scroll.height)` so it always fills or overflows the viewport.

Kivy's `TextInput` in readonly mode already maintains `cursor_index()`, `select_text()`, and internal `_selection_from` / `_selection_to` attributes. However, it does not support:
1. SHIFT+click range selection anchored to a prior click.

The fix does not need to alter any service, model, or persistence layer.

## Goals / Non-Goals

**Goals:**
- Implement SHIFT+click range selection between two arbitrary click positions in the log `TextInput`.
- Keep the existing mouse-drag selection intact for short selections inside the viewport.
- Work with the existing readonly mode — no write operations are introduced.

**Non-Goals:**
- Keyboard selection extensions (SHIFT+arrow, SHIFT+END, etc.) — Kivy handles these natively.
- Touch-screen drag selection — this is a desktop-only feature.
- Changing auto-scroll, coloring, save, or clear behaviour.
- Supporting selection across multiple widgets.

## Decisions

1. **`SelectableLogInput` subclass of `TextInput`.**
   Create `SelectableLogInput` in `log_panel.py`. This keeps the change self-contained. The KV file replaces the inline `TextInput` with `SelectableLogInput`.

2. **Anchor index stored as an instance variable `_sel_anchor`.**
   On every plain LMB `touch_down`, record the cursor index at the touch point as `_sel_anchor`. On SHIFT+LMB `touch_down`, call `select_text(_sel_anchor, current_index)` and consume the event so the default single-click deselect does not fire.

3. **Cursor-index-from-position via `get_cursor_from_xy()`.**
   Kivy's `TextInput` exposes `get_cursor_from_xy(x, y)` which returns `(col, row)`. The flat character index is obtained with `cursor_index()` after setting `cursor = (col, row)` momentarily, or by accumulating line lengths. Use the internal `_cursor_offset_from_col_row(col, row)` helper or the public `cursor_index` property after assigning `cursor`.

   > **Safer approach**: convert touch position to widget-local coords, call `_get_line_from_cursor` internals, or use the documented approach: assign `self.cursor = self.get_cursor_from_xy(lx, ly)` and then read `self.cursor_index()`.

4. **SHIFT detection via `Window.modifiers`.**
   Check `'shift' in Window.modifiers` in `on_touch_down`. If shift is held, we temporarily disable Kivy's double-tap handling (which would otherwise select a word), call `select_text` with the anchor and the current index, and return True to consume the event. Otherwise we proceed normally and record the anchor.

5. **No KV changes other than the class name.**
   The `.kv` file changes only the widget class from `TextInput` to `SelectableLogInput`. All existing properties (`readonly`, `font_name`, `font_size`, `size_hint_y`, `height`, `padding`, `background_color`, `foreground_color`) remain unchanged.

## Risks / Trade-offs

- **`get_cursor_from_xy` accuracy**: Kivy's internal method expects local (widget) coordinates. If the `ScrollView` has scrolled, the widget's `y` is negative (it overflows upward). We must transform touch screen-coords to widget-local coords using `self.to_local(touch.x, touch.y)`. This is standard Kivy practice.
- **Touch grab outside widget bounds**: Kivy `on_touch_move` is only called if the widget grabbed the touch (via `touch.grab(self)` in `on_touch_down`). We must explicitly grab the touch.
- **Readonly mode strips some touch handling**: Kivy's `TextInput.on_touch_down` returns early in some readonly paths. Call `super()` carefully; if super consumes and deselects, call `select_text` after super returns.
