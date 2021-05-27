import math

import moderngl
from moderngl_window import geometry, WindowConfig

from . import config
from .glsl_structs import Agent


class Window(WindowConfig):
    gl_version = config.OPENGL_VERSION
    title = config.WINDOW_TITLE
    resource_dir = config.RESOURCE_DIR

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.program = self.ctx.program(**self.load_shaders())
        self.slime = self.load_compute_shader(config.SHADER_DIR / config.SLIME_SHADER, config.SLIME_SHADER_GROUPS)
        self.fade = self.load_compute_shader(config.SHADER_DIR / config.FADE_SHADER, config.FADE_SHADER_GROUPS)
        self.vao = geometry.quad_fs(normals=False).instance(self.program)

        self.init_shader_resources()

    def init_shader_resources(self):
        self.texture = self.ctx.texture(self.window_size, 4)
        self.texture.filter = moderngl.NEAREST, moderngl.NEAREST

        self.tex_sampler = self.program['tex_sampler']

        self.time = self.slime['time']
        self.slime_frame_time = self.slime['frame_time']
        self.slime_speed = self.slime['speed']

        self.fade_frame_time = self.fade['frame_time']
        self.diffuse_factor = self.fade['diffuse_factor']
        self.fade_speed = self.fade['fade_speed']

        agents = bytearray()

        for i in range(config.NUM_AGENTS):
            agents += Agent((self.window_size[0] / 2, self.window_size[1] / 2), math.pi * 2 * i / 100).pack()

        self.agent_buf = self.ctx.buffer(agents)

        self.slime_groups = self.work_groups((config.NUM_AGENTS, 1, 1), config.SLIME_SHADER_GROUPS.values())
        self.fade_groups = self.work_groups((*self.texture.size, 1), config.FADE_SHADER_GROUPS.values())

    def load_shaders(self):
        shaders = {}

        for ext, name in config.WINDOW_SHADER_EXTS.items():
            if (path := config.RESOURCE_DIR / config.SHADER_DIR / f'{config.WINDOW_SHADER_NAME}.{ext}').exists():
                shaders[name] = path.read_text()
            else:
                print(f'Could not find shader: {config.WINDOW_SHADER_NAME}.{ext}')
                exit(1)

        return shaders

    @staticmethod
    def work_groups(data_dim, local_dim):
        return tuple(math.ceil(d / l) for d, l in zip(data_dim, local_dim))

    def render(self, time: float, frame_time: float):
        self.ctx.clear()

        frame_time = frame_time if frame_time > 0 else 1 / 60

        self.time.value = time
        self.slime_frame_time.value = frame_time
        self.slime_speed.value = 100.0

        self.fade_frame_time.value = frame_time
        self.diffuse_factor.value = 1.0
        self.fade_speed.value = 0.04

        self.agent_buf.bind_to_storage_buffer(0)
        self.texture.bind_to_image(0)
        self.slime.run(*self.slime_groups)
        self.fade.run(*self.fade_groups)

        self.texture.use(0)
        self.vao.render()

        self.vao.render(moderngl.TRIANGLE_STRIP)
