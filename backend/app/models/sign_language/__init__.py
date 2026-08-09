from dataclasses import dataclass
from typing import List


@dataclass
class SignLanguageTranslation:
    """Domain model representing sign language gesture translations."""
    session_id: str
    translated_text: str
    gestures_detected: List[str]
    confidence: float
