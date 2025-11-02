import wx
import src.gui.graph.system_stats
import src.gui.graph.temp
import logging
logger = logging.getLogger(__name__)
ID = wx.NewIdRef()
name="Graphs"
panel = None
pane = None
paneinfo=None
parent=None

def create(notebook):
    global name,panel, pane, paneinfo, parent
    parent=notebook
    panel = wx.ScrolledWindow(notebook)
    sizer = wx.BoxSizer(wx.VERTICAL)
    panel.SetSizer(sizer)
    panel.SetScrollRate(10, 10)
    sizer.Add(src.gui.graph.system_stats.create(panel), 0, wx.ALL | wx.EXPAND, 5)
    sizer.Add(src.gui.graph.temp.create(panel), 0, wx.ALL | wx.EXPAND, 5)
    notebook.AddPage(panel, "Graphs", False)
    sizer.Layout()
    return panel

def add_to_menu(menu):
    item = menu.AppendCheckItem(ID, "Graphs Notebook")
    item.Check(True)
    menu.Bind(wx.EVT_MENU, on_toggle, id=ID)
    return item

def on_toggle(event):
    is_checked = event.IsChecked()
    if is_checked: parent.AddPage(panel, name, select=True)
    else:
        page_index = parent.FindPage(panel)
        if page_index != wx.NOT_FOUND:
            parent.RemovePage(page_index)