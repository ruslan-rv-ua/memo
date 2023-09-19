"""A memo book."""

from datetime import datetime
from enum import Enum
from pathlib import Path

from benedict import benedict

from templates import memo_template

MEMOS_EXTENSIONS = ["md"]


class MemoType(str, Enum):
    """The type of a memo."""

    BOOKMARK = "bookmark"
    NOTE = "note"


class MemoView(str, Enum):
    """The view of the memo."""

    EDITOR = "editor"
    WEB = "web"


DEFAULT_MEMOBOOK_SETTINGS = {
    "current_view": MemoView.WEB,
    "editor": {
        "font": {
            "family": "Consolas",
            "size": 12,
        },
    },
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
        self._index_path = path / ".index"

        self.settings = MemoBookSettings(path)

        if self._index_path.exists():
            self._index = benedict(self._index_path, format="json", keypath_separator=None)
        else:
            self._index = benedict(keypath_separator=None)
        self._update_index()

    @property
    def path(self) -> Path:
        """The path to the memo book."""
        return self._path

    ########################################
    # Index
    ########################################

    def _remove_missing_files_from_index(self):
        for file_name in set(self._index):
            if not (self._path / file_name).exists():
                del self._index[file_name]

    def _add_new_files_to_index(self):
        for file_path in self._path.glob(f"*.{'|'.join(MEMOS_EXTENSIONS)}"):
            if file_path.name not in self._index:
                self._add_file_to_index(file_path)

    def _update_index(self):
        self._remove_missing_files_from_index()
        self._add_new_files_to_index()
        self._index.to_json(filepath=self._index_path, ensure_ascii=False, indent=4)  # TODO: no indent, no ensure_ascii

    def _add_file_to_index(self, file_path: Path):
        # get first line as title
        with file_path.open(encoding="utf-8") as f:
            title = f.readline().strip("#").strip()  # strip # and whitespace
        # get file extension as type
        memo_type = MemoType(file_path.suffixes[-2].strip("."))
        # get datetime from file name e.g. 20130920132804.bookmark.md
        dt_str = file_path.name.strip(".")[0:14]
        created_at = datetime.strptime(dt_str, "%Y%m%d%H%M%S")  # noqa: DTZ007
        # add to index
        self._index[file_path.name] = {
            "file_name": file_path.name,
            "title": title,
            "type": memo_type,
            "date": created_at,
        }

    ########################################
    # Memo
    ########################################

    def add_memo(self, content: str, memo_type: MemoType):
        """Add a new memo to the memo book."""
        # create file name based on current datetime and type
        while True:
            now = datetime.now()  # noqa: DTZ005
            file_name = f"{now:%Y%m%d%H%M%S}.{memo_type.value}.md"
            file_path = self._path / file_name
            if not file_path.exists():
                break
        # write content to file
        file_path.write_text(content, encoding="utf-8")
        # update index
        self._add_file_to_index(file_path)
        # save index
        self._index_path.write_text(self._index.to_json(), encoding="utf-8")

    def get_memos_list(self):
        """Get a list of memos."""
        self._update_index()  # TODO: only update if necessary
        return list(self._index.values())

    def get_memo_content(self, file_name: str):
        """Get the content of the memo with the given file name."""
        return (self._path / file_name).read_text(encoding="utf-8")

    def get_memo_html(self, file_name: str):
        """Get the html of the memo with the given file name."""
        content = self.get_memo_content(file_name)
        return memo_template.render(title=file_name, markdown_content=content)
