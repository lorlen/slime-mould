from pathlib import Path

OPENGL_VERSION = (4, 6)

RESOURCE_DIR = Path(__file__).parent.parent / 'resources'
SHADER_DIR = Path('shaders')

WINDOW_TITLE = 'Slime Mould'
WINDOW_SHADER_NAME = 'window'
WINDOW_SHADER_EXTS = {
    'vert': 'vertex_shader',
    'frag': 'fragment_shader'
}

COMPUTE_SHADER = 'slime.comp'
LOCAL_GROUP_SIZE = {'X': 16, 'Y': 1, 'Z': 1}
