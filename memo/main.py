"""The main application object for the memo application."""

import gettext

import wx

from memo_window import MemoWindow


class MemoApp(wx.App):
    """The main application object."""

    def OnInit(self):  # noqa: N802
        """Create the main application window."""
        self.frame = MemoWindow(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    gettext.install("app")  # TODO: replace with the appropriate catalog name

    app = MemoApp(0)
    app.MainLoop()
