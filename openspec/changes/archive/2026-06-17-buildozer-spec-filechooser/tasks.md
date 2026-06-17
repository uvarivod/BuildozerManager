## 1. Extract FileChooser helper

- [x] 1.1 Create `src/screens/file_chooser_helper.py` with a `FileChooserHelper` class that encapsulates the directory chooser popup (toggle view, path label, Choose/Cancel buttons)
- [x] 1.2 Refactor `ProfileEditorScreen._browse_sourcedir` to use `FileChooserHelper.show_dir_chooser` instead of inline popup code — verify no functional regression

## 2. Add buildozer.spec file chooser

- [x] 2.1 Add `FileChooserHelper.show_file_chooser` method that filters to a specific filename (e.g., `buildozer.spec`) rather than directories
- [x] 2.2 Add `_browse_spec_path` method in `ProfileEditorScreen` that calls `show_file_chooser` and sets `spec_path_input.text`
- [x] 2.3 Add Browse button next to `spec_path_input` in `profile_editor_screen.kv` that calls `root._browse_spec_path()`

## 3. Add confirmation popup for auto-detect

- [x] 3.1 After `show_dir_chooser` confirms, check if `Path(chosen_path) / "buildozer.spec"` exists
- [x] 3.2 If found, show a confirmation popup with "We found buildozer.spec in the folder you chose. Do you want to use it?" and Yes/No buttons
- [x] 3.3 On Yes, set `spec_path_input.text` to the full path; on No, dismiss
- [x] 3.4 Run `python main.py` and verify: directory browse works, spec browse works, confirmation popup appears
