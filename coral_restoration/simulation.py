import time
import random
from dataclasses import dataclass
from typing import Optional

from .config import SystemConfig
from .decision import DecisionLogic, TreatedLocationMemory
from .deployment import PodDeploymentSystem
from .gantry import Gantry
from .logging import MissionLog
from .neuromorphic import SNNProcessor
from .sensors import EventCamera, DepthIMU, JamSensor, PodCounter, ParticleSensor, MacroCamera


@dataclass
class CoralRestorationSystem:
    cfg: SystemConfig
    camera: EventCamera
    imu: DepthIMU
    snn: SNNProcessor
    decision: DecisionLogic
    deployer: PodDeploymentSystem
    log: MissionLog
    particle_sensor: Optional[ParticleSensor] = None
    macro_camera: Optional[MacroCamera] = None

    def tick(self, ts_ms: int) -> None:
        pose = self.imu.read_pose()
        events = self.camera.read_events(self.cfg.max_events_per_tick, ts_ms)
        cls = self.snn.classify(events)

        spawn_detected = False
        if self.particle_sensor and self.macro_camera:
            spawn_detected = self.particle_sensor.read_turbidity() > 0.8 and self.macro_camera.detect_spawning()

        if self.decision.should_deploy(cls, pose):
            target = self.deployer.select_target()
            success, released = self.deployer.deploy_pods(self.cfg.pods_per_deployment, target)
            if success:
                self.decision.memory.mark_treated(pose.x_m, pose.y_m)
            self.log.add(
                {
                    "ts_ms": ts_ms,
                    "action": "deploy",
                    "class": cls.label.value,
                    "confidence": cls.confidence,
                    "pose": pose,
                    "target": target,
                    "pods_released": released,
                    "success": success,
                    "spawn_detected": spawn_detected,
                }
            )
        else:
            self.log.add(
                {
                    "ts_ms": ts_ms,
                    "action": "scan",
                    "class": cls.label.value,
                    "confidence": cls.confidence,
                    "pose": pose,
                    "spawn_detected": spawn_detected,
                }
            )


def build_system() -> CoralRestorationSystem:
    cfg = SystemConfig()
    rng = random.Random(cfg.rng_seed)
    memory = TreatedLocationMemory()
    decision = DecisionLogic(cfg=cfg, memory=memory)

    camera = EventCamera(rng=rng)
    imu = DepthIMU(rng=rng)
    snn = SNNProcessor()
    gantry = Gantry(grid_size=cfg.grid_size)
    deployer = PodDeploymentSystem(
        gantry=gantry,
        jam_sensor=JamSensor(rng=rng),
        counter=PodCounter(rng=rng),
        rng=rng,
    )
    log = MissionLog()

    return CoralRestorationSystem(
        cfg=cfg,
        camera=camera,
        imu=imu,
        snn=snn,
        decision=decision,
        deployer=deployer,
        log=log,
        particle_sensor=ParticleSensor(rng=rng),
        macro_camera=MacroCamera(rng=rng),
    )


def run_simulation(ticks: int = 25, tick_ms: int = 250) -> MissionLog:
    system = build_system()
    ts_ms = int(time.time() * 1000)
    for i in range(ticks):
        system.tick(ts_ms + i * tick_ms)
    return system.log
