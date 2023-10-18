"""This module contains the "Add Bookmark" dialog."""

from gettext import gettext as _

import wx


class BookmarkDialog(wx.Dialog):
    """The "Add bookmark" dialog."""

    def __init__(self, parent, url, include_links, include_images):
        """Initialize the dialog."""
        super().__init__(parent, wx.ID_ANY, _("Add bookmark"))
        self.include_links = include_links
        self.include_images = include_images

        # URL edit
        self.url = wx.TextCtrl(self, wx.ID_ANY, "")
        self.url.SetValue(url)
        self.include_links_checkbox = wx.CheckBox(self, wx.ID_ANY, _("Include links"))
        self.include_images_checkbox = wx.CheckBox(self, wx.ID_ANY, _("Include images"))

        self.include_links_checkbox.SetValue(self.include_links)
        self.include_images_checkbox.SetValue(self.include_images)

        # Buttons
        self.ok_button = wx.Button(self, wx.ID_OK, _("OK"))
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, _("Cancel"))

        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.url, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.include_links_checkbox, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.include_images_checkbox, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.ok_button, 0, wx.ALL, 5)
        buttons_sizer.Add(self.cancel_button, 0, wx.ALL, 5)
        sizer.Add(buttons_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.SetSizer(sizer)
        self.Center()

        # Bind events
        self.ok_button.Bind(wx.EVT_BUTTON, self.on_ok)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

    def on_ok(self, event):
        """Handle the "OK" button event."""
        if self.url.GetValue() == "":
            self.EndModal(wx.ID_CANCEL)
            return
        self.include_links = self.include_links_checkbox.GetValue()
        self.include_images = self.include_images_checkbox.GetValue()
        self.EndModal(wx.ID_OK)

    def on_cancel(self, event):
        """Handle the "Cancel" button event."""
        self.EndModal(wx.ID_CANCEL)
