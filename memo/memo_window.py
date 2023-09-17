"""This module contains the GUI for the memo application."""

import wx
import wx.html2
from ObjectListView import ColumnDefn, ObjectListView

html_content = """<html>
<head>
<script src="
https://cdn.jsdelivr.net/npm/bootstrap-dark-5@1.1.3/dist/js/darkmode.min.js
"></script>
<link href="
https://cdn.jsdelivr.net/npm/bootstrap-dark-5@1.1.3/dist/css/bootstrap-dark.min.css
" rel="stylesheet">
</head>
<body class="bg-gray-900 text-white">
<h1>HTML Content</h1>
<p>This is some HTML content</p>
<a href="http://www.google.com">Google</a>
<button class="btn btn-primary">Button</button>
</body>
</html>"""


memos_data = [
    {
        "title": "Memo 1",
        "date": "2021-01-01",
    },
    {
        "title": "Memo 2",
        "date": "2021-01-02",
    },
]


class MemoWindow(wx.Frame):
    """The main window of the memo application."""

    def __init__(self, *args, **kwds):
        """Create a new memo window."""
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("Memo")

        # Menu Bar
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)

        self.panel = wx.Panel(self, wx.ID_ANY)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.list_memos = ObjectListView(self.panel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.list_memos.SetColumns(
            [
                ColumnDefn(title="Title", align="left", minimumWidth=500, valueGetter="title"),
                ColumnDefn(title="Date", align="left", width=200, valueGetter="date"),
            ]
        )
        sizer.Add(self.list_memos, 1, wx.EXPAND, 0)

        self.browser = wx.html2.WebView.New(self.panel, wx.ID_ANY, style=wx.BORDER_NONE)
        sizer.Add(self.browser, 1, wx.EXPAND, 0)

        self.panel.SetSizer(sizer)

        self.Layout()
        self.Maximize()

        self.browser.SetPage(
            html_content,
            "",
        )

        self.list_memos.SetObjects(memos_data)
