from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.clock import Clock

from src.models.action import Action
from src.models.custom_action import CustomAction, ActionType
from src.models.scenario import Scenario
from src.models.patch import PatchRegistry
from src.services.storage_service import ScenarioStore, CustomActionStore, ProfileStore
from src.services.scenario_service import ScenarioService


def _make_popup_label(text, **kw):
    lbl = Label(text=text, size_hint_y=None, halign="center", valign="middle", **kw)
    lbl.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
    return lbl


class ActionChip(Button):
    def __init__(self, action, editor_screen=None, **kwargs):
        super().__init__(**kwargs)
        self.action = action
        self.editor_screen = editor_screen
        if isinstance(action, CustomAction):
            self.text = action.name
        else:
            self.text = action.name.title()
        self.size_hint_y = None
        self.height = 36
        self.font_size = "12sp"
        self.background_normal = ""
        self.background_color = (0.25, 0.25, 0.25, 1)
        self._touch_start = None
        self._ghost = None
        self._is_patch_type = isinstance(action, CustomAction) and action.type == ActionType.PATCH

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self._touch_start = (touch.x, touch.y)
        if not self._is_patch_type:
            touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if self._is_patch_type:
            return True
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
        if self._is_patch_type:
            if self._touch_start and self.editor_screen and self.collide_point(*touch.pos):
                dx = abs(touch.x - self._touch_start[0])
                dy = abs(touch.y - self._touch_start[1])
                is_click = dx < 10 and dy < 10
                self._touch_start = None
                if is_click:
                    self.editor_screen._show_edit_dialog(self.action)
                    return True
                return False
            self._touch_start = None
            return False
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
                    target._show_edit_dialog(self.action)
                else:
                    drop_idx = target._on_drag_end()
                    if not (target._current_scenario and target._current_scenario.is_predefined):
                        if target._is_drop_on_trash(touch.x, touch.y):
                            pass
                        else:
                            action_val = self.action if isinstance(self.action, Action) else Action.CUSTOM_SCRIPT
                            custom_name = self.action.name if isinstance(self.action, CustomAction) else None
                            target._add_action_to_sequence(action_val, drop_idx, custom_name=custom_name)
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
        self._reset_state()
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
        self._scenarios_with_missing = self._find_scenarios_with_missing_actions()
        self._build_scenario_list()
        if self._all_scenarios and not self._current_scenario:
            self._on_scenario_selected(self._all_scenarios[0])

    def _find_scenarios_with_missing_actions(self) -> set:
        ca_names = self._get_existing_ca_names()
        missing = set()
        for s in self._all_scenarios:
            for name in s.custom_action_names.values():
                if name not in ca_names:
                    missing.add(s.name)
                    break
        return missing

    def _get_existing_ca_names(self) -> set:
        if not hasattr(self, '_existing_ca_names_cache'):
            custom_actions = CustomActionStore.load_all()
            self._existing_ca_names_cache = {ca.name for ca in custom_actions}
        return self._existing_ca_names_cache

    def _custom_action_exists(self, name: str) -> bool:
        return name in self._get_existing_ca_names()

    def _invalidate_ca_cache(self):
        if hasattr(self, '_existing_ca_names_cache'):
            del self._existing_ca_names_cache

    def _build_scenario_list(self):
        if not self.scenario_list_container:
            Clock.schedule_once(lambda dt: self._build_scenario_list(), 0)
            return
        self.scenario_list_container.clear_widgets()
        self._scenario_buttons.clear()
        for s in self._all_scenarios:
            has_missing = s.name in self._scenarios_with_missing
            btn = Button(
                text=f"{'[!] ' if has_missing else ''}{'[R] ' if s.is_predefined else ''}{s.name}",
                size_hint_y=None,
                height=36,
                font_size="11sp",
                halign="left",
                valign="middle",
                text_size=(self.scenario_list_container.width - 12, None),
                background_normal="",
                background_color=(0.3, 0.1, 0.1, 0.9) if has_missing else (
                    (0.2, 0.2, 0.2, 0.9) if not s.is_predefined else (0.15, 0.15, 0.15, 0.7)
                ),
                color=(1, 0.5, 0.5, 1) if has_missing else (
                    (0.7, 0.7, 0.7, 1) if s.is_predefined else (1, 1, 1, 1)
                ),
            )
            btn.scenario = s
            btn.bind(on_release=lambda b: self._on_scenario_selected(b.scenario))
            self.scenario_list_container.add_widget(btn)
            self._scenario_buttons.append(btn)
        self._highlight_selected_scenario()

    def _highlight_selected_scenario(self):
        for btn in self._scenario_buttons:
            is_selected = btn.scenario is self._current_scenario
            has_missing = btn.scenario.name in self._scenarios_with_missing
            btn.background_color = (0.25, 0.5, 0.8, 1) if is_selected else (
                (0.3, 0.1, 0.1, 0.9) if has_missing else (
                    (0.15, 0.15, 0.15, 0.7) if btn.scenario.is_predefined else (0.2, 0.2, 0.2, 0.9)
                )
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

        from kivy.uix.gridlayout import GridLayout

        inner = BoxLayout(orientation="vertical", size_hint_y=None, spacing=2, padding=[2, 2])
        inner.bind(minimum_height=inner.setter("height"))

        actions_header = Label(
            text="Available Actions",
            size_hint_y=None,
            height=22,
            bold=True,
            font_size="11sp",
            color=(0.8, 0.8, 0.8, 1),
            halign="center",
            valign="middle",
        )
        inner.add_widget(actions_header)

        actions_grid = GridLayout(cols=1, size_hint_y=None, spacing=2, padding=[4, 4])
        actions_grid.bind(minimum_height=actions_grid.setter("height"))

        for action in Action:
            if action == Action.CUSTOM_SCRIPT:
                continue
            chip = ActionChip(action=action, editor_screen=self)
            actions_grid.add_widget(chip)
            self._action_chips.append(chip)

        custom_actions = CustomActionStore.load_all()
        for ca in custom_actions:
            if ca.type == ActionType.ACTION:
                chip = ActionChip(action=ca, editor_screen=self)
                actions_grid.add_widget(chip)
                self._action_chips.append(chip)

        inner.add_widget(actions_grid)

        patches_header = Label(
            text="Available Patches",
            size_hint_y=None,
            height=22,
            bold=True,
            font_size="11sp",
            color=(0.8, 0.8, 0.8, 1),
            halign="center",
            valign="middle",
        )
        inner.add_widget(patches_header)

        patches_grid = GridLayout(cols=1, size_hint_y=None, spacing=2, padding=[4, 4])
        patches_grid.bind(minimum_height=patches_grid.setter("height"))

        for ca in custom_actions:
            if ca.type == ActionType.PATCH:
                chip = ActionChip(action=ca, editor_screen=self)
                patches_grid.add_widget(chip)
                self._action_chips.append(chip)

        for bp in PatchRegistry.list_patches():
            builtin_patch = CustomAction(
                id=f"builtin:{bp.name}",
                name=bp.name,
                description=bp.description,
                type=ActionType.PATCH,
                logic="built-in",
                is_builtin=True,
            )
            chip = ActionChip(action=builtin_patch, editor_screen=self)
            patches_grid.add_widget(chip)
            self._action_chips.append(chip)

        inner.add_widget(patches_grid)
        self.palette_container.add_widget(inner)

    def _show_edit_dialog(self, action_data):
        from src.models.custom_action import ActionType
        is_builtin_action = isinstance(action_data, Action)
        is_custom = isinstance(action_data, CustomAction)

        title = action_data.name if hasattr(action_data, 'name') else action_data.name.title()
        from kivy.uix.widget import Widget
        content = BoxLayout(orientation="vertical", spacing=6, padding=[10, 10])
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(Label(text="Name:", size_hint_y=None, height=18, font_size="11sp", halign="left", color=(0.7, 0.7, 0.7, 1)))
        name_input = TextInput(
            text=action_data.name if hasattr(action_data, 'name') else action_data.name.title(),
            size_hint_y=None, height=28, font_size="12sp", multiline=False,
            readonly=is_builtin_action,
        )
        content.add_widget(name_input)

        content.add_widget(Label(text="Description:", size_hint_y=None, height=18, font_size="11sp", halign="left", color=(0.7, 0.7, 0.7, 1)))
        desc_input = TextInput(
            text=action_data.description if hasattr(action_data, 'description') else "",
            size_hint_y=None, height=48, font_size="12sp", multiline=True,
            readonly=is_builtin_action,
        )
        content.add_widget(desc_input)

        type_label = action_data.type.name.title() if is_custom else "ACTION"
        content.add_widget(Label(text="Type:", size_hint_y=None, height=18, font_size="11sp", halign="left", color=(0.7, 0.7, 0.7, 1)))
        type_input = TextInput(text=type_label, size_hint_y=None, height=28, font_size="12sp", multiline=False, readonly=True)
        content.add_widget(type_input)

        logic_label = action_data.logic if is_custom else ("built-in" if is_builtin_action else "")
        content.add_widget(Label(text="Logic:", size_hint_y=None, height=18, font_size="11sp", halign="left", color=(0.7, 0.7, 0.7, 1)))
        logic_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=28, spacing=4)
        logic_input = TextInput(
            text=logic_label,
            size_hint_x=1, size_hint_y=None, height=28, font_size="12sp", multiline=False,
            readonly=is_builtin_action,
        )
        logic_box.add_widget(logic_input)
        if is_custom and not action_data.is_builtin:
            def on_browse(*_):
                from src.screens.file_chooser_helper import FileChooserHelper
                def script_filter(folder, filename):
                    import os
                    return os.path.isdir(os.path.join(folder, filename)) or filename.lower().endswith(".bat")
                FileChooserHelper._show_chooser(
                    title="Select script",
                    initial_path="",
                    on_choose=lambda path: setattr(logic_input, 'text', path),
                    dirselect=False,
                    custom_filter=script_filter,
                )
            browse_btn = Button(text="Browse", size_hint_x=None, width=60, font_size="10sp")
            browse_btn.bind(on_release=on_browse)
            logic_box.add_widget(browse_btn)
        content.add_widget(logic_box)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=36)

        if is_builtin_action or (is_custom and action_data.is_builtin):
            close_btn = Button(text="Close", size_hint=(0.5, 1), font_size="12sp")
            popup = Popup(title=f"Action: {title}", content=content, size_hint=(0.45, 0.55))
            close_btn.bind(on_release=lambda *_: popup.dismiss())
            btn_box.add_widget(close_btn)
        elif is_custom:
            save_btn = Button(text="Save", size_hint=(0.4, 1), font_size="12sp", background_color=(0.2, 0.6, 0.2, 1))
            delete_btn = Button(text="Delete", size_hint=(0.3, 1), font_size="12sp", background_color=(0.6, 0.2, 0.2, 1))
            cancel_btn = Button(text="Cancel", size_hint=(0.3, 1), font_size="12sp")
            popup = Popup(title=f"Custom Action: {title}", content=content, size_hint=(0.45, 0.55))

            def on_save(*_):
                ca = action_data
                new_name = name_input.text.strip()
                if new_name != ca.name:
                    existing = CustomActionStore.load_all()
                    if any(c.name == new_name for c in existing):
                        err_popup = Popup(title="Duplicate Name", size_hint=(0.35, 0.18))
                        err_content = BoxLayout(orientation="vertical", spacing=10, padding=10)
                        err_content.add_widget(Label(text=f"An action named '{new_name}' already exists."))
                        err_btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
                        err_btn_box.add_widget(Button(text="OK", on_release=lambda *_: err_popup.dismiss()))
                        err_content.add_widget(err_btn_box)
                        err_popup.content = err_content
                        err_popup.open()
                        return
                old_name = ca.name
                ca.name = new_name
                ca.description = desc_input.text.strip()
                ca.logic = logic_input.text.strip()
                CustomActionStore.save(ca)
                if old_name != new_name:
                    for s in ScenarioStore.load_all():
                        changed = False
                        for k, v in list(s.custom_action_names.items()):
                            if v == old_name:
                                s.custom_action_names[k] = new_name
                                changed = True
                        if changed:
                            ScenarioStore.save(s)
                    profiles = ProfileStore.load_all()
                    changed = False
                    for p in profiles:
                        if old_name in p.patches:
                            p.patches = [new_name if x == old_name else x for x in p.patches]
                            changed = True
                    if changed:
                        ProfileStore.save_all(profiles)
                self._invalidate_ca_cache()
                self._build_palette()
                if old_name != new_name:
                    old_current = self._current_scenario.name if self._current_scenario else None
                    self._refresh_scenarios()
                    if old_current:
                        for s in self._all_scenarios:
                            if s.name == old_current:
                                self._on_scenario_selected(s)
                                break
                popup.dismiss()

            def on_delete(*_):
                popup.dismiss()
                confirm = BoxLayout(orientation="vertical", spacing=10, padding=10)
                confirm.add_widget(Label(text=f"Delete '{action_data.name}'?"))
                btn_row = BoxLayout(spacing=10, size_hint_y=None, height=40)
                confirm_popup = Popup(title="Confirm", content=confirm, size_hint=(0.35, 0.2))
                btn_row.add_widget(Button(text="Cancel", on_release=lambda *_: confirm_popup.dismiss()))
                btn_row.add_widget(Button(text="Delete", background_color=(0.8, 0.2, 0.2, 1),
                    on_release=lambda *_: (confirm_popup.dismiss(), self._confirm_delete_action(action_data))))
                confirm.add_widget(btn_row)
                confirm_popup.open()

            save_btn.bind(on_release=on_save)
            delete_btn.bind(on_release=on_delete)
            cancel_btn.bind(on_release=lambda *_: popup.dismiss())
            btn_box.add_widget(save_btn)
            btn_box.add_widget(delete_btn)
            btn_box.add_widget(cancel_btn)

        content.add_widget(btn_box)
        content.add_widget(Widget())
        popup.open()

    def _confirm_delete_action(self, action_data):
        all_scenarios = ScenarioStore.load_all() + self._service.get_predefined_scenarios()
        used_in = set()
        if self._current_scenario:
            for idx, a in enumerate(self._current_actions):
                if a == Action.CUSTOM_SCRIPT and self._current_scenario.custom_action_names.get(idx) == action_data.name:
                    used_in.add(f"Scenario: {self._current_scenario.name}")
                    break
        for s in all_scenarios:
            if s is self._current_scenario:
                continue
            for idx, a in enumerate(s.action_sequence):
                if a == Action.CUSTOM_SCRIPT and s.custom_action_names.get(idx) == action_data.name:
                    used_in.add(f"Scenario: {s.name}")
                    break
        if action_data.type == ActionType.PATCH:
            profiles = ProfileStore.load_all()
            for p in profiles:
                if action_data.name in p.patches:
                    used_in.add(f"Profile: {p.name}")
        if used_in:
            msg = f"Cannot delete '{action_data.name}'. It is used in:\n" + "\n".join(f"  - {ref}" for ref in used_in)
            content = BoxLayout(orientation="vertical", spacing=10, padding=10)
            content.add_widget(Label(text=msg, font_size="11sp"))
            btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
            popup = Popup(title="Action In Use", content=content, size_hint=(0.45, 0.35))
            btn_box.add_widget(Button(text="OK", on_release=lambda *_: popup.dismiss()))
            content.add_widget(btn_box)
            popup.open()
            return
        CustomActionStore.delete(action_data.id)
        self._invalidate_ca_cache()
        self._build_palette()

    def _show_create_action_dialog(self):
        import uuid
        from kivy.uix.widget import Widget
        content = BoxLayout(orientation="vertical", spacing=6, padding=[10, 10])
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(Label(text="Name:", size_hint_y=None, height=18, font_size="11sp", halign="left", color=(0.7, 0.7, 0.7, 1)))
        name_input = TextInput(size_hint_y=None, height=28, font_size="12sp", multiline=False)
        content.add_widget(name_input)

        content.add_widget(Label(text="Description:", size_hint_y=None, height=18, font_size="11sp", halign="left", color=(0.7, 0.7, 0.7, 1)))
        desc_input = TextInput(size_hint_y=None, height=48, font_size="12sp", multiline=True)
        content.add_widget(desc_input)

        content.add_widget(Label(text="Type:", size_hint_y=None, height=18, font_size="11sp", halign="left", color=(0.7, 0.7, 0.7, 1)))
        type_spinner = Spinner(text="Action", values=["Action", "Patch"], size_hint_y=None, height=28, font_size="12sp")
        content.add_widget(type_spinner)

        content.add_widget(Label(text="Logic (script path or built-in name):", size_hint_y=None, height=18, font_size="11sp", halign="left", color=(0.7, 0.7, 0.7, 1)))
        logic_input = TextInput(size_hint_y=None, height=28, font_size="12sp", multiline=False)
        logic_box = BoxLayout(spacing=4, size_hint_y=None, height=28)
        logic_box.add_widget(logic_input)
        browse_btn = Button(text="Browse", size_hint_x=None, width=60, font_size="10sp")

        def on_browse(*_):
            from src.screens.file_chooser_helper import FileChooserHelper
            def script_filter(folder, filename):
                import os
                return os.path.isdir(os.path.join(folder, filename)) or filename.lower().endswith(".bat")
            FileChooserHelper._show_chooser(
                title="Select script",
                initial_path="",
                on_choose=lambda path: setattr(logic_input, 'text', path),
                dirselect=False,
                custom_filter=script_filter,
            )

        browse_btn.bind(on_release=on_browse)
        logic_box.add_widget(browse_btn)
        content.add_widget(logic_box)

        btn_box = BoxLayout(spacing=10, size_hint_y=None, height=36)
        popup = Popup(title="New Custom Action", content=content, size_hint=(0.45, 0.6))

        def on_save(*_):
            name = name_input.text.strip()
            if not name:
                return
            existing = CustomActionStore.load_all()
            if any(ca.name == name for ca in existing):
                err_popup = Popup(title="Duplicate Name", size_hint=(0.35, 0.18))
                err_content = BoxLayout(orientation="vertical", spacing=10, padding=10)
                err_content.add_widget(Label(text=f"An action named '{name}' already exists."))
                err_btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
                err_btn_box.add_widget(Button(text="OK", on_release=lambda *_: err_popup.dismiss()))
                err_content.add_widget(err_btn_box)
                err_popup.content = err_content
                err_popup.open()
                return
            ca = CustomAction(
                id=str(uuid.uuid4()),
                name=name,
                description=desc_input.text.strip(),
                type=ActionType.ACTION if type_spinner.text == "Action" else ActionType.PATCH,
                logic=logic_input.text.strip(),
                is_builtin=False,
            )
            CustomActionStore.save(ca)
            self._invalidate_ca_cache()
            self._build_palette()
            popup.dismiss()

        save_btn = Button(text="Save", size_hint=(0.5, 1), font_size="12sp", background_color=(0.2, 0.6, 0.2, 1))
        cancel_btn = Button(text="Cancel", size_hint=(0.5, 1), font_size="12sp")
        save_btn.bind(on_release=on_save)
        cancel_btn.bind(on_release=lambda *_: popup.dismiss())
        btn_box.add_widget(save_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)
        content.add_widget(Widget())
        popup.open()

    def _on_scenario_selected(self, scenario: Scenario):
        self._current_scenario = scenario
        self._current_actions = list(scenario.action_sequence)
        self._undo_mgr.clear()

        self._render_sequence()
        self._highlight_selected_scenario()

        if self.name_input:
            self.name_input.unbind(text=self._on_name_changed)
            self.name_input.text = scenario.name
            self.name_input.disabled = scenario.is_predefined
            self.name_input.bind(text=self._on_name_changed)
        if self.desc_input:
            self.desc_input.unbind(text=self._on_desc_changed)
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

            if action == Action.CUSTOM_SCRIPT and self._current_scenario:
                display_name = self._current_scenario.custom_action_names.get(idx, action.name.title())
                ca_exists = self._custom_action_exists(display_name)
            else:
                display_name = action.name.title()
                ca_exists = True
            card = BoxLayout(orientation="vertical", size_hint=(None, None), size=(100, card_height), spacing=2)
            action_btn = Button(
                text=display_name,
                size_hint_y=None,
                height=36,
                font_size="10sp",
                background_normal="",
                background_color=(0.5, 0.15, 0.15, 1) if not ca_exists else (0.3, 0.3, 0.3, 1),
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
            custom_name = None
            if self._current_scenario and index in self._current_scenario.custom_action_names:
                custom_name = self._current_scenario.custom_action_names.pop(index)
                shifted = {}
                for k, v in self._current_scenario.custom_action_names.items():
                    if k > index:
                        shifted[k - 1] = v
                    else:
                        shifted[k] = v
                self._current_scenario.custom_action_names = shifted
            self._undo_mgr.record("remove", {"index": index, "action": removed, "custom_name": custom_name}, {"index": index})
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
                custom_name = None
                if self._current_scenario and orig in self._current_scenario.custom_action_names:
                    custom_name = self._current_scenario.custom_action_names.pop(orig)
                    shifted = {}
                    for k, v in self._current_scenario.custom_action_names.items():
                        if k > orig:
                            shifted[k - 1] = v
                        else:
                            shifted[k] = v
                    self._current_scenario.custom_action_names = shifted
                self._undo_mgr.record("remove", {"index": orig, "action": removed, "custom_name": custom_name}, {"index": orig})
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

    def _add_action_to_sequence(self, action: Action, index: int | None = None, custom_name: str | None = None):
        if index is None:
            index = len(self._current_actions)
        if custom_name is not None:
            if self._current_scenario is None:
                self._current_scenario = Scenario(name="", action_sequence=list(self._current_actions))
            shifted = {}
            for k, v in self._current_scenario.custom_action_names.items():
                if k >= index:
                    shifted[k + 1] = v
                else:
                    shifted[k] = v
            shifted[index] = custom_name
            self._current_scenario.custom_action_names = shifted
        self._current_actions.insert(index, action)
        self._undo_mgr.record("add", {}, {"action": action, "index": index, "custom_name": custom_name})
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
            idx = len(self._current_actions) - 1
            if self._current_scenario:
                self._current_scenario.custom_action_names.pop(idx, None)
                shifted = {}
                for k, v in self._current_scenario.custom_action_names.items():
                    if k < idx:
                        shifted[k] = v
                    elif k > idx:
                        shifted[k - 1] = v
                self._current_scenario.custom_action_names = shifted
            self._current_actions.pop()
        elif action_name == "remove":
            idx = data["index"]
            self._current_actions.insert(idx, data["action"])
            if self._current_scenario and data["action"] == Action.CUSTOM_SCRIPT:
                custom_name = data.get("custom_name")
                if custom_name:
                    shifted = {}
                    for k, v in self._current_scenario.custom_action_names.items():
                        if k >= idx:
                            shifted[k + 1] = v
                        else:
                            shifted[k] = v
                    shifted[idx] = custom_name
                    self._current_scenario.custom_action_names = shifted
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

        custom_actions = CustomActionStore.load_all()
        ca_names = {ca.name for ca in custom_actions}
        custom_names = {}
        missing = []
        seen = set()
        for idx, action in enumerate(self._current_actions):
            if action == Action.CUSTOM_SCRIPT:
                name = (self._current_scenario.custom_action_names.get(idx)
                        if self._current_scenario else None)
                if name:
                    custom_names[idx] = name
                    if name not in ca_names and name not in seen:
                        missing.append(name)
                        seen.add(name)
        if missing:
            msg = f"Cannot save. Scenario references missing actions:\n" + "\n".join(f"  - {name}" for name in missing)
            content = BoxLayout(orientation="vertical", spacing=10, padding=10)
            content.add_widget(Label(text=msg, font_size="11sp"))
            btn_box = BoxLayout(spacing=10, size_hint_y=None, height=40)
            popup = Popup(title="Missing Actions", content=content, size_hint=(0.45, 0.3))
            btn_box.add_widget(Button(text="OK", on_release=lambda *_: popup.dismiss()))
            content.add_widget(btn_box)
            popup.open()
            return

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
            custom_action_names=custom_names,
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
            btn_box = BoxLayout(spacing=6, size_hint_y=None, height=40)
            popup = Popup(title="Unsaved Changes", content=content, size_hint=(0.45, 0.25))
            def save_and_leave(*_):
                self.on_save()
                popup.dismiss()
                self._navigate_back()
            def discard_and_leave(*_):
                self._reset_state()
                popup.dismiss()
                self._navigate_back()
            btn_box.add_widget(Button(text="Save and Leave", size_hint_x=None, width=120, on_release=save_and_leave))
            btn_box.add_widget(Button(text="Discard and Leave", size_hint_x=None, width=120, on_release=discard_and_leave))
            btn_box.add_widget(Button(text="Cancel", size_hint_x=None, width=90, on_release=lambda *_: popup.dismiss()))
            content.add_widget(btn_box)
            popup.open()
        else:
            self._navigate_back()

    def _reset_state(self):
        self._current_scenario = None
        self._current_actions.clear()
        self._undo_mgr.clear()
        if self.name_input:
            self.name_input.text = ""
        if self.desc_input:
            self.desc_input.text = ""
        if self.save_btn:
            self.save_btn.disabled = False
        if self.delete_btn:
            self.delete_btn.disabled = True
        self._render_sequence()

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
