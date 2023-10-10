"""Utilities for the memo package."""


import ctypes
import json
from pathlib import Path

from html2text import HTML2Text


# clipboard, Windows only
def copy_to_clipboard(text: str) -> None:
    """Copy the given text to the clipboard.

    Args:
        text: The text to copy to the clipboard.
    """
    ctypes.windll.user32.OpenClipboard(0)
    ctypes.windll.user32.EmptyClipboard()
    ctypes.windll.user32.SetClipboardData(1, ctypes.create_string_buffer(text.encode("utf-8")))
    ctypes.windll.user32.CloseClipboard()


def get_clipboard_text() -> str:
    """Get the text from the clipboard.

    Returns:
        The text from the clipboard.
    """
    try:
        ctypes.windll.user32.OpenClipboard(0)
        text = ctypes.windll.user32.GetClipboardData(1).decode("utf-8")
    finally:
        ctypes.windll.user32.CloseClipboard()
    return text


class HTML2MarkdownParser:
    """Convert HTML to Markdown.

    Methods:
        convert: Convert the given HTML to Markdown.
    """

    def __init__(
        self,
    ) -> None:
        """Initialize the converter."""
        self._html2text_converter = HTML2Text()

    def update_params(self, params: dict) -> None:
        """Update the parameters of the converter."""
        for param, value in params.items():
            setattr(self._html2text_converter, param, value)

    def parse(self, html: str) -> str:
        """Convert the given HTML to Markdown."""
        return self._html2text_converter.handle(html).strip()


class Settings:
    """Settings cllas."""

    def __init__(self, path: Path) -> None:
        """Create or open a settings file at the given path.

        Args:
            path: The path to the settings file.
        """
        self._path = path
        if not path.exists():
            raise FileNotFoundError(f"Settings file not found at {path}")
        self._settings = json.loads(path.read_text(encoding="utf-8"))

    @classmethod
    def create(cls, path: Path, default_settings: dict) -> "Settings":
        """Create a new settings file at the given path.

        Args:
            path: The path to the settings file.
            default_settings: The default settings.

        Returns:
            The created settings file.
        """
        path.write_text(
            json.dumps(default_settings, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )

    def save(self):
        """Save the settings to the settings file."""
        self._path.write_text(json.dumps(self._settings, ensure_ascii=False, indent=4), encoding="utf-8")

    def __getitem__(self, key):
        """Get the value of the given key."""
        return self._settings[key]

    def __setitem__(self, key, value):
        """Set the value of the given key."""
        self._settings[key] = value
        self.save()

    def __contains__(self, key):
        """Check if the given key is in the settings."""
        return key in self._settings

    def __repr__(self):
        """Return the representation of the settings."""
        return f"Settings({self._settings})"

    def __str__(self):
        """Return the string representation of the settings."""
        return str(self._settings)

    def __iter__(self):
        """Return an iterator over the settings."""
        return iter(self._settings)

    def __len__(self):
        """Return the number of settings."""
        return len(self._settings)

    def __delitem__(self, key):
        """Delete the given key."""
        del self._settings[key]
        self.save()
