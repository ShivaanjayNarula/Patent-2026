from dataclasses import dataclass


@dataclass(frozen=True)
class SystemConfig:
    confidence_threshold: float = 0.82
    pods_per_deployment: int = 10
    grid_size: int = 10  # 10x10
    max_events_per_tick: int = 120
    treated_radius_m: float = 0.75
    max_depth_m: float = 40.0
    min_depth_m: float = 2.0
    max_tilt_deg: float = 12.0
    jam_retry_limit: int = 2
    rng_seed: int = 1337
