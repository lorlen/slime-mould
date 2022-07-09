import typed_settings as ts

from .constants import CONFIG_PATH


@ts.settings
class SpeciesConfig:
    agents: int
    move_speed: float
    turn_speed: float
    sensor_angle_degrees: float
    sensor_offset_dst: float
    color: tuple[float, float, float, float]
    sensor_size: int


@ts.settings
class Config:
    species: list[SpeciesConfig]


config = ts.load(Config, "slime-mould", [CONFIG_PATH])
