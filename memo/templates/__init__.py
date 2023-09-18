"""Templates for memo app."""
from pathlib import Path

from markdown2 import Markdown

markdowner = Markdown(extras=["fenced-code-blocks", "tables"])


class Templates:
    """A class for loading and rendering templates."""

    def __init__(self, path: Path) -> None:
        """Load the template from the given path."""
        self.path = path
        self.template = self.path.read_text(encoding="utf-8")

    def render(self, title: str, markdown_content: str) -> str:
        """Render the template with the given title and content."""
        content = markdowner.convert(markdown_content)
        return self.template.format(title=title, content=content)


memo_template = Templates(Path(__file__).parent / "memo.html")
