"""
Intent Engine module for synthesizing multi-modal detections and context into actionable user intentions.
"""
from typing import Dict, Any, Optional, List
from app.intelligence.blink_command_processor import BlinkCommandProcessor
from app.intelligence.eye_command_processor import EyeCommandProcessor
from app.intelligence.gesture_command_processor import GestureCommandProcessor
from app.intelligence.context_engine import ContextEngine
from app.intelligence.phrase_predictor import PhrasePredictor
from app.intelligence.user_behavior import UserBehaviorManager
from app.intelligence.history_manager import HistoryManager
from app.intelligence.rules_engine import RulesEngine


class IntentEngine:
    """
    Synthesizes low-level AI detections (Eye Tracking, Blink, Hand Gesture, Lip Reading, Context)
    into high-level user intentions and commands.
    """

    def __init__(
        self,
        blink_processor: Optional[BlinkCommandProcessor] = None,
        eye_processor: Optional[EyeCommandProcessor] = None,
        gesture_processor: Optional[GestureCommandProcessor] = None,
        context_engine: Optional[ContextEngine] = None,
        phrase_predictor: Optional[PhrasePredictor] = None,
        user_behavior: Optional[UserBehaviorManager] = None,
        history_manager: Optional[HistoryManager] = None,
        rules_engine: Optional[RulesEngine] = None,
    ):
        self.blink_processor = blink_processor or BlinkCommandProcessor()
        self.eye_processor = eye_processor or EyeCommandProcessor()
        self.gesture_processor = gesture_processor or GestureCommandProcessor()
        self.context_engine = context_engine or ContextEngine()
        self.phrase_predictor = phrase_predictor or PhrasePredictor()
        self.user_behavior = user_behavior or UserBehaviorManager()
        self.history_manager = history_manager or HistoryManager()
        self.rules_engine = rules_engine or RulesEngine()

    def process_intent(
        self,
        eye_tracking: Optional[Dict[str, Any]] = None,
        blink: Optional[Dict[str, Any]] = None,
        gesture: Optional[Dict[str, Any]] = None,
        lip_reading: Optional[Dict[str, Any]] = None,
        context_override: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Main entry point to determine high-level user intent from raw detections.
        """
        # Apply context overrides if provided
        if context_override:
            if "current_screen" in context_override:
                self.context_engine.set_screen(context_override["current_screen"])
            if "active_mode" in context_override:
                self.context_engine.set_mode(context_override["active_mode"])

        user_profile = self.user_behavior.get_profile()
        current_context = self.context_engine.get_context()

        # 1. Rule Engine Evaluation (highest priority for multi-modal combos like SOS)
        rule_match = self.rules_engine.evaluate_rules(
            eye_data=eye_tracking,
            blink_data=blink,
            gesture_data=gesture,
            lip_data=lip_reading,
            context=current_context,
        )
        if rule_match:
            intent = rule_match["intent"]
            command = rule_match["command"]
            confidence = rule_match["confidence"]
            reason = rule_match["reason"]

            if intent == "SOS_TRIGGER":
                self.history_manager.record_emergency(
                    trigger_source="rules_engine",
                    reason=reason,
                    payload={"rule_id": rule_match.get("rule_id")},
                )

            self._record_decision_and_context(intent, confidence, command, reason, eye_tracking, blink, gesture, lip_reading)
            return self._build_result(intent, confidence, command, reason, current_context)

        # 2. Evaluate Lip Reading (e.g. spoken/typed words, typing characters)
        if lip_reading and (lip_reading.get("detected_text") or lip_reading.get("phoneme")):
            text = str(lip_reading.get("detected_text", "")).strip()
            phoneme = str(lip_reading.get("phoneme", "")).strip()

            if text.lower() == "delete":
                intent = "DELETE_CHARACTER"
                command = "ACTION_DELETE"
                reason = "Lip reading detected 'delete' request"
            elif text.lower() in ["next", "next word"]:
                intent = "NEXT_WORD"
                command = "ACTION_NEXT_WORD"
                reason = "Lip reading detected 'next word' request"
            elif text.lower() in ["prev", "previous", "previous word"]:
                intent = "PREVIOUS_WORD"
                command = "ACTION_PREVIOUS_WORD"
                reason = "Lip reading detected 'previous word' request"
            elif text:
                intent = "TYPE_CHARACTER" if len(text) == 1 else "SPEAK_PHRASE"
                command = f"TYPE_{text.upper()}" if len(text) == 1 else f"SPEAK_{text}"
                reason = f"Lip reading recognized text: '{text}'"
                self.phrase_predictor.record_phrase_usage(text)
            else:
                intent = "TYPE_CHARACTER"
                command = f"TYPE_PHONEME_{phoneme.upper()}"
                reason = f"Lip reading recognized phoneme: '{phoneme}'"

            confidence = float(lip_reading.get("confidence", 0.90))
            self._record_decision_and_context(intent, confidence, command, reason, eye_tracking, blink, gesture, lip_reading)
            return self._build_result(intent, confidence, command, reason, current_context)

        # 3. Evaluate Hand Gestures
        if gesture and (gesture.get("name") or gesture.get("gesture_name")):
            gesture_res = self.gesture_processor.process_gesture(
                gesture_data=gesture,
                confidence_threshold=0.5,
            )
            if gesture_res.get("intent"):
                intent = gesture_res["intent"]
                command = gesture_res["command"]
                confidence = gesture_res["confidence"]
                reason = gesture_res["reason"]
                self._record_decision_and_context(intent, confidence, command, reason, eye_tracking, blink, gesture, lip_reading)
                return self._build_result(intent, confidence, command, reason, current_context)

        # 4. Evaluate Blink Events
        if blink and (blink.get("blink_type") or blink.get("type") or blink.get("duration_ms") or blink.get("count")):
            blink_res = self.blink_processor.process_blink(
                blink_event=blink,
                sensitivity=user_profile.get("blink_sensitivity", 1.0),
            )
            if blink_res.get("intent"):
                intent = blink_res["intent"]
                command = blink_res["command"]
                confidence = blink_res["confidence"]
                reason = blink_res["reason"]
                self._record_decision_and_context(intent, confidence, command, reason, eye_tracking, blink, gesture, lip_reading)
                return self._build_result(intent, confidence, command, reason, current_context)

        # 5. Evaluate Eye Tracking Events
        if eye_tracking and any(k in eye_tracking for k in ["gaze_direction", "direction", "x", "y", "dwell_time_ms"]):
            eye_res = self.eye_processor.process_eye(
                eye_data=eye_tracking,
                calibration_profile=user_profile.get("calibration"),
            )
            if eye_res.get("intent"):
                intent = eye_res["intent"]
                command = eye_res["command"]
                confidence = eye_res["confidence"]
                reason = eye_res["reason"]
                self._record_decision_and_context(intent, confidence, command, reason, eye_tracking, blink, gesture, lip_reading)
                return self._build_result(intent, confidence, command, reason, current_context)

        # 6. Fallback / Default Intent
        intent = "NO_INTENT_DETECTED"
        command = "STANDBY"
        confidence = 0.0
        reason = "No actionable low-level AI signals detected"
        self._record_decision_and_context(intent, confidence, command, reason, eye_tracking, blink, gesture, lip_reading)
        return self._build_result(intent, confidence, command, reason, current_context)

    def _record_decision_and_context(
        self,
        intent: str,
        confidence: float,
        command: str,
        reason: str,
        eye_tracking: Optional[Dict[str, Any]],
        blink: Optional[Dict[str, Any]],
        gesture: Optional[Dict[str, Any]],
        lip_reading: Optional[Dict[str, Any]],
    ):
        inputs = {
            "eye_tracking": eye_tracking,
            "blink": blink,
            "gesture": gesture,
            "lip_reading": lip_reading,
        }
        self.history_manager.record_decision(intent, confidence, command, reason, inputs)
        self.context_engine.record_command(command, intent)

    def _build_result(
        self,
        intent: str,
        confidence: float,
        command: str,
        reason: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        predictions = self.phrase_predictor.get_predictions(
            current_screen=context.get("current_screen", "home"),
            limit=5,
        )
        return {
            "intent": intent,
            "confidence": confidence,
            "command": command,
            "reason": reason,
            "context": context,
            "predictions": predictions,
        }
