import math
import random

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

    def init_uniforms(self):
        self.tex_sampler = self.program["tex_sampler"]

        self.time = self.slime["time"]
        self.slime_frame_time = self.slime["frame_time"]
        self.trail_weight = self.slime["trail_weight"]

        self.fade_frame_time = self.fade["frame_time"]
        self.diffuse_rate = self.fade["diffuse_rate"]
        self.decay_rate = self.fade["decay_rate"]

        self.tex_sampler.value = 1
        self.trail_weight.value = config.general.trail_weight
        self.diffuse_rate.value = config.general.diffuse_rate
        self.decay_rate.value = config.general.decay_rate

    def init_buffers(self):
        agents = bytearray()
        settings = bytearray()
        self.num_agents = 0

        for (species_index, species_config) in enumerate(config.species):
            for i in range(species_config.agents):
                mask = random.randrange(len(config.species))
                agents += Agent(
                    position=(self.window_size[0] / 2, self.window_size[1] / 2),
                    angle=math.pi * 2 * i / species_config.agents,
                    species_index=species_index,
                    species_mask=(
                        int(mask == 0),
                        int(mask == 1),
                        int(mask == 2),
                        int(mask == 3),
                    ),
                ).pack()

            settings += SpeciesSettings(
                move_speed=species_config.move_speed,
                turn_speed=species_config.turn_speed,
                sensor_angle_degrees=species_config.sensor_angle_degrees,
                sensor_offset_dst=species_config.sensor_offset_dst,
                sensor_size=species_config.sensor_size,
                color=species_config.color,
            ).pack()

            self.num_agents += species_config.agents

        self.agent_buf = self.ctx.buffer(agents)
        self.settings_buf = self.ctx.buffer(settings)

        self.agent_buf.bind_to_storage_buffer(0)
        self.settings_buf.bind_to_storage_buffer(1)

    def init_work_groups(self):
        self.slime_groups = self.work_groups(
            (self.num_agents, 1, 1), constants.SLIME_SHADER_GROUPS.values()
        )
        self.fade_groups = self.work_groups(
            (*self.trail_map.size, 1), constants.FADE_SHADER_GROUPS.values()
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

        self.slime.run(*self.slime_groups)
        self.fade.run(*self.fade_groups)

        self.vao.render(moderngl.TRIANGLE_STRIP)
