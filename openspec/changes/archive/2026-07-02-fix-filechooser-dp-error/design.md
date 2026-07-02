## Context

The `file_chooser_helper.py` uses `dp()` (from `kivy.metrics`) in Python code to convert dp values to pixels for layout padding, but the function is not imported. The KV files reference `dp` via string suffixes (e.g., `height='44dp'`) which Kivy parses natively, but the `dp()` function call requires an explicit Python import.

## Goals / Non-Goals

**Goals:**
- Fix the `NameError: name 'dp' is not defined` crash when opening any file/dir chooser
- Ensure all Python files that call `dp()` have the proper import

**Non-Goals:**
- No changes to Kivy KV files (they use the string suffix approach and work correctly)
- No conversion of existing pixel values to dp (they already use dp strings)
- No changes to any other Python files unless they have the same missing import

## Decisions

- **Add `from kivy.metrics import dp` import** — The simplest and most correct fix for the `NameError`. The `dp` function is already part of Kivy's public API and was being called; only the import was missing.
- **Keep all existing size strings as-is** — KV-style `'44dp'` strings work in Python widget constructors via Kivy's property system. The `dp()` function is only needed when computing values dynamically (e.g., `padding=[dp(0), dp(6)]` where the list elements are individual numeric values).

## Risks / Trade-offs

- **[Low risk] Collision with `dp` variable name** — No variable named `dp` exists in this file, so no shadowing concern.
