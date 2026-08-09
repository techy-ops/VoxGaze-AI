"""
Accessibility Engine module acting as master coordinator for the Accessibility Intelligence Layer.
"""
from typing import Dict, Any, Optional, List
from app.intelligence.intent_engine import IntentEngine
from app.intelligence.blink_command_processor import BlinkCommandProcessor
from app.intelligence.eye_command_processor import EyeCommandProcessor
from app.intelligence.gesture_command_processor import GestureCommandProcessor
from app.intelligence.context_engine import ContextEngine
from app.intelligence.phrase_predictor import PhrasePredictor
from app.intelligence.user_behavior import UserBehaviorManager
from app.intelligence.history_manager import HistoryManager
from app.intelligence.rules_engine import RulesEngine


class AccessibilityEngine:
    """
    Master coordinator service for the backend Accessibility Intelligence Layer.
    Provides unified access to intent processing, calibration management, profile retrieval, and interaction history.
    """

    def __init__(self):
        self.blink_processor = BlinkCommandProcessor()
        self.eye_processor = EyeCommandProcessor()
        self.gesture_processor = GestureCommandProcessor()
        self.context_engine = ContextEngine()
        self.phrase_predictor = PhrasePredictor()
        self.user_behavior = UserBehaviorManager()
        self.history_manager = HistoryManager()
        self.rules_engine = RulesEngine()

        self.intent_engine = IntentEngine(
            blink_processor=self.blink_processor,
            eye_processor=self.eye_processor,
            gesture_processor=self.gesture_processor,
            context_engine=self.context_engine,
            phrase_predictor=self.phrase_predictor,
            user_behavior=self.user_behavior,
            history_manager=self.history_manager,
            rules_engine=self.rules_engine,
        )

    def process_intelligence(
        self,
        eye_tracking: Optional[Dict[str, Any]] = None,
        blink: Optional[Dict[str, Any]] = None,
        gesture: Optional[Dict[str, Any]] = None,
        lip_reading: Optional[Dict[str, Any]] = None,
        context_override: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process low-level detection inputs and return high-level user intention, command, and context.
        """
        return self.intent_engine.process_intent(
            eye_tracking=eye_tracking,
            blink=blink,
            gesture=gesture,
            lip_reading=lip_reading,
            context_override=context_override,
        )

    def calibrate(self, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stores and updates user calibration parameters and sensitivities.
        """
        updated_profile = self.user_behavior.update_calibration(calibration_data)
        # Update blink processor thresholds if present
        if "short_blink_max_ms" in calibration_data or "long_blink_min_ms" in calibration_data:
            self.blink_processor.configure_thresholds(
                short_blink_max_ms=calibration_data.get("short_blink_max_ms"),
                long_blink_min_ms=calibration_data.get("long_blink_min_ms"),
                double_blink_gap_max_ms=calibration_data.get("double_blink_gap_max_ms"),
            )
        return updated_profile

    def get_history(self, limit: int = 50, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve interaction history logs.
        """
        return self.history_manager.get_history(limit=limit, category=category)

    def get_profile(self) -> Dict[str, Any]:
        """
        Retrieve current user profile and AI calibration details.
        """
        return self.user_behavior.get_profile()

    def get_phrase_predictions(self, prefix: str = "", screen: str = "home", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve phrase predictions and suggestions.
        """
        return self.phrase_predictor.get_predictions(prefix=prefix, current_screen=screen, limit=limit)


# Global singleton instance of AccessibilityEngine
accessibility_engine = AccessibilityEngine()
