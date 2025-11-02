import wx
import wx.aui
import src.engine
import logging
logger = logging.getLogger(__name__)
ID = wx.NewIdRef()
name="Restart_Toolbar"
toolbar = None
pane = None
paneinfo=None
parent=None

def create(parent_frame):
    global name,toolbar, pane, paneinfo, parent
    parent=parent_frame
    toolbar = wx.aui.AuiToolBar(parent_frame, ID, style=wx.aui.AUI_TB_DEFAULT_STYLE) #|wx.aui.AUI_TB_TEXT)
    toolbar.AddTool(1, "EStop", wx.ArtProvider.GetBitmap("restart-emestop",   wx.ART_OTHER, (48,48)), "Emergency Stop",  wx.ITEM_NORMAL)
    toolbar.AddSeparator()
    toolbar.AddTool(2, "FWRestart", wx.ArtProvider.GetBitmap("restart-firmware", wx.ART_OTHER, (32,32)), "Firmware Restart", wx.ITEM_NORMAL)
    toolbar.AddTool(3, "Restart",          wx.ArtProvider.GetBitmap("restart",          wx.ART_OTHER, (32,32)), "Restart",          wx.ITEM_NORMAL)
    # toolbar.AddTool(4, "Connect",          wx.ArtProvider.GetBitmap("disconnected",          wx.ART_OTHER, (32,32)), "Connect",wx.ITEM_CHECK)
    toolbar.Bind(wx.EVT_TOOL, on_click, id=wx.ID_ANY)
    paneinfo=wx.aui.AuiPaneInfo().Name(name).ToolbarPane().Top().Floatable(True).CloseButton(True).Show(True)
    parent_frame.aui_mgr.AddPane(toolbar, paneinfo)
    toolbar.Realize()
    return toolbar

def on_click(event):
    match event.GetId():
        case 1: src.engine.engine.send_command("emergency_stop", {}),
        case 2: src.engine.engine.send_command("gcode/firmware_restart", {}),
        case 3: src.engine.engine.send_command("gcode/restart", {}),
        # case 4: handle_connect_button(event)
        case _: logging.warning("unhandled event in %s"%(name))

# def handle_connect_button(event):
#     logging.info("handle_connect_button %s"%event)

def add_to_menu(menu):
    item = menu.AppendCheckItem(ID, "Restart toolbar")
    item.Check(True)
    menu.Bind(wx.EVT_MENU, on_toggle, id=ID)
    return item

def on_toggle(event):
    parent.aui_mgr.GetPane(name).Show(event.IsChecked())
    parent.aui_mgr.Update()

