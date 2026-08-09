"""
User Behavior module for managing calibration profiles and accessibility preferences.
"""
from typing import Dict, Any, Optional


class UserBehaviorManager:
    """
    Stores and updates user-specific calibration, sensitivity preferences, dominant eye, language, and active mode.
    """

    def __init__(self):
        self.profile: Dict[str, Any] = {
            "calibration": {
                "offset_x": 0.0,
                "offset_y": 0.0,
                "grid_size": "3x3",
                "calibrated_at": None,
                "points_calibrated": 9,
            },
            "eye_sensitivity": 0.8,
            "blink_sensitivity": 0.8,
            "dominant_eye": "right",  # left, right, both
            "preferred_language": "en",
            "accessibility_mode": "HYBRID",  # EYE_GAZE, GESTURE, HYBRID, AAC, SWITCH
        }

    def get_profile(self) -> Dict[str, Any]:
        """Retrieve user profile configuration."""
        return dict(self.profile)

    def update_profile(
        self,
        eye_sensitivity: Optional[float] = None,
        blink_sensitivity: Optional[float] = None,
        dominant_eye: Optional[str] = None,
        preferred_language: Optional[str] = None,
        accessibility_mode: Optional[str] = None,
        calibration: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update profile parameters and calibration values."""
        if eye_sensitivity is not None:
            self.profile["eye_sensitivity"] = float(eye_sensitivity)
        if blink_sensitivity is not None:
            self.profile["blink_sensitivity"] = float(blink_sensitivity)
        if dominant_eye is not None:
            self.profile["dominant_eye"] = str(dominant_eye).lower()
        if preferred_language is not None:
            self.profile["preferred_language"] = str(preferred_language).lower()
        if accessibility_mode is not None:
            self.profile["accessibility_mode"] = str(accessibility_mode).upper()
        if calibration is not None:
            self.profile["calibration"].update(calibration)

        return self.get_profile()

    def update_calibration(self, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update explicit calibration profile values."""
        self.profile["calibration"].update(calibration_data)
        if "eye_sensitivity" in calibration_data:
            self.profile["eye_sensitivity"] = float(calibration_data["eye_sensitivity"])
        if "blink_sensitivity" in calibration_data:
            self.profile["blink_sensitivity"] = float(calibration_data["blink_sensitivity"])
        if "dominant_eye" in calibration_data:
            self.profile["dominant_eye"] = str(calibration_data["dominant_eye"]).lower()
        return self.get_profile()
