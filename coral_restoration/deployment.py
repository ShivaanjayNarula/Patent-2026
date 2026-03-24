from dataclasses import dataclass
from typing import Tuple, Optional
import random

from .gantry import Gantry
from .sensors import JamSensor, PodCounter


@dataclass
class PodDeploymentSystem:
    gantry: Gantry
    jam_sensor: JamSensor
    counter: PodCounter
    rng: Optional[random.Random] = None

    def deploy_pods(self, pods: int, grid_target: Tuple[int, int]) -> Tuple[bool, int]:
        self.gantry.index_to(*grid_target)
        if self.jam_sensor.is_jammed():
            return False, 0
        released = self.counter.count_released(pods)
        success = released == pods
        return success, released

    def select_target(self) -> Tuple[int, int]:
        rng = self.rng or random
        return rng.randint(0, self.gantry.grid_size - 1), rng.randint(0, self.gantry.grid_size - 1)
