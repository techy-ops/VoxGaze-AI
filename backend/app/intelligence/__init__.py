"""
Accessibility Intelligence Layer for VoxGaze AI.
Converts low-level AI detections into high-level user intentions and commands.
"""
from app.intelligence.blink_command_processor import BlinkCommandProcessor
from app.intelligence.eye_command_processor import EyeCommandProcessor
from app.intelligence.gesture_command_processor import GestureCommandProcessor
from app.intelligence.context_engine import ContextEngine
from app.intelligence.phrase_predictor import PhrasePredictor
from app.intelligence.user_behavior import UserBehaviorManager
from app.intelligence.history_manager import HistoryManager
from app.intelligence.rules_engine import RulesEngine
from app.intelligence.intent_engine import IntentEngine
from app.intelligence.accessibility_engine import AccessibilityEngine

__all__ = [
    "BlinkCommandProcessor",
    "EyeCommandProcessor",
    "GestureCommandProcessor",
    "ContextEngine",
    "PhrasePredictor",
    "UserBehaviorManager",
    "HistoryManager",
    "RulesEngine",
    "IntentEngine",
    "AccessibilityEngine",
]
