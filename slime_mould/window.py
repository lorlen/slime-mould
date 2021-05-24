import math

import moderngl
from moderngl_window import geometry, WindowConfig

from . import config


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

        self.image = self.compute['image']
        self.tex_sampler = self.program['tex_sampler']

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
        
        x, y = self.texture.size
        gx, gy, _ = config.LOCAL_GROUP_SIZE.values()
        nx, ny, nz = math.ceil(x / gx), math.ceil(y / gy), 1

        self.texture.bind_to_image(0)
        self.compute.run(nx, ny, nz)

        self.texture.use(0)
        self.vao.render()

        self.vao.render(moderngl.TRIANGLE_STRIP)
