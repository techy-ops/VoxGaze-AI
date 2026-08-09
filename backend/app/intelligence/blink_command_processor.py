"""
Blink Command Processor module for processing blink events into structured commands.
"""
from typing import Dict, Any, Optional, List


class BlinkCommandProcessor:
    """
    Processes eye blink detections into accessibility commands.
    Supports Single Blink, Double Blink, Long Blink, Blink Sequence, and Blink Duration tracking.
    """

    def __init__(
        self,
        short_blink_max_ms: float = 300.0,
        long_blink_min_ms: float = 500.0,
        double_blink_gap_max_ms: float = 400.0,
    ):
        self.short_blink_max_ms = short_blink_max_ms
        self.long_blink_min_ms = long_blink_min_ms
        self.double_blink_gap_max_ms = double_blink_gap_max_ms

    def configure_thresholds(
        self,
        short_blink_max_ms: Optional[float] = None,
        long_blink_min_ms: Optional[float] = None,
        double_blink_gap_max_ms: Optional[float] = None,
    ):
        """Update configurable timing thresholds for blink detection."""
        if short_blink_max_ms is not None:
            self.short_blink_max_ms = short_blink_max_ms
        if long_blink_min_ms is not None:
            self.long_blink_min_ms = long_blink_min_ms
        if double_blink_gap_max_ms is not None:
            self.double_blink_gap_max_ms = double_blink_gap_max_ms

    def process_blink(
        self,
        blink_event: Optional[Dict[str, Any]] = None,
        blink_type: Optional[str] = None,
        duration_ms: Optional[float] = None,
        count: int = 1,
        sequence: Optional[List[str]] = None,
        sensitivity: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Processes blink payload or explicit parameters into intent and action details.

        Returns:
            Dict containing detected_type, intent, command, confidence, duration_ms, reason.
        """
        event = blink_event or {}
        b_type = blink_type or event.get("blink_type") or event.get("type")
        dur = duration_ms if duration_ms is not None else event.get("duration_ms", 0.0)
        cnt = count if count != 1 else event.get("count", 1)
        seq = sequence or event.get("sequence", [])

        # Calculate effective duration scaled by sensitivity
        scaled_duration = dur / max(0.1, sensitivity)

        # 1. Evaluate explicit sequence if present
        if seq and len(seq) > 1:
            seq_str = "-".join(seq)
            return {
                "detected_type": "sequence",
                "intent": "BLINK_SEQUENCE",
                "command": "EXECUTE_SEQUENCE",
                "confidence": 0.95,
                "duration_ms": dur,
                "sequence": seq,
                "reason": f"Detected patterned blink sequence: {seq_str}",
            }

        # 2. Evaluate explicitly provided blink_type or count/duration
        if b_type == "double" or cnt >= 2:
            return {
                "detected_type": "double_blink",
                "intent": "CONFIRM",
                "command": "CONFIRM_ACTION",
                "confidence": 0.94,
                "duration_ms": dur,
                "reason": "Double blink detected: intent set to CONFIRM",
            }

        if b_type == "long" or scaled_duration >= self.long_blink_min_ms:
            return {
                "detected_type": "long_blink",
                "intent": "OPEN_MENU",
                "command": "TOGGLE_MENU",
                "confidence": 0.92,
                "duration_ms": dur,
                "reason": f"Long blink detected ({dur:.1f}ms): intent set to OPEN_MENU",
            }

        if b_type == "single" or scaled_duration > 0:
            return {
                "detected_type": "single_blink",
                "intent": "SELECT",
                "command": "SELECT_ITEM",
                "confidence": 0.90,
                "duration_ms": dur,
                "reason": f"Single blink detected ({dur:.1f}ms): intent set to SELECT",
            }

        return {
            "detected_type": "none",
            "intent": None,
            "command": None,
            "confidence": 0.0,
            "duration_ms": 0.0,
            "reason": "No valid blink action detected",
        }
