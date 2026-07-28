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

    kivy.uix = _KivyModule()
    kivy.uix.screenmanager = _KivyModule()
    class MockScreen:
        pass
    kivy.uix.screenmanager.Screen = MockScreen
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

    kivy.clock = _KivyModule()
    kivy.clock.Clock = MagicMock(name="Clock")

    return kivy


_KIVY = _build_kivy_tree()


def _install_kivy():
    k = _KIVY
    sys.modules["kivy"] = k
    sys.modules["kivy.uix"] = k.uix
    sys.modules["kivy.uix.screenmanager"] = k.uix.screenmanager
    sys.modules["kivy.uix.boxlayout"] = k.uix.boxlayout
    sys.modules["kivy.uix.label"] = k.uix.label
    sys.modules["kivy.uix.button"] = k.uix.button
    sys.modules["kivy.uix.textinput"] = k.uix.textinput
    sys.modules["kivy.uix.spinner"] = k.uix.spinner
    sys.modules["kivy.uix.popup"] = k.uix.popup
    sys.modules["kivy.uix.checkbox"] = k.uix.checkbox
    sys.modules["kivy.uix.scrollview"] = k.uix.scrollview
    sys.modules["kivy.uix.filechooser"] = k.uix.filechooser
    sys.modules["kivy.uix.togglebutton"] = k.uix.togglebutton
    sys.modules["kivy.properties"] = k.properties
    sys.modules["kivy.metrics"] = k.metrics
    sys.modules["kivy.core"] = k.core
    sys.modules["kivy.core.window"] = k.core.window
    sys.modules["kivy.clock"] = k.clock


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
    }
