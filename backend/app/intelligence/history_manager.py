"""
History Manager module for recording and querying backend interaction history.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from collections import deque


class HistoryManager:
    """
    Records interaction events, AI decision logs, phrase predictions, and emergency SOS activations.
    """

    def __init__(self, max_history: int = 200):
        self.max_history = max_history
        self.recent_commands: deque = deque(maxlen=max_history)
        self.ai_decisions: deque = deque(maxlen=max_history)
        self.predictions_history: deque = deque(maxlen=max_history)
        self.emergency_activations: deque = deque(maxlen=max_history)

    def record_command(self, command: str, intent: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Record executed command event."""
        event = {
            "type": "command",
            "command": command,
            "intent": intent,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.recent_commands.appendleft(event)
        return event

    def record_decision(
        self,
        intent: str,
        confidence: float,
        command: str,
        reason: str,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record AI decision with input context and reasoning."""
        event = {
            "type": "ai_decision",
            "intent": intent,
            "confidence": confidence,
            "command": command,
            "reason": reason,
            "inputs": inputs or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.ai_decisions.appendleft(event)
        return event

    def record_prediction(self, phrase: str, source: str, score: float) -> Dict[str, Any]:
        """Record selected or generated phrase prediction."""
        event = {
            "type": "prediction",
            "phrase": phrase,
            "source": source,
            "score": score,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.predictions_history.appendleft(event)
        return event

    def record_emergency(self, trigger_source: str, reason: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Record SOS emergency trigger event."""
        event = {
            "type": "emergency",
            "trigger_source": trigger_source,
            "reason": reason,
            "payload": payload or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.emergency_activations.appendleft(event)
        return event

    def get_history(self, limit: int = 50, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves interaction history filtered by category.
        Categories: 'command', 'decision', 'prediction', 'emergency', or None for all combined.
        """
        if category == "command":
            items = list(self.recent_commands)
        elif category == "decision":
            items = list(self.ai_decisions)
        elif category == "prediction":
            items = list(self.predictions_history)
        elif category == "emergency":
            items = list(self.emergency_activations)
        else:
            combined = (
                list(self.recent_commands)
                + list(self.ai_decisions)
                + list(self.predictions_history)
                + list(self.emergency_activations)
            )
            combined.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            items = combined

        return items[:limit]

    def clear_history(self) -> None:
        """Clears all stored history logs."""
        self.recent_commands.clear()
        self.ai_decisions.clear()
        self.predictions_history.clear()
        self.emergency_activations.clear()
