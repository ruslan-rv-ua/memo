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
            Title of the memo.
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
        file_stem = make_file_stem_from_string(string_for_filename)
        file_path = self._path / f"{file_stem}.md"
        if file_path.exists():
            # add timestamp to the file name
            file_stem = f"{file_stem}_{datetime.now().strftime('%Y%m%d%H%M%S')}"  # noqa: DTZ005
            file_path = self._path / f"{file_stem}{MEMO_EXTENSION}"
        memo.save(file_path)
        return file_stem

    def update_memo(self, title: str, markdown: str) -> str:
        """Update a memo in the memo book.

        Args:
            title: The title of the memo.
            markdown: The markdown of the memo.

        Returns:
            The title of the memo.
        """
        path = self._path / f"{title}{MEMO_EXTENSION}"
        memo = Memo(markdown)
        memo.save(path)
        return title

    def get_memo(self, title: str) -> Memo:
        """Get a memo from the memo book."""
        return Memo.from_path(self._path / f"{title}{MEMO_EXTENSION}")

    def get_memos_file_names(self) -> list:
        """Get the file names of all memos in the memo book."""
        return [file.name for file in self._path.glob("*.md")]

    def get_memos_info(self) -> list:
        """Get all memos in the memo book as dicts.

        Returns:
            A list of dicts with the following keys: "title".
        """
        return [{"title": file.stem} for file in self._path.glob(f"*{MEMO_EXTENSION}")]

    def is_memo_matches_search(self, title: str, include=None, exclude=None, quick_search: bool = True) -> bool:
        """Check if a memo matches the search.

        Args:
            title: The title of the memo.
            include: The words to include in the search.
            exclude: The words to exclude from the search.
            quick_search: If True, search only in the file names.
        """
        text = title
        if not quick_search:
            text += (self._path / f"{title}{MEMO_EXTENSION}").read_text()
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
            A list of dicts with the following keys: "title".
        """
        return [
            {"title": file.stem}
            for file in self._path.glob(f"*{MEMO_EXTENSION}")
            if self.is_memo_matches_search(file.name, include=include, exclude=exclude, quick_search=quick_search)
        ]

    def delete_memo(self, file_stem: str) -> str:
        """Delete a memo from the memo book.

        Args:
            file_stem: The file stem of the memo.

        Returns:
            The file name of the deleted memo.
        """
        path = self._path / f"{file_stem}{MEMO_EXTENSION}"
        path.unlink()
        return file_stem
