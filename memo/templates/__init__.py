"""Templates for memo app."""
from pathlib import Path

from markdown2 import Markdown

markdowner = Markdown(
    extras=[
        "toc",
        "metadata ",
        "code-friendly",
        "fenced-code-blocks",
        "target-blank-links",
        "tables",
        "tag-friendly",
        "task_list",
    ]
)


class Templates:
    """A class for loading and rendering templates."""

    def __init__(self, path: Path) -> None:
        """Load the template from the given path."""
        self.path = path
        self.template = self.path.read_text(encoding="utf-8")

    def render(self, markdown: str, title: str = "") -> str:
        """Render the template with the given title and content."""
        content = markdowner.convert(markdown)
        return self.template.format(title=title, content=content)


memo_template = Templates(Path(__file__).parent / "memo.html")
