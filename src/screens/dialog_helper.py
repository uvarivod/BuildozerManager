from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

# Colors
COLOR_BG = (0.15, 0.15, 0.15, 1)
COLOR_TEXT = (0.85, 0.85, 0.85, 1)
COLOR_TEXT_DIM = (0.7, 0.7, 0.7, 1)
COLOR_BTN_POSITIVE = (0.2, 0.6, 0.2, 1)
COLOR_BTN_DESTRUCTIVE = (0.8, 0.2, 0.2, 1)
COLOR_BTN_NEUTRAL = (0.3, 0.3, 0.3, 1)

# Sizes
DIALOG_SIZE_INFO = (0.4, 0.25)
DIALOG_SIZE_CONFIRM = (0.45, 0.3)
DIALOG_SIZE_ERROR = (0.5, 0.3)
DIALOG_SIZE_SUCCESS = (0.4, 0.25)
DIALOG_SIZE_FORM = (0.6, 0.5)
TOAST_SIZE = (0.3, 0.08)


def _on_key_down(popup, window, key, scancode, codepoint, modifiers):
    if key == 27:
        popup.dismiss()
    elif key == 13:
        cb = getattr(popup, '_confirm_callback', None)
        if cb:
            cb()
            popup.dismiss()


def _add_keyboard_support(popup):
    from kivy.core.window import Window
    Window.bind(on_key_down=lambda w, k, s, c, m: _on_key_down(popup, w, k, s, c, m))
    popup.bind(on_dismiss=lambda *_: _unbind_keyboard(popup))


def _unbind_keyboard(popup):
    from kivy.core.window import Window
    Window.unbind(on_key_down=lambda w, k, s, c, m: None)


def show_info_dialog(title: str, message: str):
    from kivy.uix.scrollview import ScrollView
    scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
    content = BoxLayout(orientation="vertical", spacing='10dp', padding='10dp', size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))

    label = Label(text=message, halign="center", valign="middle", color=COLOR_TEXT, size_hint_y=None)
    label.bind(
        width=lambda inst, w: setattr(inst, 'text_size', (w - 20, None)),
        texture_size=lambda inst, ts: setattr(inst, 'height', max(ts[1] + 10, 40)),
    )
    content.add_widget(label)

    btn_box = BoxLayout(size_hint_y=None, height='40dp', spacing='10dp')
    btn_box.add_widget(Button(text="OK", on_release=lambda *_: popup.dismiss()))
    content.add_widget(btn_box)

    scroll.add_widget(content)
    popup = Popup(title=title, content=scroll, size_hint=(0.5, 0.35))
    popup.open()
    return popup


def show_confirm_dialog(title: str, message: str, on_confirm, confirm_text="Delete", cancel_text="Cancel"):
    from kivy.uix.scrollview import ScrollView
    scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
    content = BoxLayout(orientation="vertical", spacing='10dp', padding='10dp', size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))

    label = Label(text=message, halign="center", valign="middle", color=COLOR_TEXT, size_hint_y=None)
    label.bind(
        width=lambda inst, w: setattr(inst, 'text_size', (w - 20, None)),
        texture_size=lambda inst, ts: setattr(inst, 'height', max(ts[1] + 10, 40)),
    )
    content.add_widget(label)

    btn_box = BoxLayout(spacing='10dp', size_hint_y=None, height='40dp')
    btn_box.add_widget(Button(text=cancel_text, on_release=lambda *_: popup.dismiss()))
    btn_box.add_widget(Button(
        text=confirm_text,
        background_color=COLOR_BTN_DESTRUCTIVE,
        on_release=lambda *_: (on_confirm(), popup.dismiss()),
    ))
    content.add_widget(btn_box)

    scroll.add_widget(content)
    popup = Popup(title=title, content=scroll, size_hint=(0.5, 0.35), auto_dismiss=False)
    popup._confirm_callback = on_confirm
    popup.open()
    return popup


def show_error_dialog(title: str, message: str):
    from kivy.uix.scrollview import ScrollView
    scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
    content = BoxLayout(orientation="vertical", spacing='10dp', padding='10dp', size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))

    label = Label(text=message, halign="center", valign="middle", color=COLOR_TEXT, size_hint_y=None)
    label.bind(
        width=lambda inst, w: setattr(inst, 'text_size', (w - 20, None)),
        texture_size=lambda inst, ts: setattr(inst, 'height', max(ts[1] + 10, 40)),
    )
    content.add_widget(label)

    btn_box = BoxLayout(spacing='10dp', size_hint_y=None, height='40dp')
    btn_box.add_widget(Button(text="OK", on_release=lambda *_: popup.dismiss()))
    content.add_widget(btn_box)

    scroll.add_widget(content)
    popup = Popup(title=title, content=scroll, size_hint=(0.5, 0.35), auto_dismiss=False)
    popup.open()
    return popup


def show_success_dialog(title: str, message: str):
    from kivy.uix.scrollview import ScrollView
    scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
    content = BoxLayout(orientation="vertical", spacing='10dp', padding='10dp', size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))

    label = Label(text=message, halign="center", valign="middle", color=COLOR_TEXT, size_hint_y=None)
    label.bind(
        width=lambda inst, w: setattr(inst, 'text_size', (w - 20, None)),
        texture_size=lambda inst, ts: setattr(inst, 'height', max(ts[1] + 10, 40)),
    )
    content.add_widget(label)

    btn_box = BoxLayout(spacing='10dp', size_hint_y=None, height='40dp')
    btn_box.add_widget(Button(text="OK", on_release=lambda *_: popup.dismiss()))
    content.add_widget(btn_box)

    scroll.add_widget(content)
    popup = Popup(title=title, content=scroll, size_hint=(0.5, 0.35), auto_dismiss=False)
    popup.open()
    return popup


def show_form_dialog(title: str, fields: list[str], on_save, save_text="Save", cancel_text="Cancel"):
    from kivy.uix.scrollview import ScrollView
    scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
    content = BoxLayout(orientation="vertical", spacing='6dp', padding=[10, 10], size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))

    inputs = {}
    for field in fields:
        content.add_widget(Label(text=f"{field}:", size_hint_y=None, height='18dp', font_size="11sp", halign="left", color=COLOR_TEXT_DIM))
        ti = TextInput(size_hint_y=None, height='28dp', font_size="12sp", multiline=False)
        content.add_widget(ti)
        inputs[field] = ti

    btn_box = BoxLayout(spacing='10dp', size_hint_y=None, height='36dp')
    btn_box.add_widget(Button(text=cancel_text, on_release=lambda *_: popup.dismiss()))
    btn_box.add_widget(Button(
        text=save_text,
        background_color=COLOR_BTN_POSITIVE,
        on_release=lambda *_: (on_save({k: v.text for k, v in inputs.items()}), popup.dismiss()),
    ))
    content.add_widget(btn_box)

    scroll.add_widget(content)
    popup = Popup(title=title, content=scroll, size_hint=(0.5, 0.5), auto_dismiss=False)
    popup._confirm_callback = lambda: on_save({k: v.text for k, v in inputs.items()})
    popup.open()
    return popup, inputs


def show_toast(message: str, duration: float = 2):
    content = BoxLayout(padding='6dp')
    label = Label(text=message, font_size="11sp", halign="center", valign="middle", color=COLOR_TEXT)
    content.add_widget(label)

    popup = Popup(title="", content=content, size_hint=(0.3, 0.1), auto_dismiss=True, background_color=(0.2, 0.2, 0.2, 0.9))
    popup.open()
    Clock.schedule_once(lambda dt: popup.dismiss(), duration)
    return popup


def show_help_popup(title: str, body_text: str):
    from kivy.uix.scrollview import ScrollView
    scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
    content = BoxLayout(orientation="vertical", spacing='10dp', padding='10dp', size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))

    label = Label(
        text=body_text,
        size_hint_y=None,
        halign="left",
        valign="top",
        color=COLOR_TEXT,
    )
    label.bind(
        width=lambda inst, w: setattr(inst, "text_size", (w - 10, None)),
        texture_size=lambda inst, ts: setattr(inst, "height", ts[1] + 10),
    )
    content.add_widget(label)

    btn_box = BoxLayout(size_hint_y=None, height='40dp', spacing='10dp')
    btn_box.add_widget(Button(text="OK", on_release=lambda *_: popup.dismiss()))
    content.add_widget(btn_box)

    scroll.add_widget(content)

    popup = Popup(
        title=title,
        content=scroll,
        size_hint=(0.6, 0.5),
    )
    popup.open()
    return popup
