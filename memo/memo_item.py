"""The memo module."""

from pathlib import Path

HASHTAGS_LINE_PREFIX = "Hashtags: "


class MemoManipulator:
    """A memo.

    The memo is a text file with markdown syntax.
    The first line is the title of the memo.
    """

    def __init__(self, markdown: str = ""):
        """Initialize a new instance of the Memo class.

        Args:
            markdown (str): the content of the memo.
        """
        self._lines = markdown.strip().splitlines()

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
        if self._lines:
            # first line without markdown syntax
            return self._lines[0].lstrip("# ")
        return ""

    def _find_hashtags_line_index(self):
        """Find the index of the line that contains only hashtags.

        The line must start with HASHTAGS_LINE_PREFIX.

        Returns:
            int: the index of the line that contains only hashtags or -1 if not found.
        """
        # beckward search
        for i in range(len(self._lines) - 1, -1, -1):
            if self._lines[i].startswith(HASHTAGS_LINE_PREFIX):
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
        index = self._find_hashtags_line_index()
        if index >= 0:
            # get the hashtags from the line
            return set(self._lines[index][len(HASHTAGS_LINE_PREFIX) :].split())
        return set()

    def set_hashtags(self, hashtags):
        """Set the hashtags of the memo.

        Args:
            hashtags: the list of hashtags.
        """
        # all hashtags to lowercase
        hashtags = [hashtag.lower() for hashtag in hashtags]
        index = self._find_hashtags_line_index()
        if index < 0:
            # add new line
            self._lines.append("")
            self._lines.append("---")
            self._lines.append("")
            self._lines.append("")
            index = len(self._lines) - 1
        # add hashtags line
        self._lines[index] = HASHTAGS_LINE_PREFIX + " ".join(sorted(hashtags))

    def update_hashtags(self, hashtags):
        """Update the hashtags of the memo.

        Args:
            hashtags: the list of hashtags.
        """
        self.set_hashtags(self.hashtags.union(set(hashtags)))

    def save(self, path: Path):
        """Save the memo to the given path."""
        path.write_text(self.content, encoding="utf-8")
