import wx
import wx.aui
import src.engine
import src.gui.error
import logging
logger = logging.getLogger(__name__)
ID = wx.NewIdRef()
name="Vacuum_Toolbar"
toolbar = None
pane = None
paneinfo=None
parent=None

pump_value = -50.0

class PumpPopup(wx.PopupTransientWindow):
    def __init__(self, parent, style=wx.BORDER_SIMPLE):
        super().__init__(parent, style)
        self.txt = wx.TextCtrl(self, value=str(pump_value), size=(100, -1), style=wx.TE_PROCESS_ENTER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.txt, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.txt.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
        self.txt.Bind(wx.EVT_CHAR_HOOK, self.on_key)

    def on_key(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Dismiss()
        else:
            event.Skip()

    def on_enter(self, event):
        global pump_value
        pump_value = float(self.txt.GetValue())
        print(f"Value set: {pump_value}")
        self.Dismiss()


def create(parent_frame):
    global name,toolbar, pane, paneinfo, parent
    parent=parent_frame
    toolbar = wx.aui.AuiToolBar(parent_frame, ID, style=wx.aui.AUI_TB_DEFAULT_STYLE|wx.aui.AUI_TB_TEXT)
    toolbar.AddTool(1, "Pump", wx.ArtProvider.GetBitmap("vacuum-pump",   wx.ART_OTHER, (32,32)), "Pump",  wx.ITEM_NORMAL)
    toolbar.SetToolDropDown(1, True)
    # toolbar.SetToolSticky(1, True)
    toolbar.AddSeparator()
    toolbar.AddTool(2, "Left",  wx.ArtProvider.GetBitmap("vacuum-valve", wx.ART_OTHER, (32,32)), "valve1", wx.ITEM_CHECK)
    toolbar.AddTool(3, "Right", wx.ArtProvider.GetBitmap("vacuum-valve", wx.ART_OTHER, (32,32)), "valve2", wx.ITEM_CHECK)
    toolbar.Bind(wx.EVT_TOOL, on_click, id=wx.ID_ANY)
    toolbar.Bind(wx.aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, on_dropdown, id=wx.ID_ANY)
    paneinfo=wx.aui.AuiPaneInfo().Name(name).ToolbarPane().Top().Floatable(True).CloseButton(True).Show(True)
    parent_frame.aui_mgr.AddPane(toolbar, paneinfo)
    src.engine.engine.subscribers.append(update)
    toolbar.Realize()
    return toolbar

def on_click(event):
    state = ["0","1"][event.IsChecked()]
    match event.GetId():
        case 1: 
            val="0" if toolbar.GetToolSticky(1) else pump_value
            command=f"SET_PUMP_PRESSURE PUMP=PUMP TARGET={val}"
        case 2: command=f"VALVE_SET VALVE=NL VALUE={state}"
        case 3: command=f"VALVE_SET VALVE=NR VALUE={state}"
        case _: logging.warning("unhandled event in %s"%(name)); return
    src.engine.engine.queue.put(("response", {"sub":"gcode","params":{"toolbar":'pressure',"command":command}}, None))
    src.engine.engine.send_command("gcode/script", {"script": command},src.gui.error.gcode_error_callback)

def on_dropdown(event):
    if not event.IsDropDownClicked():
        event.Skip()
        return
    popup = PumpPopup(toolbar)
    rect = event.GetItemRect()
    pos = toolbar.ClientToScreen(wx.Point(rect.x, rect.y + rect.height))
    popup.Position(pos, (0, 0))
    wx.CallAfter(popup.Popup)


def add_to_menu(menu):
    item = menu.AppendCheckItem(ID, "Vacuum toolbar")
    item.Check(True)
    menu.Bind(wx.EVT_MENU, on_toggle, id=ID)
    return item

def on_toggle(event):
    parent.aui_mgr.GetPane(name).Show(event.IsChecked())
    parent.aui_mgr.Update()

def update(response):
    global pump_value
    if 'pressure_valve LEFT' in response['status']:
        state = response['status']['pressure_valve LEFT']
        if 'on' in state: 
            toolbar.SetToolSticky(2, state['on'])
            toolbar.Refresh()
    if 'pressure_valve RIGHT' in response['status']:
        state = response['status']['pressure_valve RIGHT']
        if 'on' in state:
            toolbar.SetToolSticky(3, state['on'])
            toolbar.Refresh()
    if "pressure_pump PUMP" in response['status']:
        state = response['status']["pressure_pump PUMP"]
        if 'power' in state: 
            toolbar.SetToolSticky(1, state['power']!=0)
            toolbar.Refresh()
        if 'target' in state and state['target']!=0: 
            pump_value=state['target'] #store last nonzero value for next time the pump is turned on
            toolbar.Refresh()
