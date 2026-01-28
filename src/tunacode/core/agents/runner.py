"""Agent runner protocols for TunaCode CLI.

This module defines the abstract interfaces for agent execution, providing
a clean boundary between the orchestration logic and the underlying LLM
provider implementation (currently pydantic-ai).

These protocols enable:
1. Provider-agnostic agent execution
2. Testing with mock implementations
3. Future migration away from pydantic-ai

The current implementation uses pydantic-ai, but these protocols define
what we actually need from an agent runner.
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

# =============================================================================
# Node Types
# =============================================================================


class NodeKind:
    """Discriminator for agent iteration node types."""

    MODEL_REQUEST = "model-request"
    MODEL_RESPONSE = "model-response"
    TOOL_CALL = "tool-call"
    TOOL_RETURN = "tool-return"
    END = "end"


@dataclass(frozen=True, slots=True)
class ToolCallInfo:
    """Information about a tool call within a node."""

    tool_call_id: str
    tool_name: str
    args: dict[str, Any]


@dataclass(slots=True)
class AgentNode:
    """A single node in the agent iteration sequence.

    This is the canonical representation of what we get from iterating
    over an agent run. It abstracts away pydantic-ai's node types.
    """

    kind: str
    content: str = ""
    tool_calls: list[ToolCallInfo] = field(default_factory=list)
    tool_returns: dict[str, str] = field(default_factory=dict)
    thought: str | None = None
    raw: Any = None  # Original provider-specific node for escape hatch

    @property
    def is_model_request(self) -> bool:
        """Check if this is a model request node (streamable)."""
        return self.kind == NodeKind.MODEL_REQUEST

    @property
    def is_end(self) -> bool:
        """Check if this is the final node."""
        return self.kind == NodeKind.END

    @property
    def has_tool_calls(self) -> bool:
        """Check if this node contains tool calls."""
        return bool(self.tool_calls)


# =============================================================================
# Streaming Types
# =============================================================================


@dataclass(frozen=True, slots=True)
class TextDelta:
    """A streaming text delta from the model."""

    content: str


@dataclass(frozen=True, slots=True)
class ToolCallDelta:
    """A streaming tool call delta (partial args)."""

    tool_call_id: str
    tool_name: str | None = None
    args_delta: str | None = None


StreamDelta = TextDelta | ToolCallDelta


# =============================================================================
# Protocols
# =============================================================================


@runtime_checkable
class StreamContextProtocol(Protocol):
    """Protocol for streaming context from a model request node.

    Usage:
        async with node.stream(ctx) as stream:
            async for delta in stream:
                # Process TextDelta or ToolCallDelta
    """

    def __aiter__(self) -> AsyncIterator[StreamDelta]:
        """Iterate over stream deltas."""
        ...

    async def __anext__(self) -> StreamDelta:
        """Get next stream delta."""
        ...


@runtime_checkable
class AgentRunProtocol(Protocol):
    """Protocol for an active agent run.

    This is what you get from `agent.iter(message)`. It provides:
    - Async iteration over nodes
    - Access to the run context
    - Access to all messages after completion
    """

    @property
    def ctx(self) -> Any:
        """Get the run context (provider-specific)."""
        ...

    def all_messages(self) -> list[Any]:
        """Get all messages from this run.

        Returns the authoritative message history after the run completes.
        """
        ...

    def __aiter__(self) -> AsyncIterator[Any]:
        """Iterate over nodes in the run."""
        ...


@runtime_checkable
class AgentRunnerProtocol(Protocol):
    """Protocol for an agent runner.

    This is the main interface for executing agent requests.
    It abstracts away the underlying provider (pydantic-ai, etc).
    """

    @asynccontextmanager
    @abstractmethod
    async def iter(
        self,
        message: str,
        message_history: list[Any] | None = None,
    ) -> AsyncIterator[AgentRunProtocol]:
        """Start an iterative agent run.

        Args:
            message: The user message to process
            message_history: Optional conversation history

        Yields:
            AgentRunProtocol for iterating over the run

        Usage:
            async with runner.iter("Hello") as run:
                async for node in run:
                    # Process node
        """
        ...

    @staticmethod
    @abstractmethod
    def is_model_request_node(node: Any) -> bool:
        """Check if a node is a model request (streamable).

        This is a static method because pydantic-ai uses Agent.is_model_request_node().
        """
        ...


# =============================================================================
# Configuration Types
# =============================================================================


@dataclass(frozen=True, slots=True)
class RunnerConfig:
    """Configuration for creating an agent runner.

    This captures all the settings needed to create a runner,
    abstracting away provider-specific configuration.
    """

    model: str
    system_prompt: str
    tools: list[Any]  # Tool definitions (provider-specific format for now)
    max_tokens: int | None = None
    max_retries: int = 3
    request_delay: float = 0.0
    strict_validation: bool = False


@dataclass(slots=True)
class RunResult:
    """Result from a completed agent run.

    Provides a clean interface to run results without exposing
    provider-specific details.
    """

    messages: list[Any]
    output: str | None = None
    tool_calls_made: int = 0
    usage: dict[str, int] | None = None


# =============================================================================
# Factory Protocol
# =============================================================================


@runtime_checkable
class RunnerFactoryProtocol(Protocol):
    """Protocol for creating agent runners.

    This allows swapping out the underlying provider implementation.
    """

    def create_runner(self, config: RunnerConfig) -> AgentRunnerProtocol:
        """Create a new agent runner with the given configuration."""
        ...


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Node types
    "NodeKind",
    "ToolCallInfo",
    "AgentNode",
    # Streaming types
    "TextDelta",
    "ToolCallDelta",
    "StreamDelta",
    # Protocols
    "StreamContextProtocol",
    "AgentRunProtocol",
    "AgentRunnerProtocol",
    "RunnerFactoryProtocol",
    # Configuration
    "RunnerConfig",
    "RunResult",
]
