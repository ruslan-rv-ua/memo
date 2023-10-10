"""The memo module."""


HASHTAGS_LINE_PREFIX = "Hashtags: "


# class Memo:
#     """A memo."""

#     def __init__(self, markdown: str = "", hashtags=None):
#         """Initialize a new instance of the Memo class.

#         Args:
#             markdown (str): the content of the memo.
#             hashtags (list): the list of extra hashtags.
#         """
#         if hashtags:

#     @property
#     def markdown(self):
#         """Get the content of the memo."""

#     @property
#     def title(self):
#         """Get the title of the memo."""
#         if self._lines:
#             # first line without markdown syntax

#     def _find_hashtags_line_index(self):
#         """Find the index of the line that contains only hashtags.

#         The line must start with HASHTAGS_LINE_PREFIX.

#         Returns:
#             int: the index of the line that contains only hashtags or -1 if not found.
#         """
#         # beckward search
#         for i in range(len(self._lines) - 1, -1, -1):
#             if self._lines[i].startswith(HASHTAGS_LINE_PREFIX):

#     def has_hashtags(self):
#         """Check if the memo has hashtags.

#         Returns:
#             bool: True if the memo has hashtags, False otherwise.
#         """

#     @property
#     def hashtags(self):
#         """Get the hashtags from the memo.

#         Returns:
#             set: the list of hashtags.
#         """
#         if index >= 0:
#             # get the hashtags from the line

#     def set_hashtags(self, hashtags):
#         """Set the hashtags of the memo.

#         Args:
#             hashtags: the list of hashtags.
#         """
#         # all hashtags to lowercase
#         if index < 0:
#             # add new line

#     def update_hashtags(self, hashtags):
#         """Update the hashtags of the memo.

#         Args:
#             hashtags: the list of hashtags.
#         """
