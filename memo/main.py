"""The main application object for the memo application."""

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
    app = MemoApp(0)
    app.MainLoop()
