"""
Context Engine module for maintaining current screen, conversation context, history ring buffers, and active mode.
"""
from typing import Dict, Any, List, Optional
from collections import deque


class ContextEngine:
    """
    Maintains runtime context for intent processing including screen, mode, last commands, and recent actions.
    """

    def __init__(self, history_capacity: int = 20):
        self.current_screen: str = "home"
        self.active_mode: str = "HYBRID"  # EYE_GAZE, GESTURE, AAC, HYBRID, EMERGENCY_MONITOR
        self.conversation_context: Dict[str, Any] = {
            "topic": "general",
            "last_speaker": None,
            "dialogue_history": [],
        }
        self.last_commands: deque = deque(maxlen=history_capacity)
        self.recent_actions: deque = deque(maxlen=history_capacity)

    def set_screen(self, screen_name: str) -> None:
        """Update current screen layout / context."""
        self.current_screen = str(screen_name).lower()

    def set_mode(self, mode_name: str) -> None:
        """Update active accessibility mode."""
        self.active_mode = str(mode_name).upper()

    def update_conversation(self, text: str, speaker: str = "user") -> None:
        """Append to conversation context history."""
        self.conversation_context["last_speaker"] = speaker
        history: List = self.conversation_context.setdefault("dialogue_history", [])
        history.append({"text": text, "speaker": speaker})

    def record_command(self, command: str, intent: str) -> None:
        """Record an executed command into context ring buffer."""
        self.last_commands.append({"command": command, "intent": intent})

    def record_action(self, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Record a UI/System action into recent actions list."""
        self.recent_actions.append({"action": action, "details": details or {}})

    def get_context_summary(self) -> Dict[str, Any]:
        """Return brief summary of active context."""
        return {
            "current_screen": self.current_screen,
            "active_mode": self.active_mode,
            "last_command": self.last_commands[-1]["command"] if self.last_commands else None,
        }

    def get_context(self) -> Dict[str, Any]:
        """Return full snapshot of current runtime context state."""
        return {
            "current_screen": self.current_screen,
            "active_mode": self.active_mode,
            "conversation_context": dict(self.conversation_context),
            "last_commands": list(self.last_commands),
            "recent_actions": list(self.recent_actions),
        }

    def reset(self) -> None:
        """Reset context state to default."""
        self.current_screen = "home"
        self.active_mode = "HYBRID"
        self.conversation_context = {"topic": "general", "last_speaker": None, "dialogue_history": []}
        self.last_commands.clear()
        self.recent_actions.clear()
