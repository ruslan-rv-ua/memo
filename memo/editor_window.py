"""Editor dialog."""

import wx


class EditorDialog(wx.Dialog):
    """Editor dialog."""

    def __init__(self, parent, title, value):
        """Constructor.

        Args:
            parent (wx.Window): Parent window.
            title (str): Dialog title.
            value (str): Initial value for the editor.
        """
        super().__init__(parent, title=title)
        self.value = value
        self._create_ui()
        self._bind_events()
        self._layout()

    def _create_ui(self):
        self.editor = wx.TextCtrl(self, style=wx.TE_MULTILINE, value=self.value)
        self.ok_button = wx.Button(self, label="OK")
        self.cancel_button = wx.Button(self, label="Cancel")

    def _bind_events(self):
        self.ok_button.Bind(wx.EVT_BUTTON, self._on_ok)
        self.cancel_button.Bind(wx.EVT_BUTTON, self._on_cancel)

    def _layout(self):
        # width and height are half of the screen size, centered
        screen_width, screen_height = wx.GetDisplaySize()
        width = screen_width // 2
        height = screen_height // 2
        self.SetSize((width, height))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        left_sizer.Add(self.editor, 1, wx.ALL | wx.EXPAND, 5)
        right_sizer.Add(self.ok_button, 0, wx.ALL | wx.EXPAND, 5)
        right_sizer.Add(self.cancel_button, 0, wx.ALL | wx.EXPAND, 5)

        sizer.Add(left_sizer, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(right_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(sizer)
        self.Layout()
        self.Centre()

    def _on_ok(self, event):
        self.value = self.editor.GetValue()
        self.EndModal(wx.ID_OK)

    def _on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)
