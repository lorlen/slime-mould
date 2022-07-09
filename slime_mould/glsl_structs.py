from dataclasses import dataclass
from struct import Struct
from typing import ClassVar


@dataclass
class Agent:
    _struct: ClassVar[Struct] = Struct("=3fi")

    position: tuple[float, float]
    angle: float
    species: int

    def pack(self):
        return self._struct.pack(*self.position, self.angle, self.species)

    @classmethod
    def unpack(cls, buffer: bytes, offset: int = 0):
        data = cls._struct.unpack_from(buffer, offset)
        return cls(data[:2], data[2], data[3])


@dataclass
class SpeciesSettings:
    _struct: ClassVar[Struct] = Struct("=8fi12x")

    move_speed: float
    turn_speed: float
    sensor_angle_degrees: float
    sensor_offset_dst: float
    color: tuple[float, float, float, float]
    sensor_size: int

    def pack(self):
        return self._struct.pack(
            self.move_speed,
            self.turn_speed,
            self.sensor_angle_degrees,
            self.sensor_offset_dst,
            *self.color,
            self.sensor_size,
        )

    @classmethod
    def unpack(cls, buffer: bytes, offset: int = 0):
        data = cls._struct.unpack_from(buffer, offset)
        return cls(data[0], data[1], data[2], data[3], data[4:7], data[8])
