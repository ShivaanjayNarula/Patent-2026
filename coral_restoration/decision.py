from dataclasses import dataclass, field
from typing import List, Tuple

from .config import SystemConfig
from .types import Classification, CoralClass, Pose


@dataclass
class TreatedLocationMemory:
    treated: List[Tuple[float, float]] = field(default_factory=list)

    def is_treated(self, x: float, y: float, radius: float) -> bool:
        for tx, ty in self.treated:
            dx = x - tx
            dy = y - ty
            if (dx * dx + dy * dy) ** 0.5 <= radius:
                return True
        return False

    def mark_treated(self, x: float, y: float) -> None:
        self.treated.append((x, y))


@dataclass
class DecisionLogic:
    cfg: SystemConfig
    memory: TreatedLocationMemory

    def is_safe(self, pose: Pose) -> bool:
        return (
            self.cfg.min_depth_m <= pose.depth_m <= self.cfg.max_depth_m
            and pose.tilt_deg <= self.cfg.max_tilt_deg
        )

    def should_deploy(self, cls: Classification, pose: Pose) -> bool:
        if cls.label == CoralClass.HEALTHY:
            return False
        if cls.confidence < self.cfg.confidence_threshold:
            return False
        if not self.is_safe(pose):
            return False
        if self.memory.is_treated(pose.x_m, pose.y_m, self.cfg.treated_radius_m):
            return False
        return True
