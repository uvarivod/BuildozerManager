## 1. Create Dialog Helper Module

- [x] 1.1 Create `src/screens/dialog_helper.py` with color and size constants
- [x] 1.2 Implement `show_info_dialog(title, message)` function
- [x] 1.3 Implement `show_confirm_dialog(title, message, on_confirm, confirm_text="Delete")` function
- [x] 1.4 Implement `show_error_dialog(title, message)` function
- [x] 1.5 Implement `show_success_dialog(title, message)` function
- [x] 1.6 Implement `show_form_dialog(title, fields, on_save, save_text="Save")` function
- [x] 1.7 Implement `show_toast(message, duration=2)` function
- [x] 1.8 Add keyboard support (Escape to dismiss, Enter to confirm) to all dialogs
- [x] 1.9 Set `auto_dismiss=False` on confirm, error, and form dialogs

## 2. Migrate Help Popups

- [x] 2.1 Update `src/screens/help_popup.py` to use `show_info_dialog()` from dialog_helper
- [x] 2.2 Verify all 5 screens still display help popups correctly

## 3. Migrate Profile Editor Dialogs

- [x] 3.1 Update `profile_editor_screen.py:_show_error()` to use `show_error_dialog()`
- [x] 3.2 Update `profile_editor_screen.py:_check_adb()` error case to use `show_error_dialog()`
- [x] 3.3 Update `profile_editor_screen.py:_prompt_use_spec()` to use `show_confirm_dialog()`
- [x] 3.4 Update `profile_editor_screen.py:_check_adb()` success case to use `show_info_dialog()`

## 4. Migrate Settings Screen Dialogs

- [x] 4.1 Update `settings_screen.py:_show_error()` to use `show_error_dialog()`
- [x] 4.2 Update `settings_screen.py:_show_success()` to use `show_toast()` for transient notification

## 5. Migrate Log Panel Dialogs

- [x] 5.1 Update `log_panel.py:save_log()` dialog to use `show_form_dialog()` or `show_info_dialog()`

## 6. Migrate Actions Screen Dialogs

- [x] 6.1 Update `actions_screen.py:delete_profile()` confirmation to use `show_confirm_dialog()`
- [x] 6.2 Update `actions_screen.py:on_scenario_selected()` missing actions warning to use `show_error_dialog()`

## 7. Migrate Scenario Editor Dialogs

- [x] 7.1 Update `scenario_editor_screen.py:on_back()` unsaved changes dialog to use `show_confirm_dialog()`
- [x] 7.2 Update `scenario_editor_screen.py:on_delete()` confirmation to use `show_confirm_dialog()`
- [x] 7.3 Update `scenario_editor_screen.py:_show_edit_dialog()` delete confirmation to use `show_confirm_dialog()`
- [x] 7.4 Update `scenario_editor_screen.py:_show_edit_dialog()` duplicate name error to use `show_error_dialog()`
- [x] 7.5 Update `scenario_editor_screen.py:_show_create_action_dialog()` duplicate name error to use `show_error_dialog()`
- [x] 7.6 Update `scenario_editor_screen.py:on_save()` duplicate scenario name error to use `show_error_dialog()`
- [x] 7.7 Update `scenario_editor_screen.py:on_save()` missing actions warning to use `show_error_dialog()`
- [x] 7.8 Update `scenario_editor_screen.py:_confirm_delete_action()` action-in-use warning to use `show_error_dialog()`

## 8. Remove Inline Popup Imports

- [x] 8.1 Remove duplicate `from kivy.uix.popup import Popup` imports from all migrated screen files
- [x] 8.2 Verify no screen files still construct popups inline (except file_chooser_helper.py which has unique UI)
