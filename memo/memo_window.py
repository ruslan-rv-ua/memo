"""This module contains the GUI for the memo application."""

import json
from enum import Enum
from gettext import gettext as _
from pathlib import Path

import wx
import wx.html2
from courlan import check_url
from ObjectListView import ColumnDefn, FastObjectListView

from editor_window import EditorDialog
from memobook import MemoBook

MIN_CHARS_TO_SEARCH = 5
READABILITY_JS = (Path(__file__).parent / "Readability.js").read_text(encoding="utf-8")


class WebviewAction(Enum):
    """The actions that can be performed on the web view."""

    NONE = 0
    ADD_BOOKMARK = 1


class MemoBookWindow(wx.Frame):
    """The main window of the MemoBook application."""

    def __init__(self):
        """Create the main window."""
        style = wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL
        title = _("MemoBook")
        super().__init__(None, wx.ID_ANY, title, style=style)
        self.web_view_action = WebviewAction.NONE

        self.init_ui()
        self._open_memobook(Path(r"e:\dev\memo\test_memobook"))

    def _setup_menu(self):
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)

        # View menu
        self.menu_view = wx.Menu()

        self.menu_view_quick_search = self.menu_view.Append(wx.ID_ANY, _("Go to search\tCtrl+F"))
        self.Bind(wx.EVT_MENU, self._on_focus_quick_search, self.menu_view_quick_search)

        self.menu_view_goto_list = self.menu_view.Append(wx.ID_ANY, _("Go to memos list\tCtrl+L"))
        self.Bind(wx.EVT_MENU, self._on_focus_memos_list, self.menu_view_goto_list)

        self.menu_view_goto_web_view = self.menu_view.Append(wx.ID_ANY, _("Go to preview\tCtrl+W"))
        self.Bind(wx.EVT_MENU, self._on_focus_web_view, self.menu_view_goto_web_view)

        self.menu_view.AppendSeparator()

        self.menu_view_reset_search_results = self.menu_view.Append(wx.ID_ANY, _("Reset search results\tCtrl+R"))
        self.Bind(wx.EVT_MENU, self._on_reset_search_results, self.menu_view_reset_search_results)

        self.menubar.Append(self.menu_view, _("View"))

        # Memo menu
        self.menu_memo = wx.Menu()

        self.menu_memo_add_memo = self.menu_memo.Append(wx.ID_ANY, _("Add memo\tCtrl+M"))
        self.Bind(wx.EVT_MENU, self._on_add_memo, self.menu_memo_add_memo)

        self.menu_memo_add_bookmark = self.menu_memo.Append(wx.ID_ANY, _("Add bookmark\tCtrl+B"))
        self.Bind(wx.EVT_MENU, self._on_add_bookmark, self.menu_memo_add_bookmark)

        self.menu_memo_edit_memo = self.menu_memo.Append(wx.ID_ANY, _("Edit memo\tF4"))
        self.Bind(wx.EVT_MENU, self._on_edit_memo, self.menu_memo_edit_memo)

        self.menu_memo_delete_memos = self.menu_memo.Append(wx.ID_ANY, _("Delete selected memos\tDel"))
        self.Bind(wx.EVT_MENU, self._on_delete_memos, self.menu_memo_delete_memos)

        self.menubar.Append(self.menu_memo, _("Memo"))

    def init_ui(self):
        """Initialize the user interface."""
        self._setup_menu()

        self.panel = wx.Panel(self, wx.ID_ANY)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        ############################################################ left part
        # search box with label "Quick search"
        self.search_label = wx.StaticText(self.panel, wx.ID_ANY, _("Quick search"))
        self.search_text = wx.TextCtrl(self.panel, wx.ID_ANY, "")
        # bind search text events
        self.search_text.Bind(wx.EVT_TEXT, lambda event: self._update_memos())

        self.search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_sizer.Add(self.search_label, 0, wx.ALL | wx.EXPAND, 5)
        self.search_sizer.Add(self.search_text, 1, wx.ALL | wx.EXPAND, 5)

        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.left_sizer.Add(self.search_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.list_memos = FastObjectListView(
            self.panel,
            wx.ID_ANY,
            cellEditMode=FastObjectListView.CELLEDIT_F2ONLY,
            useAlternateBackColors=True,
        )
        self.list_memos.SetEmptyListMsg(_("No memos found"))
        self.list_memos.Bind(wx.EVT_LIST_ITEM_FOCUSED, self._on_focus_memo)
        self.list_memos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_activate_memo)
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

        self.Maximize(True)

        # bind events
        self.Bind(wx.html2.EVT_WEBVIEW_LOADED, self._on_web_view_loaded, self.web_view)
        self.Bind(wx.html2.EVT_WEBVIEW_ERROR, self._on_web_view_error, self.web_view)

    def _open_memobook(self, memobook_path: Path):
        """Open the memobook at the given path."""
        self.memobook = MemoBook(memobook_path)

        def rename_memo(memo, new_name):
            new_name = new_name.strip()
            if not new_name or new_name == memo["name"]:
                return
            memo_content = self.memobook.get_memo_markdown(memo["name"])
            name = self.memobook.add_memo(markdown=memo_content, name=new_name, add_date_hashtag=False)
            if name is None:
                wx.MessageBox(
                    _(
                        "Invalid memo name. Memo names must be unique and cannot contain the following characters: "
                        '/ \\ : * ? ! " < > |'
                    ),
                    _("Error"),
                    wx.OK | wx.ICON_ERROR,
                )
                return
            self.memobook.delete_memo(memo["name"])
            self._update_memos(name)

        self.list_memos.SetColumns([ColumnDefn(_("Memo"), "left", 800, "name", valueSetter=rename_memo)])
        self._update_memos(focus_on=0)

    def _update_memos(self, focus_on: str | int | None = None):
        """Update the list of memos.

        Args:
            focus_on: The item to focus on.
                If None, the focus will be not changed.
                If an int, the index of the item to focus on.
                If a str, the name of the memo to focus on.
                If True, the search text will be reset to an empty string and first item will be focused.
        """
        search_text = self.search_text.GetValue()
        if len(search_text) < MIN_CHARS_TO_SEARCH:
            self.data = self.memobook.get_memos()
        else:
            search_words = search_text.lower().split()
            include = []
            exclude = []
            for word in search_words:
                if word.startswith("-"):
                    exclude.append(word[1:])
                else:
                    include.append(word)
            # filter memos
            self.data = self.memobook.search(
                include=include, exclude=exclude, quick_search=False
            )  # TODO: quick_search=True
        self.list_memos.SetObjects(self.data)
        if len(self.data) == 0:
            self.web_view.SetPage("<h1>No memos found</h1>", "")  # TODO: use "about app" page
            return
        if focus_on is None:
            return
        if isinstance(focus_on, str):
            focus_on = self._get_memo_index(focus_on)
            if focus_on is None:
                focus_on = 0
        else:  # int, in range [0, len(self.data) - 1]
            focus_on = max(0, min(focus_on, len(self.data) - 1))
        self.list_memos.Select(focus_on)
        self.list_memos.Focus(focus_on)
        return

    def _get_focused_memo(self):
        """Get the focused memo.

        Returns:
            The focused memo, or None if no memo was focused.
        """
        focused_memo_index = self.list_memos.GetFocusedItem()
        if focused_memo_index == -1:
            return None
        return self.data[focused_memo_index]

    def _get_memo_index(self, name: str):
        """Get the index of the memo with the given name.

        Args:
            name: The name of the memo.

        Returns:
            The index of the memo with the given title, or None if no memo was found.
        """
        for i, memo in enumerate(self.data):
            if memo["name"] == name:
                return i
        return None

    ######################################## menu events

    def _on_focus_quick_search(self, event):
        self.search_text.SetFocus()

    def _on_focus_memos_list(self, event):
        self.list_memos.SetFocus()

    def _on_focus_web_view(self, event):
        self.web_view.SetFocus()

    def _on_reset_search_results(self, event):
        self.search_text.SetValue("")
        self._update_memos(focus_on=0)

    def _on_add_memo(self, event):
        edit_dlg = EditorDialog(parent=self, title=_("Add memo"), value="")
        if edit_dlg.ShowModal() != wx.ID_OK:
            return
        markdown = edit_dlg.value
        name = self.memobook.add_memo(markdown=markdown, add_date_hashtag=True)
        self._on_reset_search_results(None)
        self._update_memos(name)

    def _on_add_bookmark(self, event):
        """Add a bookmark."""
        # ask bookmark's URL
        self.url = wx.GetTextFromUser(_("Enter the URL of the bookmark"), _("Add bookmark"), "")
        if not self.url:
            return
        # validate URL
        try:
            self.url, self.domain_name = check_url(self.url)
            if not self.url:
                wx.MessageBox(_("Invalid URL"), _("Error"), wx.OK | wx.ICON_ERROR)
                return
        except TypeError:
            wx.MessageBox(_("Invalid URL"), _("Error"), wx.OK | wx.ICON_ERROR)
            return

        self.web_view.LoadURL(self.url)
        self.web_view_action = WebviewAction.ADD_BOOKMARK
        return

    def _on_web_view_loaded(self, event):
        if self.web_view_action == WebviewAction.ADD_BOOKMARK:
            self.web_view_action = WebviewAction.NONE
            self._add_bookmark()

    def _on_web_view_error(self, event):
        if self.web_view_action == WebviewAction.ADD_BOOKMARK:
            wx.MessageBox(_("Could not load the page"), _("Error"), wx.OK | wx.ICON_ERROR)
            self.web_view_action = WebviewAction.NONE

    def _add_bookmark(self):
        """Add a bookmark."""
        success, article_json = self.web_view.RunScript(READABILITY_JS)
        article = json.loads(article_json)
        if not success or not article_json:
            wx.MessageBox(_("Could not get the page"), _("Error"), wx.OK | wx.ICON_ERROR)
            return

        readable_html = article["content"]
        name = f"{article['title']} ({self.domain_name})" if article["title"] else self.domain_name
        name = self.memobook.add_memo_from_html(
            html=readable_html, name=name, add_date_hashtag=True, extra_hashtags=[_("#bookmark")]
        )
        parsed_markdown = self.memobook.get_memo_markdown(name)
        memo_markdown = f"<{self.url}>\n\n{parsed_markdown}"
        self.memobook.update_memo(name=name, markdown=memo_markdown)

        self._on_reset_search_results(None)
        self._update_memos(name)

    def _on_edit_memo(self, event):
        item = self._get_focused_memo()
        if not item:
            return
        name = item["name"]
        content = self.memobook.get_memo_markdown(name)
        edit_dlg = EditorDialog(parent=self, title=_("Edit memo"), value=content)
        if edit_dlg.ShowModal() != wx.ID_OK:
            return
        markdown = edit_dlg.value
        name = self.memobook.update_memo(name=name, markdown=markdown)
        self._update_memos(name)

    def _on_delete_memos(self, event):
        # get selected memos
        selected_items = self.list_memos.GetSelectedObjects()
        if not selected_items:
            return
        if (
            wx.MessageBox(
                _("Are you sure you want to delete the selected memos?"),
                _("Confirm deletion"),
                wx.YES_NO | wx.ICON_WARNING,
            )
            != wx.YES
        ):
            return
        # delete memos
        focused_item_index = self.list_memos.GetFocusedItem()
        for item in selected_items:
            self.memobook.delete_memo(item["name"])
        self._update_memos(focus_on=focused_item_index)

    ######################################## list events

    def _on_focus_memo(self, event):
        """Select a memo."""
        item = self._get_focused_memo()
        html = self.memobook.get_memo_html(item["name"])
        self.web_view.SetPage(html, "")

    def _on_activate_memo(self, event):
        """Open in browser first link in Web view."""
        # get first link
        success, first_link = self.web_view.RunScript("document.querySelector('a').href")
        if not success:
            return
        # open link in browser
        wx.LaunchDefaultBrowser(first_link)
