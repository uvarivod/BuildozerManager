from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock

from src.models.action import Action
from src.models.scenario import Scenario
from src.services.storage_service import ScenarioStore
from src.services.scenario_service import ScenarioService


class ActionChip(Button):
    def __init__(self, action: Action, editor_screen=None, **kwargs):
        super().__init__(**kwargs)
        self.action = action
        self.editor_screen = editor_screen
        self.text = action.name.title()
        self.size_hint_y = None
        self.height = 36
        self.font_size = "12sp"
        self.background_normal = ""
        self.background_color = (0.25, 0.25, 0.25, 1)
        self._touch_start = None
        self._ghost = None

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self._touch_start = (touch.x, touch.y)
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            if self._touch_start:
                from kivy.core.window import Window
                dx = abs(touch.x - self._touch_start[0])
                dy = abs(touch.y - self._touch_start[1])
                if dx > 10 or dy > 10:
                    if not self._ghost:
                        self._ghost = Button(
                            text=self.text,
                            size_hint=(None, None),
                            size=(100, 36),
                            font_size="12sp",
                            background_color=(0.3, 0.5, 0.7, 0.8),
                        )
                        Window.add_widget(self._ghost)
                        if self.editor_screen:
                            self.editor_screen._on_drag_start()
                    if self._ghost:
                        self._ghost.center = Window.mouse_pos
                    if self.editor_screen:
                        self.editor_screen._on_drag_update(Window.mouse_pos[0], Window.mouse_pos[1])
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            if self._ghost:
                from kivy.core.window import Window
                Window.remove_widget(self._ghost)
                self._ghost = None
            if self._touch_start and self.editor_screen:
                dx = abs(touch.x - self._touch_start[0])
                dy = abs(touch.y - self._touch_start[1])
                is_click = dx < 10 and dy < 10
                target = self.editor_screen
                if is_click:
                    if not (target._current_scenario and target._current_scenario.is_predefined):
                        target._add_action_to_sequence(self.action)
                else:
                    drop_idx = target._on_drag_end()
                    if not (target._current_scenario and target._current_scenario.is_predefined):
                        if target._is_drop_on_trash(touch.x, touch.y):
                            pass
                        else:
                            target._add_action_to_sequence(self.action, drop_idx)
            self._touch_start = None
            return True
        return super().on_touch_up(touch)


class UndoRedoManager:
    def __init__(self, max_size=50):
        self._undo_stack = []
        self._redo_stack = []
        self._max_size = max_size
        self._saved_at = 0

    def record(self, action_name: str, undo_data: dict, redo_data: dict):
        self._undo_stack.append((action_name, undo_data, redo_data))
        self._redo_stack.clear()
        if len(self._undo_stack) > self._max_size:
            self._undo_stack.pop(0)

    def undo(self):
        if not self._undo_stack:
            return None
        action_name, undo_data, redo_data = self._undo_stack.pop()
        self._redo_stack.append((action_name, redo_data, undo_data))
        return action_name, undo_data

    def redo(self):
        if not self._redo_stack:
            return None
        action_name, redo_data, undo_data = self._redo_stack.pop()
        self._undo_stack.append((action_name, undo_data, redo_data))
        return action_name, redo_data

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._saved_at = 0

    @property
    def can_undo(self):
        return len(self._undo_stack) > 0

    @property
    def can_redo(self):
        return len(self._redo_stack) > 0

    def mark_saved(self):
        self._saved_at = len(self._undo_stack)

    @property
    def has_unsaved(self):
        return len(self._undo_stack) != self._saved_at


class ScenarioEditorScreen(Screen):
    scenario_list_container = ObjectProperty(None)
    editor_container = ObjectProperty(None)
    palette_container = ObjectProperty(None)
    name_input = ObjectProperty(None)
    desc_input = ObjectProperty(None)
    undo_btn = ObjectProperty(None)
    redo_btn = ObjectProperty(None)
    save_btn = ObjectProperty(None)
    delete_btn = ObjectProperty(None)
    back_btn = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._all_scenarios: list[Scenario] = []
        self._predefined: list[Scenario] = []
        self._current_scenario: Scenario | None = None
        self._current_actions: list[Action] = []
        self._undo_mgr = UndoRedoManager()
        self._service = ScenarioService()
        self._scenario_buttons: list[Button] = []
        self._action_chips: list[ActionChip] = []
        self._trash_zone: BoxLayout | None = None
        self._seq_scroll: Widget | None = None
        self._dragging_chip: ActionChip | None = None
        self._insert_line = None
        self._card_widgets: list[Widget] = []
        self._drop_zones: list[Widget] = []
        self._drag_active = False
        self._drag_target_index = -1
        self._drag_original_index = -1
        self._drag_render_pending = False
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        self._refresh_scenarios()

    def on_kv_post(self, base_widget):
        self._build_editor_ui()
        self._build_palette()
        if self._current_scenario:
            self._render_sequence()
            self._highlight_selected_scenario()
            if self.name_input:
                self.name_input.text = self._current_scenario.name
                self.name_input.disabled = self._current_scenario.is_predefined
            if self.desc_input:
                self.desc_input.text = self._current_scenario.description
                self.desc_input.disabled = self._current_scenario.is_predefined
            if self.save_btn:
                self.save_btn.disabled = self._current_scenario.is_predefined
            if self.delete_btn:
                self.delete_btn.disabled = self._current_scenario.is_predefined
            self._update_undo_redo_buttons()

    def _refresh_scenarios(self):
        self._predefined = self._service.get_predefined_scenarios()
        user = ScenarioStore.load_all()
        self._all_scenarios = self._predefined + user
        self._build_scenario_list()
        if self._all_scenarios and not self._current_scenario:
            self._on_scenario_selected(self._all_scenarios[0])

    def _build_scenario_list(self):
        if not self.scenario_list_container:
            Clock.schedule_once(lambda dt: self._build_scenario_list(), 0)
            return
        self.scenario_list_container.clear_widgets()
        self._scenario_buttons.clear()
        for s in self._all_scenarios:
            btn = Button(
                text=f"{'[R] ' if s.is_predefined else ''}{s.name}",
                size_hint_y=None,
                height=36,
                font_size="11sp",
                halign="left",
                valign="middle",
                text_size=(self.scenario_list_container.width - 12, None),
                background_normal="",
                background_color=(0.2, 0.2, 0.2, 0.9) if not s.is_predefined else (0.15, 0.15, 0.15, 0.7),
                color=(0.7, 0.7, 0.7, 1) if s.is_predefined else (1, 1, 1, 1),
            )
            btn.scenario = s
            btn.bind(on_release=lambda b: self._on_scenario_selected(b.scenario))
            self.scenario_list_container.add_widget(btn)
            self._scenario_buttons.append(btn)
        self._highlight_selected_scenario()

    def _highlight_selected_scenario(self):
        for btn in self._scenario_buttons:
            is_selected = btn.scenario is self._current_scenario
            btn.background_color = (0.25, 0.5, 0.8, 1) if is_selected else (
                (0.15, 0.15, 0.15, 0.7) if btn.scenario.is_predefined else (0.2, 0.2, 0.2, 0.9)
            )

    def _build_editor_ui(self):
        if not self.editor_container:
            return
        self.editor_container.clear_widgets()

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=170, spacing=4, padding=[8, 8])
        name_label = Label(text="Name:", size_hint_y=None, height=20, halign="left", valign="middle", font_size="11sp", color=(0.7, 0.7, 0.7, 1))
        name_label.bind(size=lambda lbl, sz: setattr(lbl, "text_size", sz))
        self.name_input = TextInput(size_hint_y=None, height=28, font_size="12sp", multiline=False)
        desc_label = Label(text="Description:", size_hint_y=None, height=20, halign="left", valign="middle", font_size="11sp", color=(0.7, 0.7, 0.7, 1))
        desc_label.bind(size=lambda lbl, sz: setattr(lbl, "text_size", sz))
        self.desc_input = TextInput(size_hint_y=None, height=72, font_size="12sp", multiline=True)
        header.add_widget(name_label)
        header.add_widget(self.name_input)
        header.add_widget(desc_label)
        header.add_widget(self.desc_input)
        self.editor_container.add_widget(header)

    def _build_palette(self):
        if not self.palette_container:
            return
        self.palette_container.clear_widgets()
        self._action_chips.clear()

        palette_label = Label(
            text="Available Actions",
            size_hint_y=None,
            height=24,
            bold=True,
            font_size="11sp",
            color=(0.8, 0.8, 0.8, 1),
            halign="center",
            valign="middle",
            text_size=(self.palette_container.width if self.palette_container.width > 0 else 160, None),
        )
        self.palette_container.add_widget(palette_label)

        from kivy.uix.scrollview import ScrollView
        from kivy.uix.gridlayout import GridLayout
        sv = ScrollView(do_scroll_x=False, do_scroll_y=True)
        grid = GridLayout(cols=1, size_hint_y=None, spacing=2, padding=[4, 4])
        grid.bind(minimum_height=grid.setter("height"))

        for action in Action:
            chip = ActionChip(action=action, editor_screen=self)
            grid.add_widget(chip)
            self._action_chips.append(chip)

        sv.add_widget(grid)
        self.palette_container.add_widget(sv)

    def _on_scenario_selected(self, scenario: Scenario):
        self._current_scenario = scenario
        self._current_actions = list(scenario.action_sequence)
        self._undo_mgr.clear()

        self._render_sequence()
        self._highlight_selected_scenario()

        if self.name_input:
            self.name_input.text = scenario.name
            self.name_input.disabled = scenario.is_predefined
            self.name_input.bind(text=self._on_name_changed)
        if self.desc_input:
            self.desc_input.text = scenario.description
            self.desc_input.disabled = scenario.is_predefined
            self.desc_input.bind(text=self._on_desc_changed)

        if self.save_btn:
            self.save_btn.disabled = scenario.is_predefined
        if self.delete_btn:
            self.delete_btn.disabled = scenario.is_predefined

        self._update_undo_redo_buttons()

    def on_new(self):
        self._current_scenario = None
        self._current_actions.clear()
        self._undo_mgr.clear()
        self._render_sequence()
        if self.name_input:
            self.name_input.text = ""
            self.name_input.disabled = False
            self.name_input.bind(text=self._on_name_changed)
        if self.desc_input:
            self.desc_input.text = ""
            self.desc_input.disabled = False
            self.desc_input.bind(text=self._on_desc_changed)
        if self.save_btn:
            self.save_btn.disabled = False
        if self.delete_btn:
            self.delete_btn.disabled = True
        self._update_undo_redo_buttons()

    def _on_name_changed(self, instance, value):
        if not self._current_scenario or self._current_scenario.is_predefined:
            return
        old = self._current_scenario.name
        self._undo_mgr.record("rename", {"old_name": old}, {"new_name": value})

    def _on_desc_changed(self, instance, value):
        if not self._current_scenario or self._current_scenario.is_predefined:
            return
        old = self._current_scenario.description
        self._undo_mgr.record("edit_desc", {"old_desc": old}, {"new_desc": value})

    def _render_sequence(self):
        if not self.editor_container:
            Clock.schedule_once(lambda dt: self._render_sequence(), 0)
            return

        if self._seq_scroll:
            self.editor_container.remove_widget(self._seq_scroll)
            self._seq_scroll = None
        if self._trash_zone and self._trash_zone.parent:
            self.editor_container.remove_widget(self._trash_zone)

        if not self.name_input:
            Clock.schedule_once(lambda dt: self._render_sequence(), 0)
            return

        from kivy.uix.scrollview import ScrollView
        from kivy.uix.stacklayout import StackLayout

        seq_scroll = ScrollView(
            do_scroll_x=False, do_scroll_y=True,
            size_hint=(1, 1),
        )
        seq_layout = StackLayout(
            orientation='lr-tb',
            size_hint=(1, None),
            spacing=2,
            padding=[4, 4],
        )
        seq_layout.bind(minimum_height=seq_layout.setter("height"))

        is_readonly = self._current_scenario and self._current_scenario.is_predefined
        card_height = 36 if is_readonly else 58

        self._card_widgets.clear()
        self._drop_zones.clear()

        for idx, action in enumerate(self._current_actions):
            if idx > 0:
                arrow = Label(
                    text="->",
                    size_hint=(None, None),
                    size=(24, card_height),
                    bold=True,
                    color=(0.6, 0.6, 0.6, 1),
                    valign="center",
                    halign="center",
                )
                seq_layout.add_widget(arrow)

            card = BoxLayout(orientation="vertical", size_hint=(None, None), size=(100, card_height), spacing=2)
            action_btn = Button(
                text=action.name.title(),
                size_hint_y=None,
                height=36,
                font_size="10sp",
                background_normal="",
                background_color=(0.3, 0.3, 0.3, 1),
            )
            action_btn.action_index = idx
            action_btn.action = action
            if not is_readonly:
                action_btn.bind(
                    on_touch_down=self._on_seq_action_touch_down,
                    on_touch_move=self._on_seq_action_touch_move,
                    on_touch_up=self._on_seq_action_touch_up,
                )
            card.add_widget(action_btn)

            if not is_readonly:
                remove_btn = Button(
                    text="X",
                    size_hint_y=None,
                    height=20,
                    font_size="9sp",
                    background_normal="",
                    background_color=(0.6, 0.1, 0.1, 1),
                )
                remove_btn.action_index = idx
                remove_btn.bind(on_release=lambda b: self._remove_action(b.action_index))
                card.add_widget(remove_btn)

            seq_layout.add_widget(card)
            self._card_widgets.append(card)

        seq_scroll.add_widget(seq_layout)
        self.editor_container.add_widget(seq_scroll)
        self._seq_scroll = seq_scroll

        if not is_readonly:
            trash = Label(
                text="[ Drop actions here to remove ]",
                size_hint_y=None,
                height=28,
                font_size="11sp",
                color=(0.6, 0.3, 0.3, 1),
                halign="center",
                valign="middle",
            )
            self._trash_zone = trash
            self.editor_container.add_widget(trash)

    def _remove_action(self, index: int):
        if self._current_scenario and self._current_scenario.is_predefined:
            return
        if 0 <= index < len(self._current_actions):
            removed = self._current_actions.pop(index)
            self._undo_mgr.record("remove", {"index": index, "action": removed}, {"index": index})
            self._render_sequence()
            self._update_undo_redo_buttons()

    def _on_seq_action_touch_down(self, btn, touch):
        if not btn.collide_point(*touch.pos):
            return
        if self._current_scenario and self._current_scenario.is_predefined:
            return
        btn._touch_start = (touch.x, touch.y)
        btn._ghost = None
        self._drag_original_index = btn.action_index
        touch.grab(btn)

    def _on_seq_action_touch_move(self, btn, touch):
        if touch.grab_current is not btn:
            return
        if not getattr(btn, '_touch_start', None):
            return
        from kivy.core.window import Window
        dx = abs(touch.x - btn._touch_start[0])
        dy = abs(touch.y - btn._touch_start[1])
        if dx > 10 or dy > 10:
            if not btn._ghost:
                btn._ghost = Button(
                    text=btn.text,
                    size_hint=(None, None),
                    size=(100, 36),
                    font_size="12sp",
                    background_color=(0.3, 0.5, 0.7, 0.8),
                )
                Window.add_widget(btn._ghost)
                self._on_drag_start()
            if btn._ghost:
                btn._ghost.center = Window.mouse_pos
            self._on_drag_update(Window.mouse_pos[0], Window.mouse_pos[1])

    def _is_drop_on_trash(self, wx: float, wy: float) -> bool:
        if not self._trash_zone:
            return False
        local = self._trash_zone.to_widget(wx, wy)
        return self._trash_zone.collide_point(*local)

    def _on_seq_action_touch_up(self, btn, touch):
        if touch.grab_current is not btn:
            return
        touch.ungrab(btn)
        if btn._ghost:
            from kivy.core.window import Window
            Window.remove_widget(btn._ghost)
            btn._ghost = None
        if not getattr(btn, '_touch_start', None):
            return
        dx = abs(touch.x - btn._touch_start[0])
        dy = abs(touch.y - btn._touch_start[1])
        btn._touch_start = None
        is_click = dx < 10 and dy < 10
        if is_click:
            return
        if self._current_scenario and self._current_scenario.is_predefined:
            return
        orig = self._drag_original_index
        if self._is_drop_on_trash(touch.x, touch.y):
            self._on_drag_end()
            if 0 <= orig < len(self._current_actions):
                removed = self._current_actions.pop(orig)
                self._undo_mgr.record("remove", {"index": orig, "action": removed}, {"index": orig})
                self._render_sequence()
                self._update_undo_redo_buttons()
            return
        target = self._on_drag_end()
        if orig < 0 or orig >= len(self._current_actions):
            self._render_sequence()
            return
        if orig == target:
            self._render_sequence()
            return
        action = self._current_actions.pop(orig)
        if target > orig:
            target -= 1
        target = max(0, min(target, len(self._current_actions)))
        self._current_actions.insert(target, action)
        self._undo_mgr.record(
            "reorder",
            {"action": action, "orig": orig},
            {"action": action, "target": target},
        )
        self._render_sequence()
        self._update_undo_redo_buttons()

    def _add_action_to_sequence(self, action: Action, index: int | None = None):
        if index is None:
            index = len(self._current_actions)
        self._current_actions.insert(index, action)
        self._undo_mgr.record("add", {}, {"action": action, "index": index})
        self._render_sequence()
        self._update_undo_redo_buttons()

    def _on_drag_start(self):
        self._drag_active = True
        self._drag_target_index = len(self._current_actions)
        self._render_sequence()

    def _on_drag_update(self, tx: float, ty: float):
        if not self._drag_active:
            return
        old_target = self._drag_target_index
        best_idx = len(self._current_actions)
        best_dist = float("inf")
        for i, card in enumerate(self._card_widgets):
            wx, wy = card.to_window(card.center_x, card.center_y)
            dist = ((tx - wx) ** 2 + (ty - wy) ** 2) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best_idx = i
        if best_idx < len(self._current_actions):
            card = self._card_widgets[best_idx]
            wx = card.to_window(card.right, card.center_y)[0]
            if tx > wx:
                best_idx = best_idx + 1
        self._drag_target_index = best_idx
        if old_target != self._drag_target_index and not self._drag_render_pending:
            self._drag_render_pending = True
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._finalize_drag_render(), 0)

    def _finalize_drag_render(self):
        self._drag_render_pending = False
        self._render_sequence()

    def _on_drag_end(self) -> int:
        idx = self._drag_target_index
        self._drag_active = False
        self._drag_target_index = -1
        return idx

    def _update_undo_redo_buttons(self):
        if self.undo_btn:
            self.undo_btn.disabled = not self._undo_mgr.can_undo
        if self.redo_btn:
            self.redo_btn.disabled = not self._undo_mgr.can_redo

    def on_undo(self):
        result = self._undo_mgr.undo()
        if result is None:
            return
        action_name, data = result
        if action_name == "add":
            self._current_actions.pop()
        elif action_name == "remove":
            self._current_actions.insert(data["index"], data["action"])
        elif action_name == "rename":
            if self.name_input:
                self.name_input.unbind(text=self._on_name_changed)
                self.name_input.text = data.get("old_name", "")
                self.name_input.bind(text=self._on_name_changed)
        elif action_name == "edit_desc":
            if self.desc_input:
                self.desc_input.unbind(text=self._on_desc_changed)
                self.desc_input.text = data.get("old_desc", "")
                self.desc_input.bind(text=self._on_desc_changed)
        elif action_name == "reorder":
            act = data["action"]
            orig = data["orig"]
            cur = self._current_actions.index(act)
            self._current_actions.pop(cur)
            self._current_actions.insert(orig, act)
        self._render_sequence()
        self._update_undo_redo_buttons()

    def on_redo(self):
        result = self._undo_mgr.redo()
        if result is None:
            return
        action_name, data = result
        if action_name == "add":
            self._current_actions.append(data["action"])
        elif action_name == "remove":
            self._current_actions.pop(data["index"])
        elif action_name == "rename":
            if self.name_input:
                self.name_input.unbind(text=self._on_name_changed)
                self.name_input.text = data.get("new_name", "")
                self.name_input.bind(text=self._on_name_changed)
        elif action_name == "edit_desc":
            if self.desc_input:
                self.desc_input.unbind(text=self._on_desc_changed)
                self.desc_input.text = data.get("new_desc", "")
                self.desc_input.bind(text=self._on_desc_changed)
        elif action_name == "reorder":
            act = data["action"]
            target = data["target"]
            cur = self._current_actions.index(act)
            self._current_actions.pop(cur)
            self._current_actions.insert(target, act)
        self._render_sequence()
        self._update_undo_redo_buttons()

    def on_save(self):
        if not self.name_input or not self.name_input.text:
            return
        if not self._current_actions:
            return

        new_name = self.name_input.text.strip()

        existing = ScenarioStore.load_all()
        for s in existing:
            if s.name == new_name:
                if self._current_scenario is None or s.name != self._current_scenario.name:
                    content = BoxLayout(orientation="vertical", spacing=10, padding=10)
                    content.add_widget(Label(text=f"A scenario named '{new_name}' already exists."))
                    btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
                    popup = Popup(title="Duplicate Name", content=content, size_hint=(0.35, 0.18))
                    btn_box.add_widget(Button(text="OK", on_release=lambda *_: popup.dismiss()))
                    content.add_widget(btn_box)
                    popup.open()
                    return

        scenario = Scenario(
            name=new_name,
            description=self.desc_input.text.strip() if self.desc_input else "",
            action_sequence=list(self._current_actions),
            stop_on_failure=True,
            is_predefined=False,
        )
        old_name = self._current_scenario.name if self._current_scenario else None
        if old_name and old_name != new_name:
            ScenarioStore.delete(old_name)
        ScenarioStore.save(scenario)
        self._undo_mgr.mark_saved()
        self._refresh_scenarios()
        from src.services.log_service import LogService
        LogService().info(f"Scenario '{scenario.name}' saved")

    def on_delete(self):
        if not self._current_scenario or self._current_scenario.is_predefined:
            return

        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=f"Delete scenario '{self._current_scenario.name}'?"))
        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
        popup = Popup(title="Confirm", content=content, size_hint=(0.4, 0.3))
        btn_box.add_widget(Button(text="Cancel", on_release=lambda *_: popup.dismiss()))
        btn_box.add_widget(Button(
            text="Delete",
            background_color=(0.8, 0.2, 0.2, 1),
            on_release=lambda *_: self._confirm_delete(popup),
        ))
        content.add_widget(btn_box)
        popup.open()

    def _confirm_delete(self, popup):
        popup.dismiss()
        if not self._current_scenario:
            return
        ScenarioStore.delete(self._current_scenario.name)
        self._current_scenario = None
        self._current_actions.clear()
        self._undo_mgr.clear()
        if self.name_input:
            self.name_input.text = ""
        if self.desc_input:
            self.desc_input.text = ""
        self._render_sequence()
        self._refresh_scenarios()
        from src.services.log_service import LogService
        LogService().info(f"Scenario deleted")

    def on_back(self):
        if self._undo_mgr.has_unsaved:
            content = BoxLayout(orientation="vertical", spacing=10, padding=10)
            content.add_widget(Label(text="Save changes before leaving?"))
            btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
            popup = Popup(title="Unsaved Changes", content=content, size_hint=(0.4, 0.3))
            def save_and_leave(*_):
                self.on_save()
                popup.dismiss()
                self._navigate_back()
            def discard_and_leave(*_):
                popup.dismiss()
                self._navigate_back()
            btn_box.add_widget(Button(text="Save and Leave", on_release=save_and_leave))
            btn_box.add_widget(Button(text="Discard and Leave", on_release=discard_and_leave))
            btn_box.add_widget(Button(text="Cancel", on_release=lambda *_: popup.dismiss()))
            content.add_widget(btn_box)
            popup.open()
        else:
            self._navigate_back()

    def _navigate_back(self):
        if self.manager:
            actions_screen = self.manager.get_screen("actions")
            if hasattr(actions_screen, "on_enter"):
                actions_screen.on_enter()
            if hasattr(actions_screen, "scenario_spinner") and actions_screen.scenario_spinner:
                text = actions_screen.scenario_spinner.text
                if text and text != "Select scenario" and hasattr(actions_screen, "on_scenario_selected"):
                    actions_screen.on_scenario_selected(text)
            self.manager.current = "actions"
