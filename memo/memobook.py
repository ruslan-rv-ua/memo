"""A memo book."""

from datetime import datetime
from pathlib import Path

from benedict import benedict

from memo_item import Memo
from utils import make_filename_from_string

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

    def add_memo(self, markdown: str, title: str = "", add_date_hashtag: bool = True, extra_hashtags=None):
        """Add a new memo to the memo book."""
        memo = Memo(markdown)

        # set hashtags
        hashtags = set()
        if add_date_hashtag:
            hashtags.add(datetime.now().strftime("%Y-%m-%d"))  # noqa: DTZ005
        if extra_hashtags:
            hashtags.update(set(extra_hashtags))
        if hashtags:
            memo.update_hashtags(hashtags)

        # file name
        string_for_filename = title or memo.title
        file_name = make_filename_from_string(string_for_filename)
        file_path = self._path / f"{file_name}.md"
        if file_path.exists():
            # add timestamp to the file name
            file_name = make_filename_from_string(string_for_filename, with_timestamp=True)
            file_path = self._path / f"{file_name}.md"
        memo.save(file_path)

    def get_memo(self, file_name: str) -> Memo:
        """Get a memo from the memo book."""
        return Memo.from_path(self._path / file_name)

    def get_memos_file_names(self) -> list:
        """Get the file names of all memos in the memo book."""
        return [file.name for file in self._path.glob("*.md")]
