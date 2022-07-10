from pathlib import Path

OPENGL_VERSION = (4, 6)

RESOURCE_DIR = Path(__file__).parent.parent / "resources"
SHADER_DIR = Path("shaders")

WINDOW_TITLE = "Slime Mould"
WINDOW_SHADER_NAME = "window"
WINDOW_SHADER_EXTS = {"vert": "vertex_shader", "frag": "fragment_shader"}

SLIME_SHADER = "slime.comp"
SLIME_SHADER_GROUPS = {"X": 16, "Y": 1, "Z": 1}

FADE_SHADER = "fade.comp"
FADE_SHADER_GROUPS = {"X": 16, "Y": 16, "Z": 1}

COLOR_SHADER = "color.comp"
COLOR_SHADER_GROUPS = {"X": 16, "Y": 16, "Z": 1}

CONFIG_PATH = Path(__file__).parent.parent / "config.toml"
