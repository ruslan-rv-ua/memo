"""This module contains ManageMemoBooksDialog class."""

from gettext import gettext as _

import wx
from ObjectListView import ColumnDefn, ObjectListView


class ManageMemoBooksDialog(wx.Dialog):
    """This class is a dialog for managing MemoBooks."""

    def __init__(self, parent):
        """Initialize ManageMemoBooksDialog."""
        super().__init__(parent, title=_("Manage MemoBooks"), size=(400, 300))
        self.app_window = parent
        self._create_ui()
        self.Centre()

    def _create_ui(self):
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        # left - list with memobooks names, no columns headers
        self.list_memobooks = ObjectListView(self.panel, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.list_memobooks.SetColumns(
            [
                ColumnDefn(_("MemoBooks"), "left", 200, "name"),
            ]
        )
        self.list_memobooks.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.on_memobook_selected)

        # right - buttons vertically: create new, add external, delete, separator, move up, move down
        self.button_create_memobook = wx.Button(self.panel, label=_("Create MemoBook"))
        self.button_create_memobook.Bind(wx.EVT_BUTTON, self.on_button_create_memobook_clicked)
        self.button_create_memobook.SetMinSize((150, -1))  # add padding to the button
        self.button_add_external_memobook = wx.Button(self.panel, label=_("Add External MemoBook"))
        self.button_add_external_memobook.Bind(wx.EVT_BUTTON, self.on_button_add_external_memobook_clicked)
        self.button_add_external_memobook.SetMinSize((150, -1))  # add padding to the button
        self.button_delete_memobook = wx.Button(self.panel, label=_("Delete MemoBook"))
        self.button_delete_memobook.Bind(wx.EVT_BUTTON, self.on_button_delete_memobook_clicked)
        self.button_move_up = wx.Button(self.panel, label=_("Move Up"))
        self.button_move_up.Bind(wx.EVT_BUTTON, self.on_button_move_up_clicked)
        self.button_move_down = wx.Button(self.panel, label=_("Move Down"))
        self.button_move_down.Bind(wx.EVT_BUTTON, self.on_button_move_down_clicked)
        self.button_close = wx.Button(self.panel, label=_("Close"))
        self.button_close.Bind(wx.EVT_BUTTON, self.on_button_close_clicked)
        buttons_sizer = wx.BoxSizer(wx.VERTICAL)
        buttons_sizer.Add(self.button_create_memobook, 0, wx.EXPAND, 50)
        buttons_sizer.Add(self.button_add_external_memobook, 0, wx.EXPAND)
        buttons_sizer.Add(self.button_delete_memobook, 0, wx.EXPAND)
        buttons_sizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND)
        buttons_sizer.Add(self.button_move_up, 0, wx.EXPAND)
        buttons_sizer.Add(self.button_move_down, 0, wx.EXPAND)
        # align bottom
        buttons_sizer.AddStretchSpacer()
        buttons_sizer.Add(self.button_close, 0, wx.EXPAND)

        self.sizer.Add(self.list_memobooks, 1, wx.EXPAND, 10)
        self.sizer.Add(buttons_sizer, 1, wx.EXPAND, 10)
        self.panel.SetSizer(self.sizer)

        self.list_memobooks.SetObjects(self.app_window.settings["memobooks"])
        self.list_memobooks.SetFocus()
        self.list_memobooks.Focus(0)
        self.list_memobooks.Select(0)
        self.on_memobook_selected(None)

    def on_memobook_selected(self, event):
        """Enable/disable buttons based on selected item."""
        index = self.list_memobooks.GetFocusedItem()
        item = self.list_memobooks.GetSelectedObject()
        self.button_move_up.Enable(item["is_protected"] is False and index > 1)
        self.button_move_down.Enable(
            item["is_protected"] is False and index < len(self.app_window.settings["memobooks"]) - 1
        )
        self.button_delete_memobook.Enable(item["is_protected"] is False)

    def _is_memobook_name_used(self, name):
        """Check if memobook name is already used."""
        return any(item["name"] == name for item in self.app_window.settings["memobooks"])

    def on_button_create_memobook_clicked(self, event):
        """Create new MemoBook."""
        # TODO

    def on_button_add_external_memobook_clicked(self, event):
        """Add external MemoBook."""
        # ask for folder
        dlg = wx.DirDialog(self, _("Select MemoBook folder"))
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        folder_path = dlg.GetPath()
        # check if folder is already in list
        for item in self.app_window.settings["memobooks"]:
            if item["path"] == folder_path:
                wx.MessageBox(_("This MemoBook is already used."), _("Error"), wx.OK | wx.ICON_ERROR)
                return
        name = folder_path.split("/")[-1]
        # if memobook name is already used - ask for new name
        while True:
            dlg = wx.TextEntryDialog(self, _("MemoBook name"), _("Enter MemoBook name"), name)
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            name = dlg.GetValue()
            # check if name is valid for file name (letters, numbers, spaces, dashes, underscores)
            if not name.replace(" ", "").replace("-", "").replace("_", "").isalnum():
                wx.MessageBox(_("MemoBook name is not valid."), _("Error"), wx.OK | wx.ICON_ERROR)
                continue
            # check if name is already used
            if self._is_memobook_name_used(name):
                wx.MessageBox(_("This MemoBook name is already used."), _("Error"), wx.OK | wx.ICON_ERROR)
                continue
            break
        # add to list
        self.app_window.settings["memobooks"].append({"name": name, "path": folder_path, "is_protected": False})
        # TODO: create memobook

    def on_button_delete_memobook_clicked(self, event):
        """Delete selected item."""
        # get confirmation
        index = self.list_memobooks.GetFocusedItem()
        item = self.list_memobooks.GetSelectedObject()
        if (
            wx.MessageBox(
                _("Are you sure you want to delete MemoBook {}?").format(item["name"]),
                _("Confirm delete"),
                wx.YES_NO | wx.ICON_QUESTION,
            )
            == wx.NO
        ):
            return
        # delete from list
        self.app_window.settings["memobooks"].remove(item)
        self.list_memobooks.SetObjects(self.app_window.settings["memobooks"])
        self.list_memobooks.Focus(index - 1)
        self.list_memobooks.Select(index - 1)
        # ask delete from disk or only from list
        if (
            wx.MessageBox(
                _("Do you want to delete MemoBook {} from disk?").format(item["name"]),
                _("Confirm delete"),
                wx.YES_NO | wx.ICON_QUESTION,
            )
            == wx.YES
        ):
            # delete from disk
            pass  # TODO

    def on_button_move_up_clicked(self, event):
        """Move selected item up."""
        index = self.list_memobooks.GetFocusedItem()
        item = self.list_memobooks.GetSelectedObject()
        self.app_window.settings["memobooks"].remove(item)
        self.app_window.settings["memobooks"].insert(index - 1, item)
        self.list_memobooks.SetObjects(self.app_window.settings["memobooks"])
        self.list_memobooks.Focus(index - 1)
        self.list_memobooks.Select(index - 1)

    def on_button_move_down_clicked(self, event):
        """Move selected item down."""
        index = self.list_memobooks.GetFocusedItem()
        item = self.list_memobooks.GetSelectedObject()
        self.app_window.settings["memobooks"].remove(item)
        self.app_window.settings["memobooks"].insert(index + 1, item)
        self.list_memobooks.SetObjects(self.app_window.settings["memobooks"])
        self.list_memobooks.Focus(index + 1)
        self.list_memobooks.Select(index + 1)

    def on_button_close_clicked(self, event):
        """Close dialog."""
        self.Close()
