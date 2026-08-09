import hashlib
from typing import Dict, Any, Optional
from collections import OrderedDict
from app.utils.logger import logger


class AICache:
    """
    LRU Memory cache for storing frame landmark extractions and model inference outputs.
    """
    def __init__(self, max_size: int = 128):
        self.max_size = max_size
        self._cache: OrderedDict[str, Any] = OrderedDict()

    @staticmethod
    def compute_hash(data: bytes) -> str:
        """Compute SHA256 hash digest of input bytes payload."""
        return hashlib.sha256(data).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached result by hash key."""
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key: str, value: Any) -> None:
        """Insert or update entry in LRU cache."""
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        """Clear all entries in memory cache."""
        self._cache.clear()


ai_cache = AICache(max_size=256)
