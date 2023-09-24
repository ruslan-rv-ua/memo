"""This module contains the GUI for the memo application."""

from gettext import gettext as _
from pathlib import Path

import wx
import wx.html2
from ObjectListView import ColumnDefn, ObjectListView

from editor_window import EditorDialog
from memobook import MemoBook
from templates import memo_template
from utils import get_domain, get_page_description, get_page_html, get_page_markdown, get_page_title, is_valid_http_url


class MemoBookWindow(wx.Frame):
    """The main window of the MemoBook application."""

    def __init__(self):
        """Create the main window."""
        style = wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL
        title = _("MemoBook")
        super().__init__(None, wx.ID_ANY, title, style=style)

        self.init_ui()
        self._open_memobook(Path(r"e:\dev\memo\test_memobook"))

    def _setup_menu(self):
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)

        # View menu
        self.menu_view = wx.Menu()

        self.menu_view_quick_search = self.menu_view.Append(wx.ID_ANY, _("Quick search\tCtrl+F"))
        self.Bind(wx.EVT_MENU, self._on_focus_quick_search, self.menu_view_quick_search)

        self.menu_view_goto_list = self.menu_view.Append(wx.ID_ANY, _("Memos list\tCtrl+L"))
        self.Bind(wx.EVT_MENU, self._on_focus_memos_list, self.menu_view_goto_list)

        self.menu_view_goto_web_view = self.menu_view.Append(wx.ID_ANY, _("Web view\tCtrl+W"))
        self.Bind(wx.EVT_MENU, self._on_focus_web_view, self.menu_view_goto_web_view)

        self.menubar.Append(self.menu_view, _("View"))

        # Memo menu
        self.menu_memo = wx.Menu()

        self.menu_memo_add_memo = self.menu_memo.Append(wx.ID_ANY, _("Add memo\tCtrl+M"))
        self.Bind(wx.EVT_MENU, self._on_add_memo, self.menu_memo_add_memo)

        self.menu_memo_add_bookmark = self.menu_memo.Append(wx.ID_ANY, _("Add bookmark\tCtrl+B"))
        self.Bind(wx.EVT_MENU, self._on_add_bookmark, self.menu_memo_add_bookmark)

        self.menu_memo_edit_memo = self.menu_memo.Append(wx.ID_ANY, _("Edit memo\tF4"))
        self.Bind(wx.EVT_MENU, self._on_edit_memo, self.menu_memo_edit_memo)

        self.menubar.Append(self.menu_memo, _("Memo"))

    def init_ui(self):
        """Initialize the user interface."""
        self._setup_menu()

        self.panel = wx.Panel(self, wx.ID_ANY)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        ############################################################ left part
        # search box with label "Quick search"
        self.search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_label = wx.StaticText(self.panel, wx.ID_ANY, _("Quick search"))
        self.search_sizer.Add(self.search_label, 0, wx.ALL | wx.EXPAND, 5)
        self.search_text = wx.TextCtrl(self.panel, wx.ID_ANY, "")
        self.search_sizer.Add(self.search_text, 1, wx.ALL | wx.EXPAND, 5)

        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.left_sizer.Add(self.search_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.list_memos = ObjectListView(self.panel, wx.ID_ANY, style=wx.LC_REPORT)
        self.list_memos.SetEmptyListMsg(_("No memos found"))
        self.list_memos.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_select_memo)
        self.left_sizer.Add(self.list_memos, 1, wx.ALL | wx.EXPAND, 5)

        ############################################################ right part

        self.web_view = wx.html2.WebView.New(self.panel, wx.ID_ANY)

        # add left and right parts to main sizer
        self.main_sizer.Add(self.left_sizer, 1, wx.ALL | wx.EXPAND, 5)
        self.main_sizer.Add(self.web_view, 1, wx.ALL | wx.EXPAND, 5)

        # add main sizer to panel
        self.panel.SetSizer(self.main_sizer)
        self.panel.Layout()
        self.main_sizer.Fit(self.panel)

        # add panel to frame
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        # maximize the window
        self.Maximize(True)

    def _open_memobook(self, memobook_path: Path):
        """Open the memobook at the given path."""
        self.memobook = MemoBook(memobook_path)

        self.list_memos.SetColumns(
            [
                ColumnDefn(
                    _("Memo"), "left", 500, "file_name", stringConverter=lambda file_name: file_name[:-3]
                ),  # remove ".md"
            ]
        )

        self._update_memos()
        self._focus_list_memos()
        # focus first memo if any
        if self.list_memos.GetItemCount() > 0:
            self.list_memos.Select(0)
            self.list_memos.Focus(0)

    def _update_memos(self):
        """Update the list of memos."""
        objects = [{"file_name": file} for file in self.memobook.get_memos_file_names()]
        self.list_memos.SetObjects(objects)  # TODO: optimize performance

    def _focus_search_text(self):
        """Set the focus on the search text."""
        self.search_text.SetFocus()

    def _focus_list_memos(self):
        """Set the focus on the memos list."""
        self.list_memos.SetFocus()

    def _focus_web_view(self):
        """Set the focus on the web view."""
        self.web_view.SetFocus()

    ##### memo

    def _add_memo(self):
        """Add a memo."""
        edit_dlg = EditorDialog(parent=self, title=_("Add memo"), value="")
        if edit_dlg.ShowModal() != wx.ID_OK:
            return
        markdown = edit_dlg.value
        self.memobook.add_memo(markdown=markdown, add_date_hashtag=True)

    def _edit_memo(self, file_name: str):
        """Edit a memo."""
        memo = self.memobook.get_memo(file_name)
        edit_dlg = EditorDialog(parent=self, title=_("Edit memo"), value=memo.content)
        if edit_dlg.ShowModal() != wx.ID_OK:
            return
        markdown = edit_dlg.value
        self.memobook.update_memo(file_name, markdown=markdown)

    def _add_bookmark(self) -> bool:
        """Add a bookmark.

        Returns:
            True if the bookmark was added, False otherwise.
        """
        # ask bookmark's URL
        url = wx.GetTextFromUser(_("Enter the URL of the bookmark"), _("Add bookmark"), "")
        if not url:
            return False
        # validate URL
        if not is_valid_http_url(url):
            wx.MessageBox(_("Invalid URL"), _("Error"), wx.OK | wx.ICON_ERROR)
            return False

        page_html = get_page_html(url)
        # ask user to add bookmark anyway
        if (
            not page_html
            and wx.MessageBox(
                _("The URL is unreachable. Do you want to add it anyway?"),
                _("Warning"),
                wx.YES_NO | wx.ICON_WARNING,
            )
            != wx.YES
        ):
            return False

        domain = get_domain(url)
        if page_html:
            page_title = get_page_title(page_html)
            page_description = get_page_description(page_html)
            page_markdown = get_page_markdown(page_html)
        else:
            page_title = ""
            page_description = ""
            page_markdown = ""

        memo_title = f"{page_title} ({domain})" if page_title else domain
        markdown = ""
        if page_description:
            markdown += f"{page_description}\n\n"
        markdown += page_markdown.strip()
        markdown += f"\n\n---\n\n<{url}>"

        # add bookmark
        self.memobook.add_memo(
            markdown=markdown, title=memo_title, add_date_hashtag=False, extra_hashtags=["#bookmark"]
        )

        return True

    ######################################## menu events

    def _on_focus_quick_search(self, event):
        self.search_text.SetFocus()

    def _on_focus_memos_list(self, event):
        self._focus_list_memos()

    def _on_focus_web_view(self, event):
        self._focus_web_view()

    def _on_add_memo(self, event):
        self._add_memo()
        self._update_memos()

    def _on_add_bookmark(self, event):
        self._add_bookmark()
        self._update_memos()
        # focus last added bookmark
        last_item_index = self.list_memos.GetItemCount() - 1
        self.list_memos.Select(last_item_index)
        self.list_memos.Focus(last_item_index)

    def _on_edit_memo(self, event):
        selected_item_index = self.list_memos.GetFirstSelected()
        if selected_item_index == -1:
            return
        item = self.list_memos.GetSelectedObject()
        self._edit_memo(item["file_name"])
        self._update_memos()

    ######################################## list events

    def _on_select_memo(self, event):
        """Select a memo."""
        item = event.GetEventObject().GetSelectedObject()
        memo = self.memobook.get_memo(item["file_name"])
        markdown = memo.content
        html = memo_template.render(markdown=markdown, title=item["file_name"])
        self.web_view.SetPage(html, "")
