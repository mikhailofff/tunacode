"""Pydantic-AI type wrappers for TunaCode CLI.

Isolates pydantic-ai dependencies to a single module for easier
migration if the underlying library changes.

NOTE: This module is being phased out. New code should import from:
- tunacode.types.usage for NormalizedUsage, normalize_request_usage
- tunacode.types.streaming for streaming event types
- tunacode.types.canonical for message types
"""

from typing import Any

from pydantic_ai import Agent
from pydantic_ai.messages import ModelRequest as _ModelRequest
from pydantic_ai.messages import ToolReturnPart

# Re-export usage types from canonical location for backward compatibility
from tunacode.types.usage import (
    NormalizedUsage,
    normalize_request_usage,
)

# Re-export with stable names (ugly but better than what we had before)
PydanticAgent = Agent
MessagePart = ToolReturnPart | Any
ModelRequest = _ModelRequest
ModelResponse = Any

AgentResponse = Any
MessageHistory = list[Any]
AgentRun = Any


__all__ = [
    "AgentResponse",
    "AgentRun",
    "MessageHistory",
    "MessagePart",
    "ModelRequest",
    "ModelResponse",
    "PydanticAgent",
    "NormalizedUsage",
    "normalize_request_usage",
]
