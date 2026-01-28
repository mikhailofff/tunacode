"""Usage tracking types for TunaCode CLI.

This module provides provider-agnostic usage tracking types and utilities.
These replace the pydantic-ai specific usage handling.
"""

from dataclasses import dataclass
from typing import Any

# Attribute names for reading from provider-specific usage objects
USAGE_ATTR_REQUEST_TOKENS = "request_tokens"
USAGE_ATTR_RESPONSE_TOKENS = "response_tokens"
USAGE_ATTR_CACHED_TOKENS = "cached_tokens"

DEFAULT_TOKEN_COUNT = 0


@dataclass(frozen=True, slots=True)
class NormalizedUsage:
    """Normalized usage values for provider-agnostic tracking.

    This provides a stable shape for usage data regardless of which
    LLM provider generated it.
    """

    request_tokens: int
    response_tokens: int
    cached_tokens: int

    @property
    def total_tokens(self) -> int:
        """Total tokens used (request + response)."""
        return self.request_tokens + self.response_tokens

    def to_dict(self) -> dict[str, int]:
        """Convert to dict format."""
        return {
            "request_tokens": self.request_tokens,
            "response_tokens": self.response_tokens,
            "cached_tokens": self.cached_tokens,
            "total_tokens": self.total_tokens,
        }


def _read_usage_value(usage: Any, attribute: str) -> int:
    """Read a token count from a usage object, defaulting to 0.

    Args:
        usage: Provider-specific usage object
        attribute: Attribute name to read

    Returns:
        Integer token count, or 0 if not available
    """
    raw_value = getattr(usage, attribute, None)
    return int(raw_value or DEFAULT_TOKEN_COUNT)


def normalize_request_usage(usage: Any | None) -> NormalizedUsage | None:
    """Normalize a provider-specific usage object to canonical form.

    Args:
        usage: Provider-specific usage object (e.g., from pydantic-ai, anthropic SDK)

    Returns:
        NormalizedUsage if usage was provided, None otherwise
    """
    if usage is None:
        return None

    return NormalizedUsage(
        request_tokens=_read_usage_value(usage, USAGE_ATTR_REQUEST_TOKENS),
        response_tokens=_read_usage_value(usage, USAGE_ATTR_RESPONSE_TOKENS),
        cached_tokens=_read_usage_value(usage, USAGE_ATTR_CACHED_TOKENS),
    )


def usage_from_dict(data: dict[str, Any]) -> NormalizedUsage:
    """Create NormalizedUsage from a dict.

    Args:
        data: Dict with token counts (keys may vary)

    Returns:
        NormalizedUsage instance
    """
    # Support both naming conventions
    request = data.get("request_tokens", data.get("prompt_tokens", 0))
    response = data.get("response_tokens", data.get("completion_tokens", 0))
    cached = data.get("cached_tokens", 0)

    return NormalizedUsage(
        request_tokens=int(request),
        response_tokens=int(response),
        cached_tokens=int(cached),
    )


__all__ = [
    "NormalizedUsage",
    "normalize_request_usage",
    "usage_from_dict",
    "USAGE_ATTR_REQUEST_TOKENS",
    "USAGE_ATTR_RESPONSE_TOKENS",
    "USAGE_ATTR_CACHED_TOKENS",
    "DEFAULT_TOKEN_COUNT",
]
