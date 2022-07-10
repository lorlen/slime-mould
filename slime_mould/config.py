from typing import Literal

import typed_settings as ts

from .constants import CONFIG_PATH


@ts.settings
class SpeciesConfig:
    move_speed: float
    turn_speed: float
    sensor_angle_degrees: float
    sensor_offset_dst: float
    color: tuple[float, float, float, float]
    sensor_size: int


@ts.settings
class Config:
    window_size: tuple[int, int]

    agents: int
    spawn_mode: tuple[
        Literal["center", "inside-circle", "on-circle", "random"],
        Literal["inwards", "outwards", "random"],
    ]
    spawn_radius: float

    trail_weight: float
    diffuse_rate: float
    decay_rate: float

    species: list[SpeciesConfig]


config = ts.load(Config, "slime-mould", [CONFIG_PATH])

if len(config.species) > 3:
    raise Exception("More than 3 species are not supported")
