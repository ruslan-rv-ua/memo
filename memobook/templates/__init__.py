"""Templates for memo app."""
from pathlib import Path

from markdown_it_pyrs import MarkdownIt

markdowner = MarkdownIt("gfm")


class Templates:
    """A class for loading and rendering templates."""

    def __init__(self, path: Path) -> None:
        """Load the template from the given path."""
        self.path = path
        self.template = self.path.read_text(encoding="utf-8")

    def render(self, markdown: str) -> str:
        """Render the template with the given title and content."""
        content = markdowner.render(markdown)
        return self.template.replace("{{content}}", content)


memo_template = Templates(Path(__file__).parent / "memo.html")
