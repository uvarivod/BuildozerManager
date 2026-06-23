## Why

Selecting large blocks of log text is nearly impossible today. When the user click-drags to select text and the cursor moves past the visible area of the `ScrollView`, the selection is lost. There is also no SHIFT+click range-select to anchor a start point and extend the selection to an arbitrary end point. Because buildozer produces long, multi-hundred-line outputs, users need to copy large log sections daily for debugging — making this a high-frequency pain point.

## What Changes

- **SHIFT+click selection**: A single LMB click places a selection anchor. A subsequent SHIFT+LMB click on any other visible line selects all text between the anchor and the new click point, regardless of how far apart the two points are vertically.
- Both features work entirely within the existing readonly `TextInput` inside the `ScrollView` — no new widgets required.

## Capabilities

### New Capabilities
- `log-text-selection`: Extending text selection in a readonly Kivy `TextInput` using SHIFT+click range-select.

### Modified Capabilities
- `log-viewer`: The log panel gains enhanced selection behaviour. No changes to logging, streaming, auto-scroll, save, or clear.

## Impact

- `src/screens/log_panel.py` — subclass or extend `TextInput` with custom `on_touch_down` handler; manage anchor index and selection state.
- `src/kv/log_panel.kv` — replace the inline `TextInput` with the new `SelectableLogInput` class; no other layout changes required.
- No API changes, no new dependencies.
