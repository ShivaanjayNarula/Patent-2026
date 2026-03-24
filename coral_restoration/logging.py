from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class MissionLog:
    records: List[Dict[str, Any]] = field(default_factory=list)

    def add(self, record: Dict[str, Any]) -> None:
        self.records.append(record)

    def summary(self) -> Dict[str, Any]:
        total = len(self.records)
        deployments = [r for r in self.records if r.get("action") == "deploy"]
        return {
            "total_events": total,
            "deployments": len(deployments),
            "pods_released": sum(r.get("pods_released", 0) for r in deployments),
        }
