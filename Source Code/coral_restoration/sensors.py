from dataclasses import dataclass
from typing import List, Optional
import random

from .types import Event, Pose


@dataclass
class EventCamera:
    width: int = 240
    height: int = 180
    rng: Optional[random.Random] = None

    def read_events(self, max_events: int, ts_ms: int) -> List[Event]:
        rng = self.rng or random
        events: List[Event] = []
        for _ in range(max_events):
            x = rng.randint(0, self.width - 1)
            y = rng.randint(0, self.height - 1)
            polarity = rng.choice([1, -1])
            events.append(Event(x=x, y=y, polarity=polarity, ts_ms=ts_ms))
        return events


@dataclass
class DepthIMU:
    rng: Optional[random.Random] = None

    def read_pose(self) -> Pose:
        rng = self.rng or random
        # Simulate stable hover with slight noise.
        return Pose(
            x_m=rng.uniform(0, 50),
            y_m=rng.uniform(0, 50),
            depth_m=rng.uniform(5, 25),
            tilt_deg=rng.uniform(0, 8),
        )


@dataclass
class JamSensor:
    rng: Optional[random.Random] = None

    def is_jammed(self) -> bool:
        rng = self.rng or random
        return rng.random() < 0.03


@dataclass
class PodCounter:
    rng: Optional[random.Random] = None

    def count_released(self, intended: int) -> int:
        rng = self.rng or random
        # Simulate accurate count with rare off-by-one.
        if rng.random() < 0.05:
            return max(0, intended - 1)
        return intended


@dataclass
class ParticleSensor:
    rng: Optional[random.Random] = None

    def read_turbidity(self) -> float:
        rng = self.rng or random
        return rng.uniform(0.0, 1.0)


@dataclass
class MacroCamera:
    rng: Optional[random.Random] = None

    def detect_spawning(self) -> bool:
        rng = self.rng or random
        return rng.random() < 0.08
