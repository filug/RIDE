#  Copyright 2008-2009 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the 'License');
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an 'AS IS' BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  S    ee the License for the specific language governing permissions and
#  limitations under the License.

import wx

from robotide.editors import Editor
from robotide.ui import MenuEntries
from robotide.publish import RideTreeSelection, RideNotebookTabChange,\
                           RideSavingDatafile

from plugin import Plugin


_TOOLS = """
[Tools]
!Open &Editor | Opens suite/resource editor
"""
_EDIT = """
[Edit]
&Undo | Undo last modification | Ctrl-Z
---
Cu&t | Cut | Ctrl-X
&Copy | Copy | Ctrl-C
&Paste | Paste | Ctrl-V
&Delete | Delete  | Del
---
Comment | Comment selected rows | Ctrl-3
Uncomment | Uncomment selected rows | Ctrl-4
"""


class EditorPlugin(Plugin):

    def __init__(self, application):
        Plugin.__init__(self, application, initially_active=True)
        self._tab = None

    def activate(self):
        self._show_editor()
        self.register_menu_entries(MenuEntries(_TOOLS, self))
        self.register_menu_entries(MenuEntries(_EDIT, self._tab, self._tab))
        self.subscribe(self.OnTreeItemSelected, RideTreeSelection)
        self.subscribe(self.OnSaveToModel, RideNotebookTabChange)
        self.subscribe(self.OnSaveToModel, RideSavingDatafile)

    def _show_editor(self, item=None):
        if not self._tab:
            self._tab = self._create_tab()
        self._tab.create_editor(item or self.get_selected_datafile())

    def _create_tab(self):
        tab = _EditorTab(self.notebook)
        self.add_tab(tab, 'Edit')
        return tab

    def deactivate(self):
        self.unergister_menu_entries()
        self.unsubscribe_all()
        self.delete_tab(self._tab)
        self._tab = None

    def OnTreeItemSelected(self, message):
        self._show_editor(message.item)

    def OnOpenEditor(self, event):
        self._show_editor()

    def OnSaveToModel(self, message):
        if self._tab:
            self._tab.save()


class _EditorTab(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.SUNKEN_BORDER)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.editor = None

    def create_editor(self, item):
        self.Show(False)
        if self.editor:
            self.editor.close()
            self.sizer.Clear()
        self.editor = Editor(item, self)
        self.sizer.Add(self.editor, 1, wx.ALL|wx.EXPAND)
        self.Layout()
        self.Show(True)

    def OnUndo(self, event):
        self.editor.undo()

    def OnCut(self, event):
        self.editor.cut()

    def OnCopy(self, event):
        self.editor.copy()

    def OnPaste(self, event):
        self.editor.paste()

    def OnDelete(self, event):
        self.editor.delete()

    def OnComment(self, event):
        self.editor.comment()

    def OnUncomment(self, event):
        self.editor.uncomment()

    def save(self, message=None):
        self.editor.save()
