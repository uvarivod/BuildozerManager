from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock

from src.models.action import Action, ActionState
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
            self._on_card_click(self.action)

    def toggle_skip(self):
        self.is_skipped = not self.is_skipped

    def set_state(self, state: ActionState):
        self.action_state = state.name
        self.is_completed = state in (ActionState.SUCCESS, ActionState.FAILED, ActionState.CANCELLED, ActionState.SKIPPED)

    def reset_state(self):
        self.action_state = "PENDING"
        self.is_completed = False
