"""The memo module."""

from datetime import datetime
from pathlib import Path

MAX_FILENAME_LENGTH = 200


class Memo:
    """A memo.

    The memo is a text file with markdown syntax.
    The first line is the title of the memo.
    """

    def __init__(self, content: str = ""):
        """Initialize a new instance of the Memo class.

        Args:
            content (str): the content of the memo.
        """
        self._lines = content.strip().splitlines()

    @classmethod
    def from_path(cls, path: Path):
        """Create a memo from the given path."""
        # only absolute paths are allowed
        return cls(path.read_text(encoding="utf-8"))

    @property
    def content(self):
        """Get the content of the memo."""
        return "\n".join(self._lines)

    @property
    def title(self):
        """Get the title of the memo."""
        if self.lines:
            # first line without markdown syntax
            return self.lines[0].lstrip("# ")
        return ""

    def make_filename(self, with_timestamp=False):
        """Make a filename from the title of the memo.

        The filename is a valid filename without extension.

        Args:
            with_timestamp (bool): if True, the current timestamp is added to the filename.

        Returns:
            str: the filename.
        """
        # filter out invalid characters
        filename = "".join(c for c in self.title if c.isalnum() or c in "._- ()")
        # strip spaces and dots
        filename = filename.strip(" .")
        # limit the filename length
        # delete last word until the filename is short enough
        while len(filename.split()) > 1 and len(filename) > MAX_FILENAME_LENGTH:
            filename = " ".join(filename.split()[:-1])
        if len(filename) > MAX_FILENAME_LENGTH:
            filename = filename[:MAX_FILENAME_LENGTH]
        # add timestamp
        if with_timestamp:
            filename += datetime.now().strftime("-%Y-%m-%d-%H-%M-%S")  # noqa: DTZ005
        return filename

    def _find_hashtags_line_index(self):
        """Find the index of the line that contains only hashtags.

        The line must contain only hashtags and spaces.

        Returns:
            int: the index of the line that contains only hashtags or -1 if not found.
        """
        # beckward search
        for i in range(len(self._lines) - 1, -1, -1):
            # all words in the line must start with #
            if all(word.startswith("#") for word in self.lines[i].strip().split()):
                return i
        return -1

    def has_hashtags(self):
        """Check if the memo has hashtags.

        Returns:
            bool: True if the memo has hashtags, False otherwise.
        """
        return self._find_hashtags_line_index() >= 0

    @property
    def hashtags(self):
        """Get the hashtags from the memo.

        Returns:
            set: the list of hashtags.
        """
        index = self._find_hashtags_line_index(self._lines)
        if index >= 0:
            # get the hashtags from the line
            return set(self._lines[index].strip().split())
        return set()

    def set_hashtags(self, hashtags):
        """Set the hashtags of the memo.

        Args:
            hashtags: the list of hashtags.
        """
        index = self._find_hashtags_line_index()
        if index < 0:
            # add new line
            self._lines.append("")
            self._lines.append("---")
            self._lines.append("")
            self._lines.append("")
            index = len(self._lines) - 1
        # add hashtags line
        self._lines[index] = " ".join(sorted(set(hashtags)))

    def update_hashtags(self, hashtags):
        """Update the hashtags of the memo.

        Args:
            hashtags: the list of hashtags.
        """
        self.set_hashtags(self.hashtags.union(set(hashtags)))

    def save(self, path: Path):
        """Save the memo to the given path."""
        path.write_text(self.content, encoding="utf-8")
