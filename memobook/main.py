"""The main application object for the memo application."""

import gettext  # noqa: I001
from pathlib import Path

import wx

from app import MemoBookWindow


class MemoApp(wx.App):
    """The main application object."""

    def OnInit(self):  # noqa: N802
        """Create the main application window."""
        work_dir = Path(__file__).parent
        self.frame = MemoBookWindow(work_dir=work_dir)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    gettext.install("app")  # TODO: replace with the appropriate catalog name

    app = MemoApp(0)
    app.MainLoop()
