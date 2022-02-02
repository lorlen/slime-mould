from dataclasses import dataclass
from struct import Struct
from typing import ClassVar, Tuple


@dataclass
class Agent:
    _struct: ClassVar[Struct] = Struct('=3fI')

    position: Tuple[float, float]
    angle: float
    species: int

    def pack(self):
        return self._struct.pack(*self.position, self.angle, self.species)

    @classmethod
    def unpack(cls, buffer, offset=0):
        data = cls._struct.unpack_from(buffer, offset)
        return cls(data[:2], data[2], data[3])

@dataclass
class SpeciesProperties:
    _struct: ClassVar[Struct] = Struct('=8fi12x')

    move_speed: float
    turn_speed: float
    sensor_angle_deg: float
    sensor_offset_dst: float
    color: Tuple[float, float, float, float]
    sensor_size: int

    def pack(self):
        return self._struct.pack(
            self.move_speed,
            self.turn_speed,
            self.sensor_angle_deg,
            self.sensor_offset_dst,
            *self.color,
            self.sensor_size
        )
    
    @classmethod
    def unpack(cls, buffer, offset=0):
        data = cls._struct.unpack_from(buffer, offset)
        return cls(data[0], data[1], data[2], data[3], data[4:8], data[8])
