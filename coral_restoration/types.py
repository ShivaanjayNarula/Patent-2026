from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class CoralClass(str, Enum):
    HEALTHY = "healthy"
    DAMAGED = "damaged"
    DECOMPOSED = "decomposed"


@dataclass(frozen=True)
class Event:
    x: int
    y: int
    polarity: int  # +1 or -1
    ts_ms: int


@dataclass(frozen=True)
class Pose:
    x_m: float
    y_m: float
    depth_m: float
    tilt_deg: float


@dataclass(frozen=True)
class Classification:
    label: CoralClass
    confidence: float
    roi: Tuple[int, int, int, int]  # x, y, w, h in sensor coords
