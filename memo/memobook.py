"""A memo book."""

from datetime import datetime
from gettext import gettext as _
from pathlib import Path

from memo_item import Memo
from templates import memo_template
from utils import HTML2MarkdownParser, Settings

MAX_FILENAME_LENGTH = 200
MEMO_EXTENSION = ".md"

DEFAULT_HTML2TEXT_SETTINGS = {
    "unicode_snob": True,
    "slip_internal_links": True,
    "protect_links": False,
    "ignore_anchors": True,
    "ignore_emphasis": True,
    "mark_code": False,
    "ignore_links": True,
    "ignore_images": True,
    "ignore_tables": False,
}


DEFAULT_MEMOBOOK_SETTINGS = {
    "add_date_hashtag": True,
    "add_bookmark_hashtag": True,
    "add_memobook_name_hashtag": False,
    "html2text": DEFAULT_HTML2TEXT_SETTINGS,
}


class MemoBook:
    """A memo book."""

    def __init__(self, path: Path) -> None:
        """Create or open a memo book at the given path."""
        self._path = path
        self._settings_path = path / ".settings"
        self.settings = Settings(self._settings_path)
        self.html2text_parser = HTML2MarkdownParser()
        self.html2text_parser.update_params(self.settings["html2text"])

    @property
    def path(self) -> Path:
        """The path to the memo book."""
        return self._path

    @property
    def name(self) -> str:
        """The name of the memo book."""
        return self._path.name

    @property
    def is_protected(self) -> bool:
        """Check if the memo book is protected."""
        return self.settings["is_protected"]

    def _get_memo_path(self, name: str) -> Path:
        """Get the path to a memo."""
        return self._path / f"{name}{MEMO_EXTENSION}"

    ########################################
    # Memos
    ########################################

    def create_empty_memo_object(self) -> Memo:
        """Create an empty memo."""
        hashtags = set()
        if self.settings["add_date_hashtag"]:
            hashtags.add(datetime.now().strftime("#%Y-%m-%d"))  # noqa: DTZ005
        if self.settings["add_memobook_name_hashtag"]:
            hashtags.add(f"#{self.name}")
        return Memo(markdown="", hashtags=hashtags)

    def add_memo(self, memo_object: Memo, name: str = "") -> str:
        """Add a new memo to the memo book.

        Args:
            memo_object: The memo to add.
            name: The name of the memo. If empty, the title of the memo is used.

        Returns:
            The name of the added memo or None if the memo was not added.
        """
        memo_object.update_hashtags([])

        # file name
        string_for_filename = name or memo_object.title
        name = self.make_file_stem_from_string(string_for_filename)
        if not name:
            return None
        memo_path = self._get_memo_path(name)
        if memo_path.exists():
            # add timestamp to the file name
            name = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"  # noqa: DTZ005
            memo_path = self._get_memo_path(name)
        memo_path.write_text(memo_object.markdown, encoding="utf-8")
        return name

    def add_memo_from_html(self, html: str, name: str = "", url: str = "") -> str:
        """Add a new memo to the memo book from HTML.

        Args:
            html: The HTML of the memo.
            name: The name of the memo. If empty, the title of the memo is used.
            url: The URL where HTML was taken from.

        Returns:
            The name of the added memo or None if the memo was not added.
        """
        markdown = self.html2text_parser.parse(html)
        Path("temp.md").write_text(markdown, encoding="utf-8")
        if url:
            markdown = f"<{url}>\n\n{markdown}"
        temp_memo_object = self.create_empty_memo_object()
        memo_object = Memo(markdown + temp_memo_object.markdown)
        memo_object.update_hashtags([_("#bookmark")])
        return self.add_memo(memo_object, name=name)

    def update_memo(self, name: str, markdown: str) -> str:
        """Update a memo in the memo book.

        Args:
            name: The name of the memo.
            markdown: The markdown of the memo.

        Returns:
            The name of the updated memo or None if the memo was not found.
        """
        memo_path = self._get_memo_path(name)
        if not memo_path.exists():
            return None
        memo = Memo(markdown)
        memo.update_hashtags([])
        memo_path.write_text(memo.markdown, encoding="utf-8")
        return name

    def rename_memo(self, old_name: str, new_name: str) -> str:
        """Rename a memo in the memo book.

        Args:
            old_name: The old name of the memo.
            new_name: The new name of the memo.

        Returns:
            The name of the renamed memo or None if

        Raises:
            FileNotFoundError: If the memo was not found.
        """
        memo_path = self._get_memo_path(old_name)
        if not memo_path.exists():
            raise FileNotFoundError(f"Memo '{old_name}' not found.")
        memo_object = Memo(memo_path.read_text(encoding="utf-8"))
        memo_object.update_hashtags([])
        name = self.add_memo(memo_object, name=new_name)
        if not name:
            return None
        memo_path.unlink()
        return name

    def get_memo_markdown(self, name: str) -> str:
        """Get the content (markdonw) of a memo."""
        return self._get_memo_path(name).read_text(encoding="utf-8")

    def get_memos_file_names(self) -> list:
        """Get the file names of all memos in the memo book."""
        return [file.name for file in self._path.glob(f"*{MEMO_EXTENSION}")]

    def get_memos(self) -> list:
        """Get all memos in the memo book as dicts.

        Returns:
            A list of dicts with the following keys: "name".
        """
        return [{"name": file.stem} for file in self._path.glob(f"*{MEMO_EXTENSION}")]

    def is_memo_matches_search(self, name: str, include=None, exclude=None, quick_search: bool = True) -> bool:
        """Check if a memo matches the search.

        Args:
            name: The name of the memo.
            include: The words to include in the search.
            exclude: The words to exclude from the search.
            quick_search: If True, search only in the file names.

        Returns:
            True if the memo matches the search, False otherwise.
        """
        text = name
        if not quick_search:
            text += (self._path / f"{name}{MEMO_EXTENSION}").read_text(encoding="utf-8")
        text = text.lower()
        if include:
            for word in include:
                if word not in text:
                    return False
        if exclude:
            for word in exclude:
                if word in text:
                    return False
        return True

    def search(self, include=None, exclude=None, quick_search: bool = True) -> list:
        """Search memos in the memo book.

        Args:
            include: The words to include in the search.
            exclude: The words to exclude from the search.
            quick_search: If True, search only in the file names.

        Returns:
            A list of dicts with the following keys: "name".
        """
        return [
            {"name": file.stem}
            for file in self._path.glob(f"*{MEMO_EXTENSION}")
            if self.is_memo_matches_search(file.stem, include=include, exclude=exclude, quick_search=quick_search)
        ]

    def delete_memo(self, name: str) -> str:
        """Delete a memo from the memo book.

        Args:
            name: The name of the memo.

        Returns:
            The name of the deleted memo or None if the memo was not found.
        """
        memo_path = self._get_memo_path(name)
        if not memo_path.exists():
            return None
        memo_path.unlink()
        return name

    def get_memo_html(self, name: str) -> str:
        """Get the HTML of a memo from the memo book.

        Args:
            name: The name of the memo.

        Returns:
            The renedered HTML of the memo.
        """
        markdown = self._get_memo_path(name).read_text(encoding="utf-8")
        return memo_template.render(markdown=markdown)

    @staticmethod
    def make_file_stem_from_string(from_string):
        """Make a valid file name from a string.

        Args:
            from_string: The string to make the file name from.

        Returns:
            A valid file name without extension (stem only).
        """
        # filter out invalid characters
        filename = "".join(c for c in from_string if c.isalnum() or c in "._- ()")
        # strip spaces and dots
        filename = filename.strip(" .")
        # limit the filename length
        # delete last word until the filename is short enough
        while len(filename.split()) > 1 and len(filename) > MAX_FILENAME_LENGTH:
            filename = " ".join(filename.split()[:-1])
        if len(filename) > MAX_FILENAME_LENGTH:
            filename = filename[:MAX_FILENAME_LENGTH]
        # remove consecutive spaces
        return " ".join(filename.split())

    ########################################
    @classmethod
    def create(cls, path: Path, default_settings, exist_ok: bool = False) -> "MemoBook":
        """Create a new memo book at the given path.

        Args:
            path: The path to the memo book.
            default_settings: The default settings for the memo book.
            exist_ok: If True, do not raise an exception if the memo book already exists.

        Returns:
            The created memo book.
        """
        path.mkdir(parents=True, exist_ok=exist_ok)
        settings_path = path / ".settings"
        Settings.create(settings_path, default_settings)
        return cls(path)
