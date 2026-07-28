from unittest.mock import MagicMock

import pytest

from src.screens import dialog_helper


@pytest.fixture(autouse=True)
def _reset_kivy_mocks(kivy_mocks):
    """Reset all Kivy mocks before each test so call counts are clean."""
    for name, mock in kivy_mocks.items():
        if name in ("dp", "Screen", "BoxLayout", "DictProperty"):
            continue
        if hasattr(mock, "reset_mock"):
            mock.reset_mock()
    popup_instance = MagicMock(name="Popup_instance")
    kivy_mocks["Popup"].return_value = popup_instance


# ---------------------------------------------------------------------------
# show_info_dialog
# ---------------------------------------------------------------------------

class TestShowInfoDialog:
    def test_creates_popup_with_correct_title(self, kivy_mocks):
        dialog_helper.show_info_dialog("Test Title", "Test message")
        kivy_mocks["Popup"].assert_called_once()
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["title"] == "Test Title"

    def test_opens_popup(self, kivy_mocks):
        dialog_helper.show_info_dialog("T", "M")
        instance = kivy_mocks["Popup"].return_value
        instance.open.assert_called_once()

    def test_auto_dismiss_default_true(self, kivy_mocks):
        dialog_helper.show_info_dialog("T", "M")
        _, kwargs = kivy_mocks["Popup"].call_args
        assert "auto_dismiss" not in kwargs or kwargs["auto_dismiss"] is True

    def test_uses_scrollview(self, kivy_mocks):
        dialog_helper.show_info_dialog("T", "M")
        kivy_mocks["ScrollView"].assert_called_once()

    def test_label_created(self, kivy_mocks):
        dialog_helper.show_info_dialog("T", "M")
        kivy_mocks["Label"].assert_called_once()

    def test_ok_button_created(self, kivy_mocks):
        dialog_helper.show_info_dialog("T", "M")
        kivy_mocks["Button"].assert_called_once()
        _, kwargs = kivy_mocks["Button"].call_args
        assert kwargs.get("text") == "OK"

    def test_popup_size_hint(self, kivy_mocks):
        dialog_helper.show_info_dialog("T", "M")
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["size_hint"] == (0.5, 0.35)

    def test_returns_popup(self, kivy_mocks):
        result = dialog_helper.show_info_dialog("T", "M")
        assert result is kivy_mocks["Popup"].return_value

    def test_popup_content_has_scrollview(self, kivy_mocks):
        dialog_helper.show_info_dialog("T", "M")
        _, kwargs = kivy_mocks["Popup"].call_args
        content = kwargs.get("content")
        assert content is not None


# ---------------------------------------------------------------------------
# show_confirm_dialog
# ---------------------------------------------------------------------------

class TestShowConfirmDialog:
    def test_creates_popup_with_title(self, kivy_mocks):
        dialog_helper.show_confirm_dialog("Confirm", "Sure?", lambda: None)
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["title"] == "Confirm"

    def test_auto_dismiss_false(self, kivy_mocks):
        dialog_helper.show_confirm_dialog("C", "M", lambda: None)
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["auto_dismiss"] is False

    def test_opens_popup(self, kivy_mocks):
        dialog_helper.show_confirm_dialog("C", "M", lambda: None)
        instance = kivy_mocks["Popup"].return_value
        instance.open.assert_called_once()

    def test_confirm_callback_stored(self, kivy_mocks):
        callback = MagicMock()
        popup = dialog_helper.show_confirm_dialog("C", "M", callback)
        assert popup._confirm_callback is callback

    def test_custom_button_text(self, kivy_mocks):
        dialog_helper.show_confirm_dialog("C", "M", lambda: None, confirm_text="Yes", cancel_text="No")
        texts = []
        for call in kivy_mocks["Button"].call_args_list:
            texts.append(call[1].get("text"))
        assert "Yes" in texts
        assert "No" in texts

    def test_destructive_color_on_confirm(self, kivy_mocks):
        dialog_helper.show_confirm_dialog("C", "M", lambda: None)
        found_destructive = any(
            call[1].get("background_color") == dialog_helper.COLOR_BTN_DESTRUCTIVE
            for call in kivy_mocks["Button"].call_args_list
        )
        assert found_destructive

    def test_uses_scrollview(self, kivy_mocks):
        dialog_helper.show_confirm_dialog("C", "M", lambda: None)
        kivy_mocks["ScrollView"].assert_called_once()

    def test_returns_popup(self, kivy_mocks):
        result = dialog_helper.show_confirm_dialog("C", "M", lambda: None)
        assert result is kivy_mocks["Popup"].return_value


# ---------------------------------------------------------------------------
# show_error_dialog
# ---------------------------------------------------------------------------

class TestShowErrorDialog:
    def test_creates_popup_with_title(self, kivy_mocks):
        dialog_helper.show_error_dialog("Error", "Something broke")
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["title"] == "Error"

    def test_auto_dismiss_false(self, kivy_mocks):
        dialog_helper.show_error_dialog("E", "M")
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["auto_dismiss"] is False

    def test_opens_popup(self, kivy_mocks):
        dialog_helper.show_error_dialog("E", "M")
        instance = kivy_mocks["Popup"].return_value
        instance.open.assert_called_once()

    def test_uses_scrollview(self, kivy_mocks):
        dialog_helper.show_error_dialog("E", "M")
        kivy_mocks["ScrollView"].assert_called_once()

    def test_ok_button_created(self, kivy_mocks):
        dialog_helper.show_error_dialog("E", "M")
        ok_found = any(
            call[1].get("text") == "OK"
            for call in kivy_mocks["Button"].call_args_list
        )
        assert ok_found

    def test_returns_popup(self, kivy_mocks):
        result = dialog_helper.show_error_dialog("E", "M")
        assert result is kivy_mocks["Popup"].return_value


# ---------------------------------------------------------------------------
# show_success_dialog
# ---------------------------------------------------------------------------

class TestShowSuccessDialog:
    def test_creates_popup_with_title(self, kivy_mocks):
        dialog_helper.show_success_dialog("Success", "Done!")
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["title"] == "Success"

    def test_auto_dismiss_false(self, kivy_mocks):
        dialog_helper.show_success_dialog("S", "M")
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["auto_dismiss"] is False

    def test_opens_popup(self, kivy_mocks):
        dialog_helper.show_success_dialog("S", "M")
        instance = kivy_mocks["Popup"].return_value
        instance.open.assert_called_once()

    def test_uses_scrollview(self, kivy_mocks):
        dialog_helper.show_success_dialog("S", "M")
        kivy_mocks["ScrollView"].assert_called_once()

    def test_returns_popup(self, kivy_mocks):
        result = dialog_helper.show_success_dialog("S", "M")
        assert result is kivy_mocks["Popup"].return_value


# ---------------------------------------------------------------------------
# show_form_dialog
# ---------------------------------------------------------------------------

class TestShowFormDialog:
    def test_creates_popup_with_title(self, kivy_mocks):
        dialog_helper.show_form_dialog("Form", ["Field1"], lambda d: None)
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["title"] == "Form"

    def test_auto_dismiss_false(self, kivy_mocks):
        dialog_helper.show_form_dialog("F", ["x"], lambda d: None)
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["auto_dismiss"] is False

    def test_opens_popup(self, kivy_mocks):
        dialog_helper.show_form_dialog("F", ["x"], lambda d: None)
        instance = kivy_mocks["Popup"].return_value
        instance.open.assert_called_once()

    def test_uses_scrollview(self, kivy_mocks):
        dialog_helper.show_form_dialog("F", ["x"], lambda d: None)
        kivy_mocks["ScrollView"].assert_called_once()

    def test_returns_popup_and_inputs(self, kivy_mocks):
        result = dialog_helper.show_form_dialog("F", ["a", "b"], lambda d: None)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_textinputs_created_for_fields(self, kivy_mocks):
        dialog_helper.show_form_dialog("F", ["a", "b"], lambda d: None)
        ti_call_count = len(kivy_mocks["TextInput"].call_args_list)
        assert ti_call_count == 2

    def test_save_button_has_positive_color(self, kivy_mocks):
        dialog_helper.show_form_dialog("F", ["x"], lambda d: None)
        found_positive = any(
            call[1].get("background_color") == dialog_helper.COLOR_BTN_POSITIVE
            for call in kivy_mocks["Button"].call_args_list
        )
        assert found_positive

    def test_save_has_confirm_callback(self, kivy_mocks):
        dialog_helper.show_form_dialog("F", ["x"], lambda d: None)
        popup = kivy_mocks["Popup"].return_value
        assert hasattr(popup, "_confirm_callback")


# ---------------------------------------------------------------------------
# show_toast
# ---------------------------------------------------------------------------

class TestShowToast:
    def test_creates_popup(self, kivy_mocks):
        dialog_helper.show_toast("Hello")
        kivy_mocks["Popup"].assert_called_once()

    def test_auto_dismiss_true(self, kivy_mocks):
        dialog_helper.show_toast("Hello")
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["auto_dismiss"] is True

    def test_opens_popup(self, kivy_mocks):
        dialog_helper.show_toast("Hello")
        instance = kivy_mocks["Popup"].return_value
        instance.open.assert_called_once()

    def test_schedules_dismiss(self, kivy_mocks):
        dialog_helper.show_toast("Hello", duration=3)
        kivy_mocks["Clock"].schedule_once.assert_called_once()
        args = kivy_mocks["Clock"].schedule_once.call_args
        fn, delay = args[0]
        assert delay == 3

    def test_dismiss_on_timer(self, kivy_mocks):
        dialog_helper.show_toast("Hello")
        fn = kivy_mocks["Clock"].schedule_once.call_args[0][0]
        fn(None)
        instance = kivy_mocks["Popup"].return_value
        instance.dismiss.assert_called_once()

    def test_returns_popup(self, kivy_mocks):
        result = dialog_helper.show_toast("Hello")
        assert result is kivy_mocks["Popup"].return_value


# ---------------------------------------------------------------------------
# show_help_popup
# ---------------------------------------------------------------------------

class TestShowHelpPopup:
    def test_creates_popup_with_title(self, kivy_mocks):
        dialog_helper.show_help_popup("Help", "Body")
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs["title"] == "Help"

    def test_opens_popup(self, kivy_mocks):
        dialog_helper.show_help_popup("H", "B")
        instance = kivy_mocks["Popup"].return_value
        instance.open.assert_called_once()

    def test_uses_scrollview(self, kivy_mocks):
        dialog_helper.show_help_popup("H", "B")
        kivy_mocks["ScrollView"].assert_called_once()

    def test_label_halign_left(self, kivy_mocks):
        dialog_helper.show_help_popup("H", "B")
        kivy_mocks["Label"].assert_called_once()
        _, kwargs = kivy_mocks["Label"].call_args
        assert kwargs.get("halign") == "left"
        assert kwargs.get("valign") == "top"

    def test_ok_button_dismisses(self, kivy_mocks):
        dialog_helper.show_help_popup("H", "B")
        ok_call = None
        for call in kivy_mocks["Button"].call_args_list:
            if call[1].get("text") == "OK":
                ok_call = call
                break
        assert ok_call is not None, "OK button not found"
        on_release = ok_call[1]["on_release"]
        on_release()
        instance = kivy_mocks["Popup"].return_value
        instance.dismiss.assert_called_once()

    def test_popup_size(self, kivy_mocks):
        dialog_helper.show_help_popup("H", "B")
        _, kwargs = kivy_mocks["Popup"].call_args
        assert kwargs.get("size_hint") == (0.6, 0.5)
