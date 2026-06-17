from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, ListProperty

from src.models.action import Action
from src.services.storage_service import ScenarioStore


class ScenarioBuilderScreen(Screen):
    action_list = ObjectProperty(None)
    scenario_name_input = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_sequence: list[str] = []
        self._available_actions = [a.name.title() for a in Action]

    def on_enter(self, *args):
        if self.action_list:
            self.action_list.values = self._available_actions

    def add_action(self, action_name: str):
        if action_name and action_name not in self._current_sequence:
            self._current_sequence.append(action_name)
            self._update_list()

    def remove_action(self, index: int):
        if 0 <= index < len(self._current_sequence):
            self._current_sequence.pop(index)
            self._update_list()

    def move_up(self, index: int):
        if index > 0:
            self._current_sequence[index], self._current_sequence[index - 1] = \
                self._current_sequence[index - 1], self._current_sequence[index]
            self._update_list()

    def move_down(self, index: int):
        if index < len(self._current_sequence) - 1:
            self._current_sequence[index], self._current_sequence[index + 1] = \
                self._current_sequence[index + 1], self._current_sequence[index]
            self._update_list()

    def _update_list(self):
        if self.action_list:
            self.action_list.values = [
                f"{i+1}. {a}" for i, a in enumerate(self._current_sequence)
            ]

    def save_scenario(self):
        if not self.scenario_name_input or not self.scenario_name_input.text:
            return
        if not self._current_sequence:
            return

        action_map = {a.name.title(): a for a in Action}
        sequence = [action_map[name] for name in self._current_sequence if name in action_map]

        scenarios = ScenarioStore.load_all()
        scenarios.append({
            "name": self.scenario_name_input.text.strip(),
            "action_sequence": [a.name for a in sequence],
            "stop_on_failure": True,
        })
        ScenarioStore.save_all(scenarios)
        self._current_sequence.clear()
        self._update_list()
        self.scenario_name_input.text = ""
