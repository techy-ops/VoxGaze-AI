from typing import List, Dict, Any, Optional


def calculate_confidence_score(scores: List[float], default_score: float = 0.95) -> float:
    """
    Compute aggregate confidence score from a list of model probability metrics.
    """
    if not scores:
        return default_score
    valid_scores = [s for s in scores if 0.0 <= s <= 1.0]
    if not valid_scores:
        return default_score
    return round(float(sum(valid_scores) / len(valid_scores)), 4)


def validate_confidence_threshold(confidence: float, threshold: float = 0.5) -> bool:
    """
    Check whether detection confidence satisfies the required confidence threshold.
    """
    return confidence >= threshold
