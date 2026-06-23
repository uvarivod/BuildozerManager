from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from src.services.log_service import LogService, LogEvent


MAX_LOG_LINES = 1000

class SelectableLogInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sel_anchor = None

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        if 'shift' in Window.modifiers:
            anchor = self._sel_anchor if self._sel_anchor is not None else 0
            
            # Prevent Kivy from hijacking the click as a double-tap word selection
            old_double = touch.is_double_tap
            touch.is_double_tap = False
            super().on_touch_down(touch)
            touch.is_double_tap = old_double
            
            current = self.cursor_index()
            self.select_text(min(anchor, current), max(anchor, current))
            self._sel_anchor = anchor
            return True

        res = super().on_touch_down(touch)
        self._sel_anchor = self.cursor_index()
        return res

class LogPanel(BoxLayout):
    log_display = ObjectProperty(None)
    log_scroll = ObjectProperty(None)
    duration_label = StringProperty("00:00:00")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._log_service = LogService()
        self._log_service.subscribe(self._on_log_event)
        self._start_time = None
        self._pending_events: list[str] = []
        self._pending_replace: str | None = None
        self._flush_triggered = False
        self._line_count = 0
        Clock.schedule_interval(self._update_duration, 0.5)
        from datetime import datetime
        from pathlib import Path
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        self._auto_log_path = log_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    def _on_log_event(self, event: LogEvent):
        if event.replace_last:
            self._pending_replace = event.plain_text()
        else:
            self._pending_events.append(event.plain_text())
        if not self._flush_triggered:
            self._flush_triggered = True
            Clock.schedule_once(self._flush_log, 0.05)

    def _flush_log(self, dt):
        self._flush_triggered = False
        if not self.log_display or (not self._pending_events and not self._pending_replace):
            return

        if self._pending_replace and self.log_display:
            if self._line_count > 0:
                idx = self.log_display.text.rfind("\n", 0, -1)
                if idx >= 0:
                    self.log_display.text = self.log_display.text[:idx + 1] + self._pending_replace + "\n"
                else:
                    self.log_display.text = self._pending_replace + "\n"
            else:
                self.log_display.text = self._pending_replace + "\n"
                self._line_count = 1
            self._auto_save(self._pending_replace + "\n")
            self._pending_replace = None
            if not self._pending_events:
                return

        text = "\n".join(self._pending_events) + "\n"
        new_lines = len(self._pending_events)
        self._pending_events.clear()
        if self._line_count + new_lines > MAX_LOG_LINES:
            excess = self._line_count + new_lines - MAX_LOG_LINES
            idx = -1
            count = 0
            while count < excess:
                idx = self.log_display.text.find("\n", idx + 1)
                if idx == -1:
                    break
                count += 1
            if idx >= 0:
                self.log_display.text = self.log_display.text[idx + 1:]
                self._line_count -= count
        self.log_display.text += text
        self._line_count += new_lines
        if self.log_scroll:
            self.log_scroll.scroll_y = 0
        self._auto_save(text)

    def _auto_save(self, text: str):
        try:
            with open(str(self._auto_log_path), "a", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            pass

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

    def reset_timer(self):
        from datetime import datetime
        self._start_time = datetime.now()

    def stop_timer(self):
        self._start_time = None

    def clear_log(self):
        self._log_service.clear()
        if self.log_display:
            self.log_display.text = ""
        self._start_time = None

    def save_log(self):
        content = self._log_service.get_plain_text()
        if not content:
            return

        from datetime import datetime
        from pathlib import Path

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        default_name = f"buildozer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        default_path = str(log_dir / default_name)

        box = BoxLayout(orientation="vertical", padding=10, spacing=10)
        box.add_widget(Label(text="Filename:", halign="left", size_hint_y=None, height=20))
        filename_input = TextInput(text=default_path, multiline=False)
        box.add_widget(filename_input)

        def on_save(btn):
            path = filename_input.text.strip()
            if not path:
                return
            if not path.endswith(".log"):
                path += ".log"
            full = Path(path)
            full.parent.mkdir(parents=True, exist_ok=True)
            with open(str(full), "w", encoding="utf-8") as f:
                f.write(content)
            popup.dismiss()

        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=8)
        btn_save = Button(text="Save")
        btn_save.bind(on_release=on_save)
        btn_box.add_widget(btn_save)
        btn_cancel = Button(text="Cancel")
        btn_cancel.bind(on_release=lambda x: popup.dismiss())
        btn_box.add_widget(btn_cancel)
        box.add_widget(btn_box)

        popup = Popup(title="Save Log", content=box, size_hint=(0.5, 0.3))
        popup.open()
