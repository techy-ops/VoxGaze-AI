from dataclasses import dataclass
from typing import Optional


@dataclass
class GPTConversationContext:
    """Domain model for GPT accessibility query context."""
    user_id: str
    prompt: str
    response_text: str
    tokens_used: int = 42
    model_name: str = "gpt-4o-mini"
