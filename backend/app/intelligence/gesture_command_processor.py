"""
Gesture Command Processor module for mapping hand gesture detections to user actions.
"""
from typing import Dict, Any, Optional


class GestureCommandProcessor:
    """
    Processes hand gesture inputs (Open Palm, Closed Fist, Thumbs Up, Pointing, Pinch)
    into standard accessibility commands.
    """

    DEFAULT_GESTURE_MAP = {
        "open_palm": {"intent": "OPEN_MENU", "command": "TOGGLE_MENU", "default_confidence": 0.93},
        "closed_fist": {"intent": "CANCEL", "command": "CANCEL_ACTION", "default_confidence": 0.92},
        "thumbs_up": {"intent": "CONFIRM", "command": "CONFIRM_SELECTION", "default_confidence": 0.95},
        "pointing": {"intent": "SELECT", "command": "POINT_TARGET", "default_confidence": 0.90},
        "pinch": {"intent": "SELECT", "command": "PINCH_CLICK", "default_confidence": 0.91},
    }

    def __init__(self, custom_mappings: Optional[Dict[str, Dict[str, Any]]] = None):
        self.gesture_map = dict(self.DEFAULT_GESTURE_MAP)
        if custom_mappings:
            self.gesture_map.update(custom_mappings)

    def process_gesture(
        self,
        gesture_data: Dict[str, Any],
        confidence_threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Maps hand gesture payload to intent and command details.

        Returns:
            Dict containing intent, command, confidence, gesture_name, reason.
        """
        raw_name = str(
            gesture_data.get("name")
            or gesture_data.get("gesture_name")
            or gesture_data.get("gesture")
            or ""
        ).lower().replace(" ", "_")

        conf = float(gesture_data.get("confidence", 0.90))

        if not raw_name or conf < confidence_threshold:
            return {
                "intent": None,
                "command": None,
                "confidence": conf,
                "gesture_name": raw_name,
                "reason": f"Gesture '{raw_name}' below confidence threshold ({conf:.2f} < {confidence_threshold:.2f})",
            }

        # Match exact gesture or substring
        matched = None
        for key in self.gesture_map:
            if key in raw_name or raw_name in key:
                matched = self.gesture_map[key]
                break

        if matched:
            return {
                "intent": matched["intent"],
                "command": matched["command"],
                "confidence": min(1.0, conf),
                "gesture_name": raw_name,
                "reason": f"Mapped gesture '{raw_name}' to intent {matched['intent']}",
            }

        return {
            "intent": "CUSTOM_GESTURE",
            "command": f"ACTION_{raw_name.upper()}",
            "confidence": min(1.0, conf),
            "gesture_name": raw_name,
            "reason": f"Unrecognized standard gesture '{raw_name}', using generic fallback",
        }
