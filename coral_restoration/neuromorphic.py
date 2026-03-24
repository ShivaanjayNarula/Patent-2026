from dataclasses import dataclass
from typing import List

from .types import Classification, CoralClass, Event


@dataclass
class SNNProcessor:
    def classify(self, events: List[Event]) -> Classification:
        # Deterministic classifier based on event polarity balance and activity.
        if not events:
            return Classification(label=CoralClass.HEALTHY, confidence=0.5, roi=(0, 0, 0, 0))

        total = len(events)
        pos = sum(1 for e in events if e.polarity > 0)
        neg = total - pos
        balance = (pos - neg) / total  # [-1, 1]

        # Activity is proportional to event density.
        activity = min(1.0, total / 200.0)

        if balance > 0.12:
            label = CoralClass.HEALTHY
            confidence = 0.6 + 0.3 * activity
        elif balance < -0.12:
            label = CoralClass.DECOMPOSED
            confidence = 0.7 + 0.25 * activity
        else:
            label = CoralClass.DAMAGED
            confidence = 0.65 + 0.3 * activity

        # Deterministic ROI based on the centroid of events.
        cx = sum(e.x for e in events) // total
        cy = sum(e.y for e in events) // total
        roi = (max(0, cx - 20), max(0, cy - 15), 40, 30)
        return Classification(label=label, confidence=confidence, roi=roi)
