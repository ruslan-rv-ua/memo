"""A memo book."""

from datetime import datetime
from pathlib import Path

from benedict import benedict

from memo_item import Memo
from utils import make_file_stem_from_string

DEFAULT_MEMOBOOK_SETTINGS = {
    "memos": {
        "columns": {
            "file_name": {"width": 0},
            "title": {"width": 0},
            "type": {"width": 0},
            "date": {"width": 0},
        },
        "sort": {"column": "date", "order": "desc"},
    }
}

MEMO_EXTENSION = ".md"


class MemoBookSettings(benedict):
    """The settings of a memo book."""

    def __init__(self, path: Path) -> None:
        """Create or open the settings of a memo book at the given path."""
        settings_path = path / ".settings"
        if settings_path.exists():
            super().__init__(str(settings_path), format="json", keypath_separator=None)
        else:
            super().__init__({})
            self.update(DEFAULT_MEMOBOOK_SETTINGS)
        self.__settings_path = settings_path
        self.save()

    def save(self):
        """Save the settings."""
        self.to_json(filepath=self.__settings_path, ensure_ascii=False, indent=4)  # TODO: no indent, no ensure_ascii


class MemoBook:
    """A memo book."""

    def __init__(self, path: Path) -> None:
        """Create or open a memo book at the given path."""
        self._path = path

        self.settings = MemoBookSettings(path)

    @property
    def path(self) -> Path:
        """The path to the memo book."""
        return self._path

    ########################################
    # Memos
    ########################################

    def add_memo(self, markdown: str, title: str = "", add_date_hashtag: bool = True, extra_hashtags=None) -> str:
        """Add a new memo to the memo book.

        Args:
            markdown: The markdown of the memo.
            title: The title of the memo.
            add_date_hashtag: If True, add the date as a hashtag.
            extra_hashtags: Extra hashtags to add to the memo.

        Returns:
            Name of the memo.
        """
        memo = Memo(markdown)

        # set hashtags
        hashtags = set()
        if add_date_hashtag:
            hashtags.add(datetime.now().strftime("#%Y-%m-%d"))  # noqa: DTZ005
        if extra_hashtags:
            hashtags.update(set(extra_hashtags))
        if hashtags:
            memo.update_hashtags(hashtags)

        # file name
        string_for_filename = title or memo.title
        name = make_file_stem_from_string(string_for_filename)
        file_path = self._path / f"{name}{MEMO_EXTENSION}"
        if file_path.exists():
            # add timestamp to the file name
            name = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"  # noqa: DTZ005
            file_path = self._path / f"{name}{MEMO_EXTENSION}"
        memo.save(file_path)
        return name

    def update_memo(self, name: str, markdown: str) -> str:
        """Update a memo in the memo book.

        Args:
            name: The name of the memo.
            markdown: The markdown of the memo.

        Returns:
            The name of the updated memo or None if the memo was not found.
        """
        path = self._path / f"{name}{MEMO_EXTENSION}"
        if not path.exists():
            return None
        memo = Memo(markdown)
        memo.save(path)
        return name

    def get_memo(self, name: str) -> Memo:
        """Get a memo from the memo book."""
        return Memo.from_path(self._path / f"{name}{MEMO_EXTENSION}")

    def get_memo_content(self, name: str) -> str:
        """Get the content of a memo from the memo book."""
        return (self._path / f"{name}{MEMO_EXTENSION}").read_text(encoding="utf-8")

    def get_memos_file_names(self) -> list:
        """Get the file names of all memos in the memo book."""
        return [file.name for file in self._path.glob("*.md")]

    def get_memos_info(self) -> list:
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
            text += (self._path / f"{name}{MEMO_EXTENSION}").read_text()
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
            if self.is_memo_matches_search(file.name, include=include, exclude=exclude, quick_search=quick_search)
        ]

    def delete_memo(self, name: str) -> str:
        """Delete a memo from the memo book.

        Args:
            name: The name of the memo.

        Returns:
            The name of the deleted memo or None if the memo was not found.
        """
        path = self._path / f"{name}{MEMO_EXTENSION}"
        if path.exists():
            path.unlink()
            return name
        return None

    def rename_memo(self, old_name: str, new_name: str) -> str:
        """Rename a memo in the memo book.

        Args:
            old_name: The old name of the memo.
            new_name: The new name of the memo.

        Returns:
            The name of the renamed memo or None if the memo was not found.
        """
        path = self._path / f"{old_name}{MEMO_EXTENSION}"
        if path.exists():
            new_path = self._path / f"{new_name}{MEMO_EXTENSION}"
            path.rename(new_path)
            return new_name
        return None
