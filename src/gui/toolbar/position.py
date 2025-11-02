import wx
import wx.aui
import src.engine
import logging
logger = logging.getLogger(__name__)

ID = wx.NewIdRef()
name="Position"
toolbar = None
pane = None
paneinfo=None
parent=None

pos_x = None
pos_y = None
pos_z = None
pos_e = None
pos_a = None
pos_b = None

def create(parent_frame):
    global name,toolbar, pane, paneinfo, parent
    global pos_x, pos_y, pos_z, pos_e, pos_a, pos_b
    parent=parent_frame
    toolbar = wx.aui.AuiToolBar(parent_frame, style=wx.aui.AUI_TB_DEFAULT_STYLE | wx.aui.AUI_TB_TEXT)
    pos_x = wx.StaticText(toolbar, wx.ID_ANY, "0.000", wx.DefaultPosition, wx.Size( 150,-1 ), wx.ALIGN_RIGHT|wx.BORDER_RAISED )
    pos_y = wx.StaticText(toolbar, wx.ID_ANY, "0.000", wx.DefaultPosition, wx.Size( 150,-1 ), wx.ALIGN_RIGHT|wx.BORDER_RAISED )
    pos_z = wx.StaticText(toolbar, wx.ID_ANY, "0.000", wx.DefaultPosition, wx.Size( 150,-1 ), wx.ALIGN_RIGHT|wx.BORDER_RAISED )
    pos_e = wx.StaticText(toolbar, wx.ID_ANY, "0.000", wx.DefaultPosition, wx.Size( 150,-1 ), wx.ALIGN_RIGHT|wx.BORDER_RAISED )
    pos_a = wx.StaticText(toolbar, wx.ID_ANY, "0.000", wx.DefaultPosition, wx.Size( 150,-1 ), wx.ALIGN_RIGHT|wx.BORDER_RAISED )
    pos_b = wx.StaticText(toolbar, wx.ID_ANY, "0.000", wx.DefaultPosition, wx.Size( 150,-1 ), wx.ALIGN_RIGHT|wx.BORDER_RAISED )
    for ctrl,label in zip([pos_x, pos_y, pos_z, pos_e, pos_a, pos_b],"XYZEAB"):
        ctrl.SetFont(wx.Font(18, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        ctrl.SetMinSize( wx.Size( 80,-1 ))
        ctrl.Wrap(-1)
        toolbar.AddControl(ctrl,label=label)
    paneinfo= wx.aui.AuiPaneInfo().Name(name).ToolbarPane().Top().Floatable(True).CloseButton(True).Show(True)
    parent_frame.aui_mgr.AddPane(toolbar, paneinfo)
    toolbar.Realize()
    src.engine.engine.subscribers.append(update)
    return toolbar

def add_to_menu(menu):
    item = menu.AppendCheckItem(ID, "Position")
    item.Check(True)
    menu.Bind(wx.EVT_MENU, on_toggle, id=ID)
    return item

def on_toggle(event):
    parent.aui_mgr.GetPane(name).Show(event.IsChecked())
    parent.aui_mgr.Update()

def update(response):
    #{'eventtime': 293848.747924456, 'status': {'toolhead': {'position': [0.0, 470.0, -3.0, 0.0, 0.0, 0.0]}}}
    if not 'toolhead' in response['status']: return
    pos=response['status']['toolhead']['position']
    for coord,ctrl in zip(pos,[pos_x, pos_y, pos_z, pos_e, pos_a, pos_b]):
        ctrl.SetLabel(format(coord,"+03.3f"))
    toolbar.SendSizeEvent()
    toolbar.Refresh()