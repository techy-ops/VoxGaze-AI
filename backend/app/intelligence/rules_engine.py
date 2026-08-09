"""
Rules Engine module for matching configurable multi-signal trigger rules.
"""
from typing import Dict, Any, List, Optional


class RulesEngine:
    """
    Evaluates multi-modal input signals against configurable rule conditions.
    Supports complex combinations (e.g. Double Blink + Look Left -> Emergency SOS).
    """

    DEFAULT_RULES = [
        {
            "id": "rule_double_blink_look_left_sos",
            "name": "Double Blink + Look Left Emergency SOS",
            "conditions": {
                "blink": ["double", "double_blink"],
                "gaze": ["left", "look_left"],
            },
            "output": {
                "intent": "SOS_TRIGGER",
                "command": "TRIGGER_EMERGENCY_SOS",
                "confidence": 0.99,
                "reason": "Matched Rule: Double Blink + Look Left triggered Emergency SOS",
            },
            "enabled": True,
        },
        {
            "id": "rule_long_blink_closed_fist_cancel",
            "name": "Long Blink + Closed Fist Cancel",
            "conditions": {
                "blink": ["long", "long_blink"],
                "gesture": ["closed_fist"],
            },
            "output": {
                "intent": "CANCEL",
                "command": "CANCEL_CURRENT_ACTION",
                "confidence": 0.96,
                "reason": "Matched Rule: Long Blink + Closed Fist triggered Cancel",
            },
            "enabled": True,
        },
        {
            "id": "rule_open_palm_look_up_menu",
            "name": "Open Palm + Look Up Menu",
            "conditions": {
                "gesture": ["open_palm"],
                "gaze": ["up", "look_up"],
            },
            "output": {
                "intent": "OPEN_MENU",
                "command": "OPEN_MAIN_MENU",
                "confidence": 0.95,
                "reason": "Matched Rule: Open Palm + Look Up triggered Open Menu",
            },
            "enabled": True,
        },
    ]

    def __init__(self, custom_rules: Optional[List[Dict[str, Any]]] = None):
        self.rules: List[Dict[str, Any]] = [dict(r) for r in self.DEFAULT_RULES]
        if custom_rules:
            self.rules.extend(custom_rules)

    def add_rule(self, rule: Dict[str, Any]) -> None:
        """Add a custom rule definition."""
        self.rules.append(rule)

    def evaluate_rules(
        self,
        eye_data: Optional[Dict[str, Any]] = None,
        blink_data: Optional[Dict[str, Any]] = None,
        gesture_data: Optional[Dict[str, Any]] = None,
        lip_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluates active rules against current multi-modal detection signals.

        Returns matching rule output dict if triggered, otherwise None.
        """
        eye = eye_data or {}
        blink = blink_data or {}
        gesture = gesture_data or {}
        lip = lip_data or {}

        gaze_str = str(eye.get("gaze_direction") or eye.get("direction") or "").lower()
        blink_str = str(blink.get("blink_type") or blink.get("type") or "").lower()
        if blink.get("count", 1) >= 2 or blink.get("type") == "double":
            blink_str = "double"
        elif blink.get("type") == "long" or blink.get("duration_ms", 0) >= 500:
            blink_str = "long"

        gesture_str = str(gesture.get("name") or gesture.get("gesture_name") or "").lower().replace(" ", "_")
        lip_str = str(lip.get("detected_text") or lip.get("phoneme") or "").lower()

        for rule in self.rules:
            if not rule.get("enabled", True):
                continue

            conds = rule.get("conditions", {})
            match_all = True

            # Match Gaze Condition
            if "gaze" in conds:
                if not any(target in gaze_str for target in conds["gaze"]):
                    match_all = False

            # Match Blink Condition
            if "blink" in conds:
                if not any(target in blink_str for target in conds["blink"]):
                    match_all = False

            # Match Gesture Condition
            if "gesture" in conds:
                if not any(target in gesture_str for target in conds["gesture"]):
                    match_all = False

            # Match Lip Condition
            if "lip" in conds:
                if not any(target in lip_str for target in conds["lip"]):
                    match_all = False

            if match_all:
                output = dict(rule["output"])
                output["rule_id"] = rule.get("id")
                return output

        return None
