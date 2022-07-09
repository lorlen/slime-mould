import math

import moderngl
from moderngl_window import WindowConfig, geometry

from . import constants
from .config import config
from .glsl_structs import Agent, SpeciesSettings


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
        self.vao = geometry.quad_fs(normals=False).instance(self.program)

        self.init_shader_resources()

    def init_shader_resources(self):
        self.texture = self.ctx.texture(self.window_size, 4)
        self.texture.filter = moderngl.NEAREST, moderngl.NEAREST

        self.tex_sampler = self.program["tex_sampler"]

        self.time = self.slime["time"]
        self.slime_frame_time = self.slime["frame_time"]

        self.fade_frame_time = self.fade["frame_time"]
        self.diffuse_factor = self.fade["diffuse_factor"]
        self.fade_speed = self.fade["fade_speed"]

        agents = bytearray()
        settings = bytearray()
        num_agents = 0

        for (species_idx, species_config) in enumerate(config.species):
            for i in range(species_config.agents):
                agents += Agent(
                    (self.window_size[0] / 2, self.window_size[1] / 2),
                    math.pi * 2 * i / species_config.agents,
                    species_idx,
                ).pack()

            settings += SpeciesSettings(
                move_speed=species_config.move_speed,
                turn_speed=species_config.turn_speed,
                sensor_angle_degrees=species_config.sensor_angle_degrees,
                sensor_offset_dst=species_config.sensor_offset_dst,
                sensor_size=species_config.sensor_size,
                color=species_config.color,
            ).pack()

            num_agents += species_config.agents

        self.agent_buf = self.ctx.buffer(agents)
        self.settings_buf = self.ctx.buffer(settings)

        self.slime_groups = self.work_groups(
            (num_agents, 1, 1), constants.SLIME_SHADER_GROUPS.values()
        )
        self.fade_groups = self.work_groups(
            (*self.texture.size, 1), constants.FADE_SHADER_GROUPS.values()
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

    @staticmethod
    def work_groups(data_dim, local_dim):
        return tuple(math.ceil(d / l) for d, l in zip(data_dim, local_dim))

    def render(self, time: float, frame_time: float):
        self.ctx.clear()

        frame_time = frame_time if frame_time > 0 else 1 / 60

        self.time.value = time
        self.slime_frame_time.value = frame_time

        self.fade_frame_time.value = frame_time
        self.diffuse_factor.value = 1.0
        self.fade_speed.value = 0.04

        self.agent_buf.bind_to_storage_buffer(0)
        self.settings_buf.bind_to_storage_buffer(1)
        self.texture.bind_to_image(0)
        self.slime.run(*self.slime_groups)
        self.fade.run(*self.fade_groups)

        self.texture.use(0)
        self.vao.render()

        self.vao.render(moderngl.TRIANGLE_STRIP)
