from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView


def show_help_popup(title: str, body_text: str):
    scroll = ScrollView(do_scroll_x=False, do_scroll_y=True)
    content = BoxLayout(orientation="vertical", spacing='10dp', padding='10dp', size_hint_y=None)
    content.bind(minimum_height=content.setter("height"))

    label = Label(
        text=body_text,
        size_hint_y=None,
        halign="left",
        valign="top",
        color=(0.85, 0.85, 0.85, 1),
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
