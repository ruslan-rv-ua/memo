"""This module contains the GUI for the memo application."""

from gettext import gettext as _
from pathlib import Path

import wx
import wx.html2
from ObjectListView import ColumnDefn, ObjectListView


class MemoWindow(wx.Frame):
    """The main window of the memo application."""

    def __init__(self, *args, **kwds):
        """Create a new memo window."""
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.SetTitle(_("Memo"))

        # Menu Bar
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)

        self.panel = wx.Panel(self, wx.ID_ANY)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left panel
        self.list_memos = ObjectListView(self.panel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.list_memos.SetColumns(
            [
                ColumnDefn(title=_("Title"), align="left", minimumWidth=500, maximumWidth=500, valueGetter="title"),
                ColumnDefn(title=_("Date"), align="left", width=200, valueGetter="date"),
            ]
        )
        sizer.Add(self.list_memos, 1, wx.EXPAND, 0)

        # Right panel - read-only text view
        self.memo_view = wx.TextCtrl(self.panel, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.panel.SetSizer(sizer)

        self.Layout()
        self.Maximize()

        from memobook import MemoBook

        memobook = MemoBook(Path(r"e:\dev\memo\test_memobook"))
        memos_data = memobook.get_memos_list()
        self.list_memos.SetObjects(memos_data)
