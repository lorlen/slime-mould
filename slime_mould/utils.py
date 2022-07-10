import math
import random

from .config import Config
from .glsl_structs import Agent, SpeciesSettings


def _random_on_circle(r: float = 1, center: tuple[float, float] = (0, 0)):
    theta = random.random() * math.tau
    return round(center[0] + r * math.cos(theta)), round(
        center[1] + r * math.sin(theta)
    )


def _random_inside_circle(r: float = 1, center: tuple[float, float] = (0, 0)):
    return _random_on_circle(r * math.sqrt(random.random()), center)


def _normalized_diff(a: tuple[float, float], b: tuple[float, float]):
    x = a[0] - b[0]
    y = a[1] - b[1]
    mag = math.sqrt(x * x + y * y)
    return x / mag, y / mag


def generate_agents_buffer(config: Config, window_size: tuple[int, int]):
    agents = bytearray()
    center = (window_size[0] // 2, window_size[1] // 2)

    for i in range(config.agents):
        match config.spawn_mode[0]:
            case "inside-circle":
                position = _random_inside_circle(
                    min(window_size[0], window_size[1])
                    / 2
                    * config.spawn_radius,
                    center,
                )
            case "on-circle":
                position = _random_on_circle(
                    min(window_size[0], window_size[1])
                    / 2
                    * config.spawn_radius,
                    center,
                )
            case "random":
                position = random.randrange(window_size[0]), random.randrange(
                    window_size[1]
                )
            case _:
                position = center

        match config.spawn_mode[1]:
            case "inwards":
                x, y = _normalized_diff(center, position)
                angle = math.atan2(y, x)
            case "outwards":
                x, y = _normalized_diff(position, center)
                angle = math.atan2(y, x)
            case _:
                angle = random.random() * math.tau

        species = random.randrange(len(config.species))

        agents += Agent(
            position=position,
            angle=angle,
            species_index=species,
            species_mask=(
                int(species == 0),
                int(species == 1),
                int(species == 2),
                int(species == 3),
            ),
        ).pack()

    return agents


def generate_species_buffer(config: Config):
    settings = bytearray()

    for species_config in config.species:
        settings += SpeciesSettings(
            move_speed=species_config.move_speed,
            turn_speed=species_config.turn_speed,
            sensor_angle_degrees=species_config.sensor_angle_degrees,
            sensor_offset_dst=species_config.sensor_offset_dst,
            sensor_size=species_config.sensor_size,
            color=species_config.color,
        ).pack()

    return settings


def work_groups(data_dim, local_dim):
    return tuple(math.ceil(d / l) for d, l in zip(data_dim, local_dim))
