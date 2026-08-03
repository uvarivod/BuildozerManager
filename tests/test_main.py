import main

_CONFIG_CALLS = [c.args for c in main.Config.set.call_args_list]


def test_main_sets_exit_on_escape_before_app_import():
    assert ("kivy", "exit_on_escape", "0") in _CONFIG_CALLS


def test_main_exit_on_escape_config_positioned_first():
    esc_index = _CONFIG_CALLS.index(("kivy", "exit_on_escape", "0"))
    keyboard_mode_index = _CONFIG_CALLS.index(("kivy", "keyboard_mode", "system"))
    assert esc_index > keyboard_mode_index


def test_escape_does_not_trigger_window_close_without_dialog(kivy_mocks):
    window = kivy_mocks["Window"]
    assert window.close.call_count == 0
    for call in window.bind.call_args_list:
        assert "on_request_close" not in (call.kwargs or {})
