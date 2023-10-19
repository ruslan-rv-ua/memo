"""This module contains the GUI for the memo application."""

# TODO: DEBUG only, remove in production
from snoop import snoop, pp  # noqa: F401, I001

import json
import os
from enum import Enum
from gettext import gettext as _
from pathlib import Path

import wx
import wx.html2

from bookmark_dialog import BookmarkDialog
from editor_window import EditorDialog
from memobook import DEFAULT_MEMOBOOK_SETTINGS, MemoBook
from ObjectListView2 import ColumnDefn, FastObjectListView
from utils import Settings, get_domain_name_from_url, validate_url

MEMOBOOKS_DIR_NAME = "memobooks"
DEFAULT_MEMOBOOK_NAME = _("My Memos")  # TRANSLATORS: This is the name of the default memobook.
DEFAULT_APP_SETTINGS = {"memobooks_dir": MEMOBOOKS_DIR_NAME, "last_opened_memobook": None, "memobooks": []}

MIN_CHARS_TO_SEARCH = 5
READABILITY_JS = (Path(__file__).parent / "Readability.js").read_text(encoding="utf-8")


class WebviewAction(Enum):
    """The actions that can be performed on the web view."""

    NONE = 0
    ADD_BOOKMARK = 1


class MemoBookWindow(wx.Frame):
    """The main window of the MemoBook application."""

    def __init__(self, work_dir: Path):
        """Create the main window.

        Args:
            work_dir: The path to the directory where the memobook is stored.
        """
        style = wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL
        title = _("MemoBook")
        super().__init__(None, wx.ID_ANY, title, style=style)

        self.work_dir = work_dir
        self._settings_path = self.work_dir / ".settings"
        if not self._settings_path.exists():
            Settings.create(self._settings_path, DEFAULT_APP_SETTINGS)
        self.settings = Settings(self._settings_path)

        memobooks_path = Path(self.settings["memobooks_dir"])
        self.memobooks_path = self.work_dir / memobooks_path if not memobooks_path.is_absolute() else memobooks_path
        if not self.memobooks_path.exists():
            self.memobooks_path.mkdir()
        self.web_view_action = WebviewAction.NONE

        self.init_ui()
        self._load_memobooks()

    def _get_memobook_path(self, str_path: str) -> Path:
        """Get the path to a file in the memobook.

        Args:
            str_path: The path to the file.


        Returns:
            The path to the file in the memobook.


        Raises:
            FileNotFoundError: If the file does not exist.

        """
        p = Path(str_path)
        return p if p.is_absolute() else self.memobooks_path / p

    def _load_memobooks(self):
        """Load the memobooks.

        Remove memobooks that do not exist.
        Create a default memobook if there are no any.
        """
        memobooks_to_remove = []
        for memobook_str_path in self.settings["memobooks"]:
            memobook_path = self._get_memobook_path(memobook_str_path)
            if not memobook_path.exists():
                memobooks_to_remove.append(memobook_str_path)
                continue
            try:
                MemoBook(memobook_path)
            except FileNotFoundError:
                memobooks_to_remove.append(memobook_str_path)
                continue
        for memobook_str_path in memobooks_to_remove:
            self.settings["memobooks"].remove(memobook_str_path)
        self.settings.save()
        if not self.settings["memobooks"]:
            # create default memobook if there are no any.
            memobook_path = self.memobooks_path / DEFAULT_MEMOBOOK_NAME
            MemoBook.create(memobook_path, DEFAULT_MEMOBOOK_SETTINGS, exist_ok=True)
            self.settings["memobooks"].append(DEFAULT_MEMOBOOK_NAME)
            self.settings["last_opened_memobook"] = DEFAULT_MEMOBOOK_NAME
            self.settings.save()
        self._build_memobooks_menu()
        # open last opened memobook
        if self.settings["last_opened_memobook"] not in self.settings["memobooks"]:
            self.settings["last_opened_memobook"] = self.settings["memobooks"][0]
        self._open_memobook(self.settings["last_opened_memobook"])

    def _build_memobooks_menu(self):
        """Build the memobooks menu."""
        # clear menu
        for item in self.menu_memobooks_menu_open.GetMenuItems():
            self.menu_memobooks_menu_open.Delete(item)

        for i, memobook_str_path in enumerate(self.settings["memobooks"][:9], start=1):
            menu_item = self.menu_memobooks_menu_open.AppendRadioItem(wx.ID_ANY, memobook_str_path + f"\tCtrl+{i}")
            menu_item.Check(memobook_str_path == self.settings["last_opened_memobook"])
            self.Bind(
                wx.EVT_MENU,
                lambda event, str_path=memobook_str_path: self._open_memobook(str_path),
                menu_item,
            )
        for i, memobook_str_path in enumerate(self.settings["memobooks"][9:]):  # noqa: B007
            menu_item = self.menu_memobooks_menu_open.AppendRadioItem(wx.ID_ANY, memobook_str_path)
            menu_item.Check(memobook_str_path == self.settings["last_opened_memobook"])
            self.Bind(
                wx.EVT_MENU,
                lambda event, str_path=memobook_str_path: self._open_memobook(str_path),
                menu_item,
            )
        self.menu_memobooks_delete.Enable(len(self.settings["memobooks"]) > 1)

    def _setup_menu(self):
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)

        # memobooks menu
        self.menu_memobooks = wx.Menu()
        self.menubar.Append(self.menu_memobooks, _("MemoBook"))
        # `open` sub-menu
        self.menu_memobooks_menu_open = wx.Menu()
        self.menu_memobooks_open = self.menu_memobooks.AppendSubMenu(self.menu_memobooks_menu_open, _("Open"))
        # rest of the menu is built in `_build_open_memobook_menu`

        self.menu_memobooks_new = self.menu_memobooks.Append(wx.ID_ANY, _("New\tF7"))
        self.Bind(wx.EVT_MENU, self._on_new_internal_memobook, self.menu_memobooks_new)

        self.menu_memobooks_add = self.menu_memobooks.Append(wx.ID_ANY, _("Connect\tCtrl+F7"))
        self.Bind(wx.EVT_MENU, self._on_add_external_memobook, self.menu_memobooks_add)

        self.menu_memobooks_delete = self.menu_memobooks.Append(wx.ID_ANY, _("Delete\tF8"))
        self.Bind(wx.EVT_MENU, self._on_delete_memobook, self.menu_memobooks_delete)

        ##### Search menu
        self.menu_search = wx.Menu()
        self.menubar.Append(self.menu_search, _("Search"))

        self.menu_search_reset_results = self.menu_search.Append(wx.ID_ANY, _("Reset search results\tEsc"))
        self.Bind(wx.EVT_MENU, self._on_reset_search_results, self.menu_search_reset_results)

        ##### Memo menu
        self.menu_memo = wx.Menu()

        self.menu_memo_add_memo = self.menu_memo.Append(wx.ID_ANY, _("Add memo\tCtrl+M"))
        self.Bind(wx.EVT_MENU, self._on_add_memo, self.menu_memo_add_memo)

        self.menu_memo_quick_add_bookmark = self.menu_memo.Append(wx.ID_ANY, _("Quick add bookmark\tCtrl+B"))
        self.Bind(wx.EVT_MENU, self._on_quick_add_bookmark, self.menu_memo_quick_add_bookmark)

        self.menu_memo_add_bookmark = self.menu_memo.Append(wx.ID_ANY, _("Add bookmark\tCtrl+Shift+B"))
        self.Bind(wx.EVT_MENU, self._on_add_bookmark, self.menu_memo_add_bookmark)

        self.menu_memo_edit_memo = self.menu_memo.Append(wx.ID_ANY, _("Edit\tF4"))
        self.Bind(wx.EVT_MENU, self._on_edit_memo, self.menu_memo_edit_memo)

        self.menu_memo_delete_memos = self.menu_memo.Append(wx.ID_ANY, _("Delete selected\tDel"))
        self.Bind(wx.EVT_MENU, self._on_delete_memos, self.menu_memo_delete_memos)

        self.menubar.Append(self.menu_memo, _("Memo"))

    def init_ui(self):
        """Initialize the user interface."""
        self._setup_menu()

        self.panel = wx.Panel(self, wx.ID_ANY)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        ############################################################ left part
        # search box with label "Quick search"
        self.search_label = wx.StaticText(self.panel, wx.ID_ANY, _("Search"))
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

        # bind WebView events
        self.Bind(wx.html2.EVT_WEBVIEW_LOADED, self._on_webview_loaded, self.web_view)
        self.Bind(wx.html2.EVT_WEBVIEW_ERROR, self._on_webview_error, self.web_view)
        self.Bind(wx.html2.EVT_WEBVIEW_NEWWINDOW, self._on_webview_newwindow, self.web_view)
        """ TODO: bind events if needed
        self.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, self._on_webview_navigating, self.web_view)
        self.Bind(wx.html2.EVT_WEBVIEW_NAVIGATED, self._on_webview_navigated, self.web_view)
        """

    def _open_memobook(self, memobook_str_path: Path):
        """Open the memobook at the given path."""
        memobook_path = self._get_memobook_path(memobook_str_path)
        self.memobook = MemoBook(memobook_path)

        def rename_memo(memo, new_name):
            new_name = new_name.strip()
            if not new_name or new_name == memo["name"]:
                return
            name = self.memobook.rename_memo(old_name=memo["name"], new_name=new_name)
            self._update_memos(name)

        self.list_memos.SetFocus()
        self.list_memos.SetColumns([ColumnDefn(self.memobook.name, "left", 800, "name", valueSetter=rename_memo)])
        self._update_memos(focus_on=0)
        self.settings["last_opened_memobook"] = memobook_str_path
        self.settings.save()
        self.search_label.SetLabel(_("Search in") + f" {self.memobook.name}")

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
            self.data = self.memobook.search(include=include, exclude=exclude, quick_search=False)
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

    def _get_webview_links(self):
        """Get all links in the web view.

        Returns:
            A list of dicts with the following keys: "url", "text" or None if no links were found.
        """
        success, links_str = self.web_view.RunScript(
            "const getAllLinks=()=>Array.from(document.querySelectorAll('a')).map(link=>({url:link.href,text:link.textContent.trim()}));getAllLinks();"  # noqa: E501
        )
        if not success or not links_str:
            return None
        return json.loads(links_str)

    ######################################## menu events
    # memobooks menu
    ######################################## menu events

    def _on_new_internal_memobook(self, event):
        """Create a new internal memobook."""
        memobook_name = wx.GetTextFromUser(_("Enter the name of the memobook"), _("New memobook"), "")
        if not memobook_name:
            return
        memobook_name = MemoBook.make_file_stem_from_string(memobook_name)
        if memobook_name in self.settings["memobooks"]:
            wx.MessageBox(_("A memobook with this name already exists"), _("Error"), wx.OK | wx.ICON_ERROR)
            return
        # create memobook
        memobook_path = self.memobooks_path / memobook_name
        MemoBook.create(memobook_path, DEFAULT_MEMOBOOK_SETTINGS, exist_ok=True)
        self.settings["memobooks"].append(memobook_name)
        self.settings.save()
        self._build_memobooks_menu()
        self._open_memobook(memobook_name)

    def _on_add_external_memobook(self, event):
        """Add an external memobook."""
        # ask folder path
        dlg = wx.DirDialog(self, _("Choose a directory"), style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() != wx.ID_OK:
            return
        memobook_path = Path(dlg.GetPath())
        # check if memobook is in the memobooks settings
        if str(memobook_path) in self.settings["memobooks"]:
            wx.MessageBox(_("This memobook is already added"), _("Error"), wx.OK | wx.ICON_ERROR)
            return
        memobook = MemoBook.create(memobook_path, DEFAULT_MEMOBOOK_SETTINGS, exist_ok=True)
        if not memobook:
            wx.MessageBox(_("Could not create the memobook"), _("Error"), wx.OK | wx.ICON_ERROR)
            return
        self.settings["memobooks"].append(str(memobook.path))
        self.settings.save()
        self._build_memobooks_menu()
        self._open_memobook(str(memobook.path))

    def _on_delete_memobook(self, event):
        # ask confirmation
        if (
            wx.MessageBox(
                _("Are you sure you want to delete the memobook?"),
                _("Confirm deletion"),
                wx.YES_NO | wx.ICON_WARNING,
            )
            != wx.YES
        ):
            return
        # delete memobook from settings
        memobook_str_path = self.settings["last_opened_memobook"]
        self.settings["memobooks"].remove(memobook_str_path)
        self.settings.save()
        # message where files are left
        memobook_path = self._get_memobook_path(memobook_str_path)
        wx.MessageBox(
            _(f"The memobook has been deleted.\n\nBut files are left in the following directory:\n{memobook_path}"),
            _("Memobook deleted"),
            wx.OK | wx.ICON_INFORMATION,
        )
        # open another memobook
        self._open_memobook(self.settings["memobooks"][0])

    ############################################################ left part
    # view menu
    ############################################################ left part

    def _on_reset_search_results(self, event):
        """Reset the search results or exit the application."""
        if self.search_text.GetValue():
            self.search_text.SetValue("")
            self._update_memos(focus_on=0)
            return
        # ask confirmation, default button is "No"
        if (
            wx.MessageBox(
                _("Are you sure you want to exit the application?"),
                _("Confirm exit"),
                wx.YES_NO | wx.ICON_WARNING | wx.NO_DEFAULT,
            )
            != wx.YES
        ):
            return
        self.Close()

    ############################################################
    # memo menu
    ############################################################

    def _on_add_memo(self, event):
        edit_dlg = EditorDialog(parent=self, title=_("Add memo"), value="")
        if edit_dlg.ShowModal() != wx.ID_OK:
            return
        name = self.memobook.add_memo(edit_dlg.value)
        self.search_text.SetValue("")  # to reset the search results
        self._update_memos(name)

    def _get_url_from_clipboard(self):
        text_data = wx.TextDataObject()
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(text_data)
            wx.TheClipboard.Close()
        url = text_data.GetText() if success else ""
        if not validate_url(url):
            url = ""
        return url

    def _on_quick_add_bookmark(self, event):
        """Quickly add a bookmark.

        The URL is read from the clipboard, if possible.
        Parsing only title and description of the webpage.
        """
        clipboard_url = self._get_url_from_clipboard()
        url = wx.GetTextFromUser(_("Enter the URL of the bookmark"), _("Add bookmark"), clipboard_url)
        url = url.strip()
        if not url:
            return
        # validate URL
        if not validate_url(url):
            wx.MessageBox(_("Invalid URL"), _("Error"), wx.OK | wx.ICON_ERROR)
            return
        self.parse_params = {"include_bookmark_content": False}
        self.web_view_action = WebviewAction.ADD_BOOKMARK
        self.web_view.LoadURL(url)
        return

    def _on_add_bookmark(self, event):
        clipboard_url = self._get_url_from_clipboard()
        dlg = BookmarkDialog(
            parent=self,
            url=clipboard_url,
            include_links=self.memobook.settings["html_parser_include_links"],
            include_images=self.memobook.settings["html_parser_include_images"],
        )
        if dlg.ShowModal() != wx.ID_OK:
            return
        url = dlg.url.GetValue().strip()
        if not url:
            return
        # validate URL
        if not validate_url(url):
            wx.MessageBox(_("Invalid URL"), _("Error"), wx.OK | wx.ICON_ERROR)
            return
        self.parse_params = {
            "include_bookmark_content": True,
            "include_links": dlg.include_links,
            "include_images": dlg.include_images,
        }
        self.web_view_action = WebviewAction.ADD_BOOKMARK
        self.web_view.LoadURL(url)
        return

    def _on_webview_navigating(self, event):
        pass

    def _on_webview_navigated(self, event):
        pass

    def _on_webview_loaded(self, event):
        if self.web_view_action != WebviewAction.ADD_BOOKMARK or event.GetURL() == "about:blank":
            return
        self.web_view_action = WebviewAction.NONE
        self._add_bookmark()

    def _on_webview_error(self, event):
        if self.web_view_action == WebviewAction.ADD_BOOKMARK:
            wx.MessageBox(_("Could not load the page"), _("Error"), wx.OK | wx.ICON_ERROR)
            self.web_view_action = WebviewAction.NONE

    def _on_webview_newwindow(self, event):
        url = event.GetURL()
        os.startfile(url)  # noqa: S606

    def _add_bookmark(self):
        """Add a bookmark.

        Raises:
            ValueError: If the parse mode is invalid.
        """
        success, article_json = self.web_view.RunScript(READABILITY_JS)
        try:
            article = json.loads(article_json)
        except json.JSONDecodeError:
            article = None
        if not success or not article_json or not article:
            wx.MessageBox(_("Could not get the page"), _("Error"), wx.OK | wx.ICON_ERROR)
            self.web_view.LoadURL("about:blank")  # TODO: make help page
            return
        url = self.web_view.GetCurrentURL()
        domain_name = get_domain_name_from_url(url)
        memo_body = article["excerpt"]
        if self.parse_params["include_bookmark_content"] and article["content"]:
            memo_body = article["content"]
        memo_body = memo_body.strip()  # TODO: check if empty
        name = f"{article['title']} ({domain_name})" if article["title"] else domain_name
        name = self.memobook.add_memo_from_html(
            html=memo_body,
            name=name,
            title=article["title"],
            link=url,
            link_text=domain_name,
            parse_params=self.parse_params,
        )
        if not name:
            wx.MessageBox(_("Could not add the bookmark"), _("Error"), wx.OK | wx.ICON_ERROR)
            return
        self.parse_params = None
        self.search_text.SetValue("")  # to reset the search results TODO: make this a method
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
        """Show the memo in the web view."""
        item = self._get_focused_memo()
        html = self.memobook.get_memo_html(item["name"])
        self.web_view.SetPage(html, "")

    def _on_activate_memo(self, event):
        """Open in browser first link in Web view."""
        links = self._get_webview_links()
        # open first link in browser
        if links:
            wx.LaunchDefaultBrowser(links[0]["url"])
