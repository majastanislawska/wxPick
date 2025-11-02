import wx
import wx.aui
import src.engine
import logging
logger = logging.getLogger(__name__)

ID = wx.NewIdRef()
name="State"
toolbar = None
pane = None
paneinfo=None
parent=None
state_pic =None
state_ctrl = None
state_message_ctrl = None
state_map = {
    "ready": None,
    "error": None,
    "startup": None,
    "shutdown": None
}
state_unknown=None

def create(parent_frame):
    global name,toolbar, pane, paneinfo, parent
    global state_pic, state_ctrl,state_message_ctrl,state_map,state_unknown
    parent=parent_frame
    state_map["ready"]=   wx.ArtProvider.GetBitmap("state-ready", wx.ART_OTHER, (32,32))
    state_map["error"]=   wx.ArtProvider.GetBitmap("state-error", wx.ART_OTHER, (32,32))
    state_map["startup"]= wx.ArtProvider.GetBitmap("state-startup", wx.ART_OTHER, (32,32))
    state_map["shutdown"]=wx.ArtProvider.GetBitmap("state-shutdown", wx.ART_OTHER, (32,32))
    state_unknown=wx.ArtProvider.GetBitmap("state-unknown", wx.ART_OTHER, (32,32))
    toolbar = wx.aui.AuiToolBar(parent_frame, ID, #size = wx.Size(300,64),
        style=wx.aui.AUI_TB_DEFAULT_STYLE | wx.aui.AUI_TB_TEXT) #|
    state_pic = wx.StaticBitmap(toolbar, wx.ID_ANY, state_unknown,size = wx.Size(32,32))
    toolbar.AddControl(state_pic) #,"state")
    state_ctrl = wx.StaticText(toolbar, size = wx.Size(80,32),label="unknown")
    state_ctrl.SetFont(wx.Font(16, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    toolbar.AddControl(state_ctrl,"state")
    toolbar.AddSeparator()
    state_message_ctrl = wx.StaticText(toolbar, size = wx.Size(250,32),label="no info")
    state_message_ctrl.SetFont(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    toolbar.AddControl(state_message_ctrl,"message")
    paneinfo= wx.aui.AuiPaneInfo().Name(name).ToolbarPane().Top().Floatable(True).CloseButton(True)
    parent_frame.aui_mgr.AddPane(toolbar, paneinfo)
    parent_frame.aui_mgr.GetPane(name).Show(True)
    toolbar.Realize()
    src.engine.engine.subscribers.append(update)
    return toolbar

def add_to_menu(menu):
    item = menu.AppendCheckItem(ID, "State")
    item.Check(True)
    menu.Bind(wx.EVT_MENU, on_toggle, id=ID)
    return item

def on_toggle(event):
    parent.aui_mgr.GetPane(name).Show(event.IsChecked())
    parent.aui_mgr.Update()

def update(response):
    # logger.info("%s.update: %s"%(name,response))
    if not 'status' in response: return
    if not 'webhooks' in response['status']: return
    r=response['status']['webhooks']
    state = r['state']
    message = str(r.get('state_message',[])).strip().splitlines()[0]
    state_pic.SetBitmap(state_map.get(state, state_unknown))
    state_ctrl.SetLabel(state)
    state_message_ctrl.SetLabel(message)
    toolbar.SendSizeEvent()
    toolbar.Refresh()