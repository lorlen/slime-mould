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
class GeneralConfig:
    agents: int
    spawn_mode: tuple[
        Literal["center", "inside-circle", "on-circle", "random"],
        Literal["inwards", "outwards", "random"],
    ]
    trail_weight: float
    diffuse_rate: float
    decay_rate: float


@ts.settings
class Config:
    general: GeneralConfig
    species: list[SpeciesConfig]


config = ts.load(Config, "slime-mould", [CONFIG_PATH])
