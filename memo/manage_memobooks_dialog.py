"""This module contains ManageMemoBooksDialog class."""

from gettext import gettext as _
from pathlib import Path

import wx
from ObjectListView import ColumnDefn, FastObjectListView

from memo.memobook import DEFAULT_MEMOBOOK_SETTINGS, MemoBook


class DeleteMemoBookDialog(wx.Dialog):
    """This class is a dialog for deleting MemoBook."""

    def __init__(self, parent, memobook_name):
        """Initialize DeleteMemoBookDialog."""
        super().__init__(parent, title=_("Delete MemoBook"), size=(400, 300))
        self.app_window = parent
        self.memobook_name = memobook_name
        self._create_ui()
        # size 800x600, position in the center of the screen
        self.SetSize((800, 600))
        self.Centre()

    def _create_ui(self):
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        # message
        self.label_message = wx.StaticText(
            self.panel, label=_("Do you want to delete MemoBook {}?").format(self.memobook_name)
        )
        self.sizer.Add(self.label_message, 0, wx.EXPAND | wx.ALL, 10)
        # checkbox
        self.checkbox_delete_from_disk = wx.CheckBox(self.panel, label=_("Delete from disk"))
        self.sizer.Add(self.checkbox_delete_from_disk, 0, wx.EXPAND | wx.ALL, 10)
        # buttons
        self.button_yes = wx.Button(self.panel, label=_("Yes"))
        self.button_yes.Bind(wx.EVT_BUTTON, self.on_button_yes_clicked)
        self.button_no = wx.Button(self.panel, label=_("No"))
        self.button_no.Bind(wx.EVT_BUTTON, self.on_button_no_clicked)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.button_yes, 0, wx.EXPAND, 10)
        buttons_sizer.Add(self.button_no, 0, wx.EXPAND, 10)
        self.sizer.Add(buttons_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.panel.SetSizer(self.sizer)

    def on_button_yes_clicked(self, event):
        """Delete MemoBook."""
        self.EndModal(wx.ID_YES)

    def on_button_no_clicked(self, event):
        """Do not delete MemoBook."""
        self.EndModal(wx.ID_NO)

    @property
    def delete_from_disk(self):
        """Get delete from disk checkbox value."""
        return self.checkbox_delete_from_disk.GetValue()


class ManageMemoBooksDialog(wx.Dialog):
    """This class is a dialog for managing MemoBooks."""

    def __init__(self, parent):
        """Initialize ManageMemoBooksDialog."""
        super().__init__(parent, title=_("Manage MemoBooks"), size=(400, 300))
        self.app_window = parent
        self._create_ui()
        # size 800x600, position in the center of the screen
        self.SetSize((800, 600))
        self.Centre()

    def _create_ui(self):
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        # left - list with memobooks names, no columns headers
        self.list_memobooks = FastObjectListView(self.panel, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.list_memobooks.SetColumns(
            [
                ColumnDefn(_("MemoBooks"), "left", 700, valueGetter=lambda x: x),
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
        self.list_memobooks.GetSelectedObject()
        self.button_move_up.Enable(index > 0)
        self.button_move_down.Enable(index < len(self.app_window.settings["memobooks"]) - 1)
        self.button_delete_memobook.Enable(self.list_memobooks.GetItemCount() > 1)

    def _is_memobook_name_used(self, name):
        """Check if memobook name is already used."""
        return any(item == name for item in self.app_window.settings["memobooks"])

    def on_button_create_memobook_clicked(self, event):
        """Create new MemoBook."""
        # TODO

    def on_button_add_external_memobook_clicked(self, event):
        """Add external MemoBook."""
        # ask for folder
        dlg = wx.DirDialog(self, _("Select MemoBook folder"))
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        folder_str_path = dlg.GetPath()
        # check if folder is already in list
        for item in self.app_window.settings["memobooks"]:
            if item == folder_str_path:
                wx.MessageBox(_("This MemoBook is already used."), _("Error"), wx.OK | wx.ICON_ERROR)
                return
        folder_path = Path(folder_str_path)
        memobook = MemoBook.create(folder_path, default_settings=DEFAULT_MEMOBOOK_SETTINGS, exist_ok=True)
        self.app_window.settings["memobooks"].append(str(memobook.path))
        self.app_window.settings.save()
        self.list_memobooks.SetObjects(self.app_window.settings["memobooks"])
        self.list_memobooks.Focus(len(self.app_window.settings["memobooks"]) - 1)
        self.list_memobooks.Select(len(self.app_window.settings["memobooks"]) - 1)

    def on_button_delete_memobook_clicked(self, event):
        """Delete selected item."""
        # get confirmation
        index = self.list_memobooks.GetFocusedItem()
        item = self.list_memobooks.GetSelectedObject()
        # dialog: yes, no, checkbox for delete from disk
        dlg = DeleteMemoBookDialog(self, item)
        if dlg.ShowModal() == wx.ID_NO:
            return
        # delete from list
        self.app_window.settings["memobooks"].remove(item)
        self.list_memobooks.SetObjects(self.app_window.settings["memobooks"])
        self.list_memobooks.Focus(index - 1)
        self.list_memobooks.Select(index - 1)
        # delete from disk
        if dlg.delete_from_disk:
            # TODO
            pass
        self.app_window.settings.save()

    def on_button_move_up_clicked(self, event):
        """Move selected item up."""
        index = self.list_memobooks.GetFocusedItem()
        item = self.list_memobooks.GetSelectedObject()
        self.app_window.settings["memobooks"].remove(item)
        self.app_window.settings["memobooks"].insert(index - 1, item)
        self.app_window.settings.save()
        self.list_memobooks.SetObjects(self.app_window.settings["memobooks"])
        self.list_memobooks.Focus(index - 1)
        self.list_memobooks.Select(index - 1)

    def on_button_move_down_clicked(self, event):
        """Move selected item down."""
        index = self.list_memobooks.GetFocusedItem()
        item = self.list_memobooks.GetSelectedObject()
        self.app_window.settings["memobooks"].remove(item)
        self.app_window.settings["memobooks"].insert(index + 1, item)
        self.app_window.settings.save()
        self.list_memobooks.SetObjects(self.app_window.settings["memobooks"])
        self.list_memobooks.Focus(index + 1)
        self.list_memobooks.Select(index + 1)

    def on_button_close_clicked(self, event):
        """Close dialog."""
        self.Close()
