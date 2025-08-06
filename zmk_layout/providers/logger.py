"""Logger provider protocol for layout domain abstraction."""

from __future__ import annotations

from typing import Protocol


class LayoutLogger(Protocol):
    """Protocol for providing logging functionality to the layout domain.

    This abstraction enables the layout library to operate independently
    of the specific logging system implementation (structured logging, etc.).
    """

    def info(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        """Log an informational message.

        Args:
            message: The message to log
            **kwargs: Additional structured logging fields
        """
        ...

    def error(
        self,
        message: str,
        exc_info: bool = False,
        **kwargs: str | int | float | bool | None,
    ) -> None:
        """Log an error message.

        Args:
            message: The error message to log
            exc_info: Whether to include exception traceback information
            **kwargs: Additional structured logging fields
        """
        ...

    def warning(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        """Log a warning message.

        Args:
            message: The warning message to log
            **kwargs: Additional structured logging fields
        """
        ...

    def debug(self, message: str, **kwargs: str | int | float | bool | None) -> None:
        """Log a debug message.

        Args:
            message: The debug message to log
            **kwargs: Additional structured logging fields
        """
        ...

    def exception(
        self, message: str, **kwargs: str | int | float | bool | None
    ) -> None:
        """Log an exception with traceback.

        Args:
            message: The exception message to log
            **kwargs: Additional structured logging fields
        """
        ...
