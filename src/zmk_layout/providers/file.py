"""File provider protocol for layout domain abstraction."""

from pathlib import Path
from typing import Protocol


class FileProvider(Protocol):
    """Protocol for providing file operations to the layout domain.

    This abstraction enables the layout library to operate independently
    of the specific file system implementation.
    """

    def read_text(self, path: Path | str, encoding: str = "utf-8") -> str:
        """Read text content from a file.

        Args:
            path: Path to the file to read
            encoding: Text encoding to use

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If the file doesn't exist
            OSError: If there's an error reading the file
        """
        ...

    def write_text(
        self, path: Path | str, content: str, encoding: str = "utf-8"
    ) -> None:
        """Write text content to a file.

        Args:
            path: Path to the file to write
            content: Content to write
            encoding: Text encoding to use

        Raises:
            OSError: If there's an error writing the file
        """
        ...

    def exists(self, path: Path | str) -> bool:
        """Check if a file or directory exists.

        Args:
            path: Path to check

        Returns:
            True if the path exists, False otherwise
        """
        ...

    def mkdir(self, path: Path | str, parents: bool = False, exist_ok: bool = False) -> None:
        """Create a directory.

        Args:
            path: Directory path to create
            parents: Create parent directories if they don't exist
            exist_ok: Don't raise error if directory already exists

        Raises:
            OSError: If there's an error creating the directory
        """
        ...