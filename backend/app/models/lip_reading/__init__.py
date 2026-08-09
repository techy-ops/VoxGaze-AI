from dataclasses import dataclass


@dataclass
class LipReadingResult:
    """Domain model for decoded lip movement transcripts."""
    session_id: str
    transcript: str
    confidence: float
    duration_ms: float
