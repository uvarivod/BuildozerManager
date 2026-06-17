from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.button import Button

from src.services.log_service import LogService, LogEvent


class LogPanel(BoxLayout):
    log_display = ObjectProperty(None)
    duration_label = StringProperty("00:00:00")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._log_service = LogService()
        self._log_service.subscribe(self._on_log_event)
        self._start_time = None
        Clock.schedule_interval(self._update_duration, 1)

    def _on_log_event(self, event: LogEvent):
        Clock.schedule_once(lambda dt: self._append_log(event), 0)

    def _append_log(self, event: LogEvent):
        if not self.log_display:
            return
        self.log_display.text += event.formatted() + "\n"
        if hasattr(self.log_display, "scroll_y"):
            self.log_display.scroll_y = 0
        if self._start_time is None:
            self._start_time = event.timestamp

    def _update_duration(self, dt):
        if self._start_time is None:
            return
        from datetime import datetime
        elapsed = datetime.now() - self._start_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        self.duration_label = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def clear_log(self):
        self._log_service.clear()
        if self.log_display:
            self.log_display.text = ""
        self._start_time = None

    def save_log(self):
        content = self._log_service.get_plain_text()
        if not content:
            return

        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        filechooser = FileChooserListView(path=".")
        box.add_widget(filechooser)

        def on_choose(btn):
            selection = filechooser.selection
            if selection:
                path = selection[0]
                if not path.endswith(".log"):
                    path += ".log"
                import os
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            popup.dismiss()

        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=8)
        btn_choose = Button(text="Save")
        btn_choose.bind(on_release=on_choose)
        btn_cancel = Button(text="Cancel")
        btn_cancel.bind(on_release=lambda x: popup.dismiss())
        btn_box.add_widget(btn_choose)
        btn_box.add_widget(btn_cancel)
        box.add_widget(btn_box)

        popup = Popup(title="Save Log", content=box, size_hint=(0.8, 0.8))
        popup.open()
