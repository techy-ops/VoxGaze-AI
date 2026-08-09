from dataclasses import dataclass
from typing import Optional


@dataclass
class EyeTrackingFrame:
    """Domain model representing processed eye-tracking gaze state."""
    session_id: str
    direction: str
    blink: bool
    confidence: float = 1.0
    x_coordinate: Optional[float] = None
    y_coordinate: Optional[float] = None
