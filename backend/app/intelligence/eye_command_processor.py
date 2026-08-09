"""
Eye Command Processor module for processing gaze tracking and eye coordinate inputs into user actions.
"""
from typing import Dict, Any, Optional, Tuple


class EyeCommandProcessor:
    """
    Processes eye tracking data into higher-level commands.
    Supports Dwell Selection, Cursor Movement, Screen Zones, Grid Selection, and Calibration Profile adjustments.
    """

    def __init__(
        self,
        dwell_threshold_ms: float = 800.0,
        grid_rows: int = 3,
        grid_cols: int = 3,
        screen_width: int = 1920,
        screen_height: int = 1080,
    ):
        self.dwell_threshold_ms = dwell_threshold_ms
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.screen_width = screen_width
        self.screen_height = screen_height

    def calculate_screen_zone(self, x: float, y: float) -> str:
        """Determines screen quadrant / region from normalized or pixel coordinates (0..1 or 0..width/height)."""
        norm_x = x / self.screen_width if x > 1.0 else x
        norm_y = y / self.screen_height if y > 1.0 else y

        norm_x = max(0.0, min(1.0, norm_x))
        norm_y = max(0.0, min(1.0, norm_y))

        if norm_x < 0.33:
            col_zone = "LEFT"
        elif norm_x > 0.66:
            col_zone = "RIGHT"
        else:
            col_zone = "CENTER"

        if norm_y < 0.33:
            row_zone = "TOP"
        elif norm_y > 0.66:
            row_zone = "BOTTOM"
        else:
            row_zone = "MIDDLE"

        if row_zone == "MIDDLE" and col_zone == "CENTER":
            return "CENTER"
        return f"{row_zone}_{col_zone}"

    def calculate_grid_cell(self, x: float, y: float) -> Tuple[int, int, str]:
        """Calculates 2D matrix grid cell index (row, col, cell_id)."""
        norm_x = x / self.screen_width if x > 1.0 else x
        norm_y = y / self.screen_height if y > 1.0 else y

        norm_x = max(0.0, min(0.999, norm_x))
        norm_y = max(0.0, min(0.999, norm_y))

        row = int(norm_y * self.grid_rows)
        col = int(norm_x * self.grid_cols)
        cell_id = f"R{row + 1}C{col + 1}"
        return row, col, cell_id

    def process_eye(
        self,
        eye_data: Dict[str, Any],
        calibration_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Processes gaze data and applies calibration profile parameters.

        Returns:
            Dict with intent, command, confidence, zone, grid_cell, coordinates, reason.
        """
        profile = calibration_profile or {}
        gaze_dir = str(eye_data.get("gaze_direction", eye_data.get("direction", "center"))).lower()
        dwell_time = float(eye_data.get("dwell_time_ms", eye_data.get("dwell_ms", 0.0)))
        x = float(eye_data.get("x", 0.5))
        y = float(eye_data.get("y", 0.5))
        grid_target = eye_data.get("grid_zone") or eye_data.get("grid_cell")

        # Apply calibration offsets & sensitivities
        offset_x = float(profile.get("offset_x", 0.0))
        offset_y = float(profile.get("offset_y", 0.0))
        sensitivity = float(profile.get("gaze_sensitivity", profile.get("eye_sensitivity", 1.0)))

        calibrated_x = (x + offset_x) * sensitivity
        calibrated_y = (y + offset_y) * sensitivity

        zone = self.calculate_screen_zone(calibrated_x, calibrated_y)
        row, col, calculated_cell = self.calculate_grid_cell(calibrated_x, calibrated_y)
        grid_cell = grid_target or calculated_cell

        # 1. Evaluate Dwell Selection
        scaled_dwell_threshold = self.dwell_threshold_ms / max(0.1, sensitivity)
        if dwell_time >= scaled_dwell_threshold:
            return {
                "intent": "SELECT",
                "command": "DWELL_SELECT",
                "confidence": 0.94,
                "zone": zone,
                "grid_cell": grid_cell,
                "coordinates": {"x": calibrated_x, "y": calibrated_y},
                "dwell_time_ms": dwell_time,
                "reason": f"Dwell threshold exceeded ({dwell_time:.1f}ms >= {scaled_dwell_threshold:.1f}ms): item selected",
            }

        # 2. Evaluate Gaze Directions
        intent_map = {
            "left": ("LOOK_LEFT", "NAVIGATE_LEFT"),
            "right": ("LOOK_RIGHT", "NAVIGATE_RIGHT"),
            "up": ("LOOK_UP", "NAVIGATE_UP"),
            "down": ("LOOK_DOWN", "NAVIGATE_DOWN"),
        }

        if gaze_dir in intent_map:
            intent, cmd = intent_map[gaze_dir]
            return {
                "intent": intent,
                "command": cmd,
                "confidence": 0.91,
                "zone": zone,
                "grid_cell": grid_cell,
                "coordinates": {"x": calibrated_x, "y": calibrated_y},
                "dwell_time_ms": dwell_time,
                "reason": f"Gaze direction oriented towards {gaze_dir.upper()}",
            }

        # 3. Fallback to Cursor Movement
        return {
            "intent": "MOVE_CURSOR",
            "command": "POSITION_CURSOR",
            "confidence": 0.88,
            "zone": zone,
            "grid_cell": grid_cell,
            "coordinates": {"x": calibrated_x, "y": calibrated_y},
            "dwell_time_ms": dwell_time,
            "reason": f"Gaze positioned at zone {zone} grid cell {grid_cell}",
        }
