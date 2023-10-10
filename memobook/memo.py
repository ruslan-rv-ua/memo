"""Memo."""


from datetime import datetime


class Memo:
    """Memo."""

    def __init__(
        self,
        content: str | None = None,
        title: str | None = None,
        link: str | None = None,
        link_text: str | None = None,
        hashtags=None,
    ):
        """Create a memo.

        Args:
            content (str | None): The content of the memo.
            title (str | None): The title of the memo.
            link (str | None): The link of the memo.
            link_text (str | None): The link text of the memo.
            hashtags: The hashtags of the memo.


        Raises:
            ValueError: If link_text is set but link is not.
        """
        if link_text and not link:
            raise ValueError("link_text is set but link is not")

        self._content = content if content else ""
        self._sanitize_content()
        self._title = title
        self._link = link
        self._link_text = link_text
        self._hashtags = self._correct_hashtags(hashtags) if hashtags else set()

    @property
    def title(self) -> str:
        """The title of the memo."""
        return self._title or self._get_title_from_content()

    def get_markdown(self) -> str:
        """The markdown of the memo.

        Returns:
            The markdown of the memo.
        """
        link_line = ""
        if self._link:
            link_line = f"[{self._link_text}]({self._link})" if self._link_text else self._link
        title = self._title or ""
        header = ""
        if title or link_line:
            header = "\n\n".join([link_line, f"# {title}"]) + "\n\n----\n\n"

        hashtags_line = " ".join(sorted(self._hashtags)) if self._hashtags else ""
        footer = ""
        if hashtags_line:
            footer = f"\n\n----\n\n{hashtags_line}"
        return header + self._content + footer

    def _get_title_from_content(self) -> str:
        first_line = self._content.splitlines()[0].strip()
        if first_line.startswith("#"):
            return first_line.lstrip("#").strip()
        return first_line

    def _sanitize_content(self) -> str:
        """Sanitize the content of the memo.

        - strips leading and trailing whitespace and newlines
        - removes tripple newlines
        """
        self._content = self._content.strip()
        while "\n\n\n" in self._content:
            self._content = self._content.replace("\n\n\n", "\n\n")

    def _correct_hashtags(self, hashtags) -> set[str]:
        """Correct the hashtags of the memo.

        Add `#` to the hashtags if they don't start with `#`.

        Args:
            hashtags: The hashtags to correct.

        Returns:
            The corrected hashtags.
        """
        return {f"#{hashtag}" if not hashtag.startswith("#") else hashtag for hashtag in hashtags}

    def update_hashtags(self, hashtags) -> None:
        """Update the hashtags of the memo.

        Args:
            hashtags: The hashtags to update.
        """
        self._hashtags.update(self._correct_hashtags(hashtags))

    @staticmethod
    def get_current_date_hashtag() -> str:
        """Get the current date as a hashtag.

        Returns:
            The current date as a hashtag.
        """
        return datetime.now().strftime("#%Y-%m-%d")  # noqa: DTZ005
