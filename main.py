import os
import sys
from kivy import Config
from pathlib import Path
Config.set('kivy', 'keyboard_mode', 'system')
Config.set('input', 'mouse', 'mouse,disable_multitouch')

# Ensure Kivy dependency DLLs (SDL2, GLEW, etc.) are on PATH
_venv_share = Path(sys.prefix) / "share"
for dep_dir in ["sdl2", "glew", "angle"]:
    bin_path = str(_venv_share / dep_dir / "bin")
    if os.path.isdir(bin_path) and bin_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = bin_path + os.pathsep + os.environ.get("PATH", "")

sys.path.insert(0, str(Path(__file__).parent))

from src.app import BuildozerManagerApp

if __name__ == '__main__':
    BuildozerManagerApp().run()
