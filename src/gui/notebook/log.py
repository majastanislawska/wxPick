import wx
ID = wx.NewIdRef()
name="Log"
panel = None
pane = None
paneinfo=None
parent=None

log_display=None

def create(notebook):
    global name,panel, pane, paneinfo, parent
    global log_display
    parent=notebook
    panel = wx.Panel(notebook, wx.ID_ANY, 
        wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
    sizer = wx.BoxSizer( wx.VERTICAL )
    log_display = wx.TextCtrl(panel, 
        style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
    log_display.SetFont(wx.Font(16, wx.FONTFAMILY_TELETYPE,
        wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    sizer.Add(wx.StaticText(panel,
            label="Log Output:"), 0, wx.ALL, 5)
    sizer.Add(log_display, 1, wx.EXPAND | wx.ALL, 5)
    panel.SetSizer(sizer)
    panel.Layout()
    notebook.AddPage(panel, u"Logs", True )

def add_to_menu(menu):
    item = menu.AppendCheckItem(ID, "Log Notebook")
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