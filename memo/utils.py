"""Utility functions for the memo package."""


from html2text import HTML2Text

html2text_converter = HTML2Text()  # TODO: use html2text directly, make customizable
html2text_converter.unicode_snob = True
html2text_converter.skip_internal_links = True
html2text_converter.protect_links = True
# html2text_converter.ignore_anchors = True   # noqa: ERA001
html2text_converter.ignore_images = True
html2text_converter.ignore_emphasis = True
html2text_converter.mark_code = True
html2text_converter.ignore_links = True
html2text_converter.ignore_images = True


def get_page_markdown(html: str) -> str:
    """Get the markdown of the given HTML."""
    return html2text_converter.handle(html).strip()
