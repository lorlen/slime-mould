import moderngl
from moderngl_window import WindowConfig, geometry

from . import constants
from .config import config
from .utils import generate_agents_buffer, generate_species_buffer, work_groups


class Window(WindowConfig):
    gl_version = constants.OPENGL_VERSION
    title = constants.WINDOW_TITLE
    resource_dir = constants.RESOURCE_DIR

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.program = self.ctx.program(**self.load_shaders())
        self.slime = self.load_compute_shader(
            constants.SHADER_DIR / constants.SLIME_SHADER, constants.SLIME_SHADER_GROUPS
        )
        self.fade = self.load_compute_shader(
            constants.SHADER_DIR / constants.FADE_SHADER, constants.FADE_SHADER_GROUPS
        )
        self.color = self.load_compute_shader(
            constants.SHADER_DIR / constants.COLOR_SHADER, constants.COLOR_SHADER_GROUPS
        )
        self.vao = geometry.quad_fs(normals=False).instance(self.program)

        self.init_textures()
        self.init_uniforms()
        self.init_buffers()
        self.init_work_groups()

    def init_textures(self):
        self.trail_map = self.ctx.texture(self.window_size, 4)
        self.trail_map.filter = moderngl.NEAREST, moderngl.NEAREST
        self.trail_map.bind_to_image(0)
        self.trail_map.use(0)

        self.diffused_trail_map = self.ctx.texture(self.window_size, 4)
        self.diffused_trail_map.filter = moderngl.NEAREST, moderngl.NEAREST
        self.diffused_trail_map.bind_to_image(1)
        self.diffused_trail_map.use(1)

        self.color_map = self.ctx.texture(self.window_size, 4)
        self.color_map.filter = moderngl.NEAREST, moderngl.NEAREST
        self.color_map.bind_to_image(2)
        self.color_map.use(2)

        self.swap_buffer = self.ctx.buffer(
            reserve=self.trail_map.size[0]
            * self.trail_map.size[1]
            * self.trail_map.components
        )

    def init_uniforms(self):
        self.tex_sampler = self.program["tex_sampler"]

        self.time = self.slime["time"]
        self.slime_frame_time = self.slime["frame_time"]
        self.trail_weight = self.slime["trail_weight"]

        self.fade_frame_time = self.fade["frame_time"]
        self.diffuse_rate = self.fade["diffuse_rate"]
        self.decay_rate = self.fade["decay_rate"]

        self.tex_sampler.value = 2  # type: ignore
        self.trail_weight.value = config.general.trail_weight  # type: ignore
        self.diffuse_rate.value = config.general.diffuse_rate  # type: ignore
        self.decay_rate.value = config.general.decay_rate  # type: ignore

    def init_buffers(self):
        self.agent_buf = self.ctx.buffer(
            generate_agents_buffer(config, self.window_size)
        )
        self.settings_buf = self.ctx.buffer(generate_species_buffer(config))

        self.agent_buf.bind_to_storage_buffer(0)
        self.settings_buf.bind_to_storage_buffer(1)

    def init_work_groups(self):
        self.slime_groups = work_groups(
            (config.general.agents, 1, 1), constants.SLIME_SHADER_GROUPS.values()
        )
        self.fade_groups = work_groups(
            (*self.trail_map.size, 1), constants.FADE_SHADER_GROUPS.values()
        )
        self.color_groups = work_groups(
            (*self.trail_map.size, 1), constants.COLOR_SHADER_GROUPS.values()
        )

    def load_shaders(self):
        shaders = {}

        for ext, name in constants.WINDOW_SHADER_EXTS.items():
            if (
                path := constants.RESOURCE_DIR
                / constants.SHADER_DIR
                / f"{constants.WINDOW_SHADER_NAME}.{ext}"
            ).exists():
                shaders[name] = path.read_text()
            else:
                print(f"Could not find shader: {constants.WINDOW_SHADER_NAME}.{ext}")
                exit(1)

        return shaders

    def render(self, time: float, frame_time: float):
        self.ctx.clear()

        frame_time = frame_time if frame_time > 0 else 1 / 60

        self.time.value = time  # type: ignore
        self.slime_frame_time.value = frame_time  # type: ignore
        self.fade_frame_time.value = frame_time  # type: ignore

        self.slime.run(*self.slime_groups)
        self.fade.run(*self.fade_groups)

        self.diffused_trail_map.read_into(self.swap_buffer)
        self.trail_map.write(self.swap_buffer)

        self.color.run(*self.color_groups)

        self.vao.render(moderngl.TRIANGLE_STRIP)
