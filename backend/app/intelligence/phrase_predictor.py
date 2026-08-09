"""
Phrase Predictor module for managing sentence completion, context-aware suggestions, favorites, and pinned phrases.
"""
from typing import List, Dict, Any, Optional
from collections import Counter, deque


class PhrasePredictor:
    """
    Manages sentence & phrase prediction for fast AAC (Augmentative and Alternative Communication).
    """

    DEFAULT_SCREEN_SUGGESTIONS = {
        "home": ["Hello", "How are you?", "Thank you", "Yes", "No"],
        "medical": ["I am in pain", "Call nurse", "I need water", "Adjust bed", "Emergency"],
        "keyboard": ["Next word", "Delete character", "Clear text", "Space", "Enter"],
        "emergency": ["I need immediate help", "Call emergency contact", "Medical assistance needed"],
    }

    DEFAULT_PINNED = [
        "I need help",
        "Yes",
        "No",
        "Thank you",
        "Please wait",
    ]

    def __init__(self):
        self.frequently_used: Counter = Counter()
        self.recently_used: deque = deque(maxlen=30)
        self.favorites: List[str] = ["I am doing well", "Can you help me?", "Good morning"]
        self.pinned_phrases: List[str] = list(self.DEFAULT_PINNED)

        # Seed initial frequent sentences
        for sentence in ["Hello", "Thank you", "Yes", "No", "Call nurse"]:
            self.frequently_used[sentence] += 1

    def record_phrase_usage(self, phrase: str) -> None:
        """Track usage of a spoken/typed phrase for frequency and recency."""
        clean_phrase = phrase.strip()
        if not clean_phrase:
            return
        self.frequently_used[clean_phrase] += 1
        if clean_phrase in self.recently_used:
            self.recently_used.remove(clean_phrase)
        self.recently_used.appendleft(clean_phrase)

    def add_favorite(self, phrase: str) -> None:
        """Add phrase to user favorites list."""
        clean_phrase = phrase.strip()
        if clean_phrase and clean_phrase not in self.favorites:
            self.favorites.append(clean_phrase)

    def remove_favorite(self, phrase: str) -> None:
        """Remove phrase from user favorites list."""
        if phrase in self.favorites:
            self.favorites.remove(phrase)

    def pin_phrase(self, phrase: str) -> None:
        """Pin phrase to quick access list."""
        clean_phrase = phrase.strip()
        if clean_phrase and clean_phrase not in self.pinned_phrases:
            self.pinned_phrases.insert(0, clean_phrase)

    def unpin_phrase(self, phrase: str) -> None:
        """Unpin phrase from quick access list."""
        if phrase in self.pinned_phrases:
            self.pinned_phrases.remove(phrase)

    def get_predictions(
        self,
        prefix: str = "",
        current_screen: str = "home",
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Generates context-aware sentence and phrase suggestions.
        """
        prefix_clean = prefix.strip().lower()
        suggestions: List[Dict[str, Any]] = []
        seen = set()

        def add_item(text: str, source: str, score: float):
            if text and text.lower() not in seen:
                seen.add(text.lower())
                suggestions.append({"phrase": text, "source": source, "score": score})

        # 1. Pinned & Favorites matching prefix
        for p in self.pinned_phrases:
            if not prefix_clean or p.lower().startswith(prefix_clean):
                add_item(p, "pinned", 1.0)

        for f in self.favorites:
            if not prefix_clean or f.lower().startswith(prefix_clean):
                add_item(f, "favorite", 0.9)

        # 2. Context-aware screen suggestions
        screen_phrases = self.DEFAULT_SCREEN_SUGGESTIONS.get(current_screen.lower(), [])
        for s in screen_phrases:
            if not prefix_clean or s.lower().startswith(prefix_clean):
                add_item(s, "context", 0.85)

        # 3. Frequently used phrases
        for phrase, count in self.frequently_used.most_common(10):
            if not prefix_clean or phrase.lower().startswith(prefix_clean):
                add_item(phrase, "frequent", 0.75 + min(0.1, count * 0.01))

        # 4. Recently used phrases
        for r in list(self.recently_used):
            if not prefix_clean or r.lower().startswith(prefix_clean):
                add_item(r, "recent", 0.70)

        # Sort by score and limit
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        return suggestions[:limit]
