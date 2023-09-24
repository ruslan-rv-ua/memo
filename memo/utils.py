"""Utility functions for the memo package."""

import re  # TODO: do not use regex
import urllib.parse
from datetime import datetime

from html2text import HTML2Text

MAX_FILENAME_LENGTH = 200


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


def is_valid_http_url(url):
    """Check if the given url is a valid http url."""
    try:
        result = urllib.parse.urlparse(url)
        if result.scheme not in ["http", "https"]:
            return False
        return True
    except ValueError:
        return False


def get_page_html(url) -> str:
    """Get the HTML of the given URL."""
    try:
        response = urllib.request.urlopen(url)  # noqa: S310
        if response.status != 200:
            raise urllib.error.URLError("Status code is not 200")
        return response.read().decode("utf-8")
    except urllib.error.URLError:
        return ""


def get_page_title(html: str) -> str:
    """Get the title of the page from the given HTML."""
    title = ""
    if html:
        match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if match:
            title = match.group(1).strip()
    return title


def get_page_description(html: str) -> str:
    """Get the description of the page from the given HTML."""
    description = ""
    if html:
        match = re.search(r'<meta name="description" content="(.*?)"', html, re.IGNORECASE | re.DOTALL)
        if match:
            description = match.group(1).strip()
    return description


def get_domain(url: str) -> str:
    """Get the domain of the given URL."""
    return urllib.parse.urlparse(url).netloc


def get_page_markdown(html: str) -> str:
    """Get the markdown of the given HTML."""
    return html2text_converter.handle(html)


def make_filename_from_string(from_string, with_timestamp=False):
    """Make a filename from the given string.

    The filename is a valid filename without extension.

    Args:
        from_string (str): the string to make the filename from.
        with_timestamp (bool): if True, the current timestamp is added to the filename.

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
    filename = " ".join(filename.split())

    # add timestamp
    if with_timestamp:
        filename += datetime.now().strftime("-%Y-%m-%d-%H-%M-%S")  # noqa: DTZ005
    return filename
