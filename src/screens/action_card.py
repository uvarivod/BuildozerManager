from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty, DictProperty
from kivy.clock import Clock

from src.models.action import Action, ActionState
from src.models.patch import PatchRegistry
from src.services.action_runner import ActionRunner
from src.services.log_service import LogService


class ActionCard(BoxLayout):
    action_name = StringProperty("")
    description = StringProperty("")
    is_skipped = BooleanProperty(False)
    allow_click = BooleanProperty(False)
    action_state = StringProperty("PENDING")
    is_completed = BooleanProperty(False)

    def __init__(self, action: Action, on_card_click=None, **kwargs):
        super().__init__(**kwargs)
        self.action = action
        self.action_name = action.name
        self.description = action.description
        self.action_index = -1
        self._on_card_click = on_card_click

    def on_button_pressed(self):
        if not self.allow_click:
            return
        if self._on_card_click:
            self._on_card_click(self.action, self.action_index)

    def toggle_skip(self):
        self.is_skipped = not self.is_skipped

    def set_state(self, state: ActionState):
        self.action_state = state.name
        self.is_completed = state in (ActionState.SUCCESS, ActionState.FAILED, ActionState.CANCELLED, ActionState.SKIPPED)

    def reset_state(self):
        self.action_state = "PENDING"
        self.is_completed = False


class PatchCard(BoxLayout):
    action_name = StringProperty("")
    description = StringProperty("")
    is_skipped = BooleanProperty(False)
    allow_click = BooleanProperty(False)
    action_state = StringProperty("PENDING")
    is_completed = BooleanProperty(False)
    patch_names = ListProperty([])
    patch_states = DictProperty({})

    def __init__(self, action: Action, on_card_click=None, on_patch_click=None, profile=None, **kwargs):
        super().__init__(**kwargs)
        self.action = action
        self.action_name = action.name
        self.description = action.description
        self.action_index = -1
        self._on_card_click = on_card_click
        self._on_patch_click = on_patch_click
        self._profile = profile
        self.patch_names = list(profile.patches) if profile else []
        self.patch_states = {name: "PENDING" for name in self.patch_names}

    def on_button_pressed(self):
        if not self.allow_click:
            return
        if self._on_card_click:
            self._on_card_click(self.action, self.action_index)

    def toggle_skip(self):
        self.is_skipped = not self.is_skipped

    def set_state(self, state: ActionState):
        self.action_state = state.name
        self.is_completed = state in (ActionState.SUCCESS, ActionState.FAILED, ActionState.CANCELLED, ActionState.SKIPPED)

    def reset_state(self):
        self.action_state = "PENDING"
        self.is_completed = False
        for name in self.patch_states:
            self.patch_states[name] = "PENDING"

    def on_patch_button_pressed(self, patch_name: str):
        if not self.allow_click:
            return
        if self._on_patch_click:
            self._on_patch_click(self.action, patch_name)

    def set_patch_state(self, patch_name: str, state: str):
        self.patch_states = {**self.patch_states, patch_name: state}

    def _build_patch_buttons(self):
        from kivy.uix.button import Button
        from kivy.uix.gridlayout import GridLayout
        grid = self.ids.get("patch_buttons_grid")
        if not grid:
            return
        grid.clear_widgets()
        self._patch_buttons = []
        for name in self.patch_names:
            btn = Button(
                text=name,
                size_hint_y=None,
                height=28,
                font_size="10sp",
                background_normal="",
                background_color=(0.25, 0.25, 0.25, 1),
                disabled=not self.allow_click,
            )
            self._bind_patch_button(btn, name)
            grid.add_widget(btn)
            self._patch_buttons.append(btn)

        def on_allow_click(inst, value):
            for btn in self._patch_buttons:
                btn.disabled = not value
        self.bind(allow_click=on_allow_click)

    def _bind_patch_button(self, btn, patch_name):
        from kivy.clock import Clock
        def update_color(dt):
            state = self.patch_states.get(patch_name, "PENDING")
            if state == "SUCCESS":
                btn.background_color = (0.2, 0.6, 0.2, 1)
            elif state == "FAILED":
                btn.background_color = (0.6, 0.2, 0.2, 1)
            elif state == "RUNNING":
                btn.background_color = (0.8, 0.6, 0.1, 1)
            else:
                btn.background_color = (0.25, 0.25, 0.25, 1)
        def on_click(instance):
            self.on_patch_button_pressed(patch_name)
        btn.bind(on_release=on_click)
        self.bind(patch_states=lambda *_: Clock.schedule_once(update_color))
