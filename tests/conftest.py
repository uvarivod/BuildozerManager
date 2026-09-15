import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.models.profile import Profile


# ---------------------------------------------------------------------------
# Kivy mocking: build stable mock modules so imports resolve consistently
# ---------------------------------------------------------------------------

class _KivyModule:
    pass


def _build_kivy_tree():
    kivy = _KivyModule()

    kivy.app = _KivyModule()
    kivy.app.App = MagicMock(name="App")

    kivy.uix = _KivyModule()
    kivy.uix.screenmanager = _KivyModule()
    class MockScreen:
        pass
    kivy.uix.screenmanager.Screen = MockScreen
    kivy.uix.screenmanager.ScreenManager = MagicMock(name="ScreenManager")
    kivy.uix.boxlayout = _KivyModule()
    class MockBoxLayout:
        def __init__(self, **kwargs):
            self._mock = MagicMock()
        def __getattr__(self, name):
            return getattr(self._mock, name)
        def bind(self, **kwargs):
            pass
    kivy.uix.boxlayout.BoxLayout = MockBoxLayout
    kivy.uix.label = _KivyModule()
    kivy.uix.label.Label = MagicMock(name="Label")
    kivy.uix.button = _KivyModule()
    kivy.uix.button.Button = MagicMock(name="Button")
    kivy.uix.textinput = _KivyModule()
    kivy.uix.textinput.TextInput = MagicMock(name="TextInput")
    kivy.uix.spinner = _KivyModule()
    kivy.uix.spinner.Spinner = MagicMock(name="Spinner")

    class _MockSpinnerOption:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
            self.text = kwargs.get("text", "")
            self._hover_inside = False
            self._hover_event = None

        def bind(self, **kwargs):
            pass

        def unbind(self, **kwargs):
            pass

        def collide_point(self, *args):
            return False

        def to_widget(self, x, y):
            return (x, y)

        def get_parent_window(self):
            return None

    kivy.uix.spinner.SpinnerOption = _MockSpinnerOption
    kivy.uix.dropdown = _KivyModule()
    kivy.uix.dropdown.DropDown = MagicMock(name="DropDown")
    kivy.uix.popup = _KivyModule()
    kivy.uix.popup.Popup = MagicMock(name="Popup")
    kivy.uix.checkbox = _KivyModule()
    kivy.uix.checkbox.CheckBox = MagicMock(name="CheckBox")
    kivy.uix.scrollview = _KivyModule()
    kivy.uix.scrollview.ScrollView = MagicMock(name="ScrollView")
    kivy.uix.filechooser = _KivyModule()
    kivy.uix.filechooser.FileChooserIconView = MagicMock(name="FileChooserIconView")
    kivy.uix.filechooser.FileChooserListView = MagicMock(name="FileChooserListView")
    kivy.uix.togglebutton = _KivyModule()
    kivy.uix.togglebutton.ToggleButton = MagicMock(name="ToggleButton")

    kivy.lang = _KivyModule()
    kivy.lang.Builder = MagicMock(name="Builder")

    kivy.properties = _KivyModule()
    kivy.properties.ObjectProperty = MagicMock(name="ObjectProperty")
    kivy.properties.StringProperty = MagicMock(name="StringProperty")
    kivy.properties.BooleanProperty = MagicMock(name="BooleanProperty")
    kivy.properties.ListProperty = MagicMock(name="ListProperty")
    kivy.properties.DictProperty = MagicMock(name="DictProperty")

    kivy.metrics = _KivyModule()
    kivy.metrics.dp = MagicMock(name="dp", return_value=0)

    kivy.core = _KivyModule()
    kivy.core.window = _KivyModule()
    kivy.core.window.Window = MagicMock(name="Window")
    kivy.core.window.Window.width = 800
    kivy.core.window.Window.height = 600
    kivy.core.window.Window.mouse_pos = (0, 0)

    kivy.clock = _KivyModule()
    kivy.clock.Clock = MagicMock(name="Clock")

    kivy.graphics = _KivyModule()
    kivy.graphics.Color = MagicMock(name="Color")
    kivy.graphics.RoundedRectangle = MagicMock(name="RoundedRectangle")

    kivy.uix.gridlayout = _KivyModule()
    kivy.uix.gridlayout.GridLayout = MagicMock(name="GridLayout")

    kivy.config = _KivyModule()
    kivy.config.Config = MagicMock(name="Config")
    kivy.Config = kivy.config.Config

    return kivy


_KIVY = _build_kivy_tree()


def _install_kivy():
    k = _KIVY
    sys.modules["kivy"] = k
    sys.modules["kivy.app"] = k.app
    sys.modules["kivy.uix"] = k.uix
    sys.modules["kivy.uix.screenmanager"] = k.uix.screenmanager
    sys.modules["kivy.uix.boxlayout"] = k.uix.boxlayout
    sys.modules["kivy.uix.label"] = k.uix.label
    sys.modules["kivy.uix.button"] = k.uix.button
    sys.modules["kivy.uix.textinput"] = k.uix.textinput
    sys.modules["kivy.uix.spinner"] = k.uix.spinner
    sys.modules["kivy.uix.dropdown"] = k.uix.dropdown
    sys.modules["kivy.uix.popup"] = k.uix.popup
    sys.modules["kivy.uix.checkbox"] = k.uix.checkbox
    sys.modules["kivy.uix.scrollview"] = k.uix.scrollview
    sys.modules["kivy.uix.filechooser"] = k.uix.filechooser
    sys.modules["kivy.uix.togglebutton"] = k.uix.togglebutton
    sys.modules["kivy.uix.gridlayout"] = k.uix.gridlayout
    sys.modules["kivy.graphics"] = k.graphics
    sys.modules["kivy.lang"] = k.lang
    sys.modules["kivy.properties"] = k.properties
    sys.modules["kivy.metrics"] = k.metrics
    sys.modules["kivy.core"] = k.core
    sys.modules["kivy.core.window"] = k.core.window
    sys.modules["kivy.clock"] = k.clock
    sys.modules["kivy.config"] = k.config


def pytest_configure():
    _install_kivy()


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_profile():
    return Profile(
        name="test-profile",
        sourcedir="/home/user/project",
        spec_path="/home/user/project/buildozer.spec",
        adb_path="adb",
        excluded_files=["__pycache__", ".git"],
        wsl_dir="\\\\wsl.localhost\\Ubuntu-22.04\\home\\alex\\bui",
        wsl_distro="Ubuntu-22.04",
        patches=["patch1", "patch2"],
        delete_exclusions=[],
    )


@pytest.fixture
def mock_log_callback():
    return MagicMock()


@pytest.fixture
def kivy_mocks():
    k = _KIVY
    return {
        "Screen": k.uix.screenmanager.Screen,
        "BoxLayout": k.uix.boxlayout.BoxLayout,
        "Label": k.uix.label.Label,
        "Button": k.uix.button.Button,
        "TextInput": k.uix.textinput.TextInput,
        "Spinner": k.uix.spinner.Spinner,
        "Popup": k.uix.popup.Popup,
        "CheckBox": k.uix.checkbox.CheckBox,
        "ScrollView": k.uix.scrollview.ScrollView,
        "DictProperty": k.properties.DictProperty,
        "ObjectProperty": k.properties.ObjectProperty,
        "StringProperty": k.properties.StringProperty,
        "BooleanProperty": k.properties.BooleanProperty,
        "ListProperty": k.properties.ListProperty,
        "dp": k.metrics.dp,
        "Window": k.core.window.Window,
        "Clock": k.clock.Clock,
        "Config": k.config.Config,
    }
