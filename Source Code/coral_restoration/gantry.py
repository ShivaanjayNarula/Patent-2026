from dataclasses import dataclass
from typing import Tuple


@dataclass
class Gantry:
    grid_size: int = 10
    x_idx: int = 0
    y_idx: int = 0

    def index_to(self, x_idx: int, y_idx: int) -> Tuple[int, int]:
        if not (0 <= x_idx < self.grid_size and 0 <= y_idx < self.grid_size):
            raise ValueError("Index out of range")
        self.x_idx = x_idx
        self.y_idx = y_idx
        return self.x_idx, self.y_idx
