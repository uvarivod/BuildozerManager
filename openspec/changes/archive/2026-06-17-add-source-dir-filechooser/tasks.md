## 1. KV Layout

- [x] 1.1 Replace standalone Source Directory TextInput with a horizontal BoxLayout containing the TextInput and a "Browse" button

## 2. Python Logic

- [x] 2.1 Add `_browse_sourcedir()` method to ProfileEditorScreen that opens a Kivy FileChooserIconView in a Popup with `dirselect=True`
- [x] 2.2 Pre-populate the FileChooser path with the current text input value
- [x] 2.3 On directory selection, populate the text input and dismiss the popup

## 3. Verify

- [x] 3.1 Browse button opens directory chooser dialog
- [x] 3.2 Selecting a directory fills the Source Directory field
- [x] 3.3 Manual typing and copy-paste still work on the field
- [x] 3.4 Auto-detect buildozer.spec fires when path changes via Browse
