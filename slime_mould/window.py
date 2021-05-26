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
        self.compute = self.load_compute_shader(config.SHADER_DIR / config.COMPUTE_SHADER, config.LOCAL_GROUP_SIZE)
        self.vao = geometry.quad_fs(normals=False).instance(self.program)

        self.init_shader_resources()

    def init_shader_resources(self):
        self.texture = self.ctx.texture(self.window_size, 4)
        self.texture.filter = moderngl.NEAREST, moderngl.NEAREST

        self.tex_sampler = self.program['tex_sampler']
        #self.time = self.compute['time']
        self.frame_time = self.compute['frame_time']
        self.speed = self.compute['speed']

        agents = bytearray()

        for i in range(100):
            agents += Agent((self.window_size[0] / 2, self.window_size[1] / 2), math.pi * 2 * i / 100).pack()

        self.agent_buf = self.ctx.buffer(agents)

    def load_shaders(self):
        shaders = {}

        for ext, name in config.WINDOW_SHADER_EXTS.items():
            if (path := config.RESOURCE_DIR / config.SHADER_DIR / f'{config.WINDOW_SHADER_NAME}.{ext}').exists():
                shaders[name] = path.read_text()
            else:
                print(f'Could not find shader: {config.WINDOW_SHADER_NAME}.{ext}')
                exit(1)

        return shaders

    def render(self, time: float, frame_time: float):
        self.ctx.clear()
        
        gx, _, _ = config.LOCAL_GROUP_SIZE.values()
        nx, ny, nz = math.ceil(100 / gx), 1, 1

        #self.time.value = time
        self.frame_time.value = frame_time if frame_time > 0 else 1 / 60
        self.speed.value = 100.0

        self.agent_buf.bind_to_storage_buffer(0)
        self.texture.bind_to_image(0)
        self.compute.run(nx, ny, nz)

        self.texture.use(0)
        self.vao.render()

        self.vao.render(moderngl.TRIANGLE_STRIP)
