"""Utility functions for the memo package."""

import urllib.parse
from dataclasses import dataclass

from courlan import check_url
from html2text import HTML2Text
from readability import Document

MAX_FILENAME_LENGTH = 200


@dataclass
class ParsedPage:
    """A parsed page."""

    url: str
    domain_name: str
    title: str
    markdown: str


html2text_converter = HTML2Text()
html2text_converter.unicode_snob = True
html2text_converter.skip_internal_links = True
html2text_converter.protect_links = True
# html2text_converter.ignore_anchors = True   # noqa: ERA001
html2text_converter.ignore_images = True
html2text_converter.ignore_emphasis = True
html2text_converter.mark_code = True
html2text_converter.ignore_links = True
html2text_converter.ignore_images = True


def is_valid_url(url):
    """Check if the given url is a valid http url."""
    url, domain_name = check_url(url)
    return url is not None and domain_name is not None


def get_page_html(url) -> str:
    """Get the HTML of the given URL."""
    try:
        response = urllib.request.urlopen(url)  # noqa: S310
        if response.status != 200:
            raise urllib.error.URLError("Status code is not 200")
        return response.read().decode("utf-8")
    except urllib.error.URLError:
        return ""


def get_page_markdown(html: str) -> str:
    """Get the markdown of the given HTML."""
    return html2text_converter.handle(html).strip()


def make_file_stem_from_string(from_string):
    """Make a filename from the given string.

    The filename is a valid filename without extension.

    Args:
        from_string (str): the string to make the filename from.

    Returns:
        str: the filename.
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


def parse_page(html: str, url: str, use_readability: bool = True) -> ParsedPage:
    """Get a page from the given URL.

    Args:
        html: The HTML of the page.
        url: The URL to get the page from.
        use_readability: If True, use Readability to parse the page.

    Returns:
        A ParsedPage object.
    """
    html = get_page_html(url)
    markdown = get_page_markdown(html)
    if use_readability:
        document = Document(html)
        title = document.short_title()
        html = document.summary()
        url, domain_name = check_url(url)
    else:
        title = ""
        url, domain_name = check_url(url)
    markdown = get_page_markdown(html)
    return ParsedPage(url, domain_name, title, markdown)
