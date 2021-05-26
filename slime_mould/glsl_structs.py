from dataclasses import dataclass
from struct import Struct
from typing import ClassVar, Tuple


@dataclass
class Agent:
    _struct: ClassVar[Struct] = Struct('=fff4x')

    position: Tuple[float, float]
    angle: float

    def pack(self):
        return self._struct.pack(*self.position, self.angle)

    @classmethod
    def unpack(cls, buffer, offset=0):
        data = cls._struct.unpack_from(buffer, offset)
        return cls(data[:2], data[2])
