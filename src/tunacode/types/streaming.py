"""Streaming types for TunaCode CLI.

This module defines canonical streaming event types that abstract away
provider-specific streaming implementations (pydantic-ai PartDeltaEvent,
anthropic MessageStreamEvent, etc.).

These types represent the streaming primitives needed for real-time
token display in the TUI.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class StreamEventKind(Enum):
    """Discriminator for stream event types."""

    TEXT_DELTA = "text-delta"
    TOOL_CALL_DELTA = "tool-call-delta"
    TOOL_CALL_START = "tool-call-start"
    TOOL_CALL_END = "tool-call-end"
    THOUGHT_DELTA = "thought-delta"
    MESSAGE_START = "message-start"
    MESSAGE_END = "message-end"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class TextDelta:
    """A streaming text content delta.

    This is the most common event - a chunk of text being generated.
    """

    content: str
    kind: StreamEventKind = StreamEventKind.TEXT_DELTA


@dataclass(frozen=True, slots=True)
class ThoughtDelta:
    """A streaming thought/reasoning delta.

    For models that support extended thinking or chain-of-thought.
    """

    content: str
    kind: StreamEventKind = StreamEventKind.THOUGHT_DELTA


@dataclass(frozen=True, slots=True)
class ToolCallStart:
    """Signals the start of a tool call.

    Emitted when the model begins generating a tool call.
    """

    tool_call_id: str
    tool_name: str
    kind: StreamEventKind = StreamEventKind.TOOL_CALL_START


@dataclass(frozen=True, slots=True)
class ToolCallDelta:
    """A streaming tool call arguments delta.

    Contains partial JSON for tool call arguments as they stream in.
    """

    tool_call_id: str
    args_delta: str
    kind: StreamEventKind = StreamEventKind.TOOL_CALL_DELTA


@dataclass(frozen=True, slots=True)
class ToolCallEnd:
    """Signals the end of a tool call.

    Emitted when tool call arguments are complete.
    """

    tool_call_id: str
    tool_name: str
    args: dict[str, Any]
    kind: StreamEventKind = StreamEventKind.TOOL_CALL_END


@dataclass(frozen=True, slots=True)
class MessageStart:
    """Signals the start of a new message.

    Emitted at the beginning of model response generation.
    """

    message_id: str | None = None
    kind: StreamEventKind = StreamEventKind.MESSAGE_START


@dataclass(frozen=True, slots=True)
class MessageEnd:
    """Signals the end of a message.

    Emitted when the model finishes generating a response.
    """

    message_id: str | None = None
    stop_reason: str | None = None
    kind: StreamEventKind = StreamEventKind.MESSAGE_END


@dataclass(frozen=True, slots=True)
class StreamError:
    """An error during streaming.

    Emitted when an error occurs during stream processing.
    """

    error: str
    recoverable: bool = False
    kind: StreamEventKind = StreamEventKind.ERROR


# Union type for all stream events
StreamEvent = (
    TextDelta
    | ThoughtDelta
    | ToolCallStart
    | ToolCallDelta
    | ToolCallEnd
    | MessageStart
    | MessageEnd
    | StreamError
)


def is_content_delta(event: StreamEvent) -> bool:
    """Check if event contains displayable content."""
    return isinstance(event, TextDelta | ThoughtDelta)


def is_tool_event(event: StreamEvent) -> bool:
    """Check if event is related to tool calls."""
    return isinstance(event, ToolCallStart | ToolCallDelta | ToolCallEnd)


__all__ = [
    # Enums
    "StreamEventKind",
    # Event types
    "TextDelta",
    "ThoughtDelta",
    "ToolCallStart",
    "ToolCallDelta",
    "ToolCallEnd",
    "MessageStart",
    "MessageEnd",
    "StreamError",
    # Union type
    "StreamEvent",
    # Helpers
    "is_content_delta",
    "is_tool_event",
]
