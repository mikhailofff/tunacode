"""Tool-specific exceptions for TunaCode CLI.

This module defines exceptions used by tools for control flow and error handling.
These replace pydantic-ai's ModelRetry for provider-agnostic tool retry logic.
"""

from tunacode.exceptions import TunaCodeError


class ToolRetryError(TunaCodeError):
    """Signal that the model should retry with corrected parameters.

    Raise this exception from a tool when:
    - The model provided invalid arguments that can be corrected
    - A recoverable error occurred (e.g., file not found, pattern too broad)
    - The tool wants to give the model a hint for a better approach

    The message will be sent back to the model as feedback for retry.

    This replaces pydantic-ai's ModelRetry exception for provider-agnostic
    tool execution.

    Example:
        @base_tool
        async def read_file(filepath: str) -> str:
            if not Path(filepath).exists():
                raise ToolRetryError(f"File not found: {filepath}. Check the path.")
            return Path(filepath).read_text()
    """

    def __init__(self, message: str) -> None:
        """Initialize with a message to send back to the model.

        Args:
            message: Feedback message for the model to correct its approach.
        """
        self.message = message
        super().__init__(message)


__all__ = ["ToolRetryError"]
