import wx
import src.engine
import src.gui.camera
import src.gui.error
import logging
logger = logging.getLogger(__name__)
#config
topcam_cv_id =1200
topcam_framerate=30
#"globals"
ID = wx.NewIdRef()
name="Topcam Panel"
panel=None
pane = None
paneinfo=None
parent=None
topcam=None
topcam_light=None
topcam_on =None
zoom_slider =None

def create(parent_frame):
    global parent,panel,pane,paneinfo,topcam,topcam_light,topcam_on,zoom_slider
    parent=parent_frame
    panel = wx.Panel(parent_frame, wx.ID_ANY, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
    paneinfo=wx.aui.AuiPaneInfo().Name(name).Caption("Top Camera").Left().PinButton(True).Dock().Resizable().FloatingSize( wx.Size( 170,180 ) ).MinSize(wx.Size(170,180))
    parent_frame.aui_mgr.AddPane(panel, paneinfo)
    grid = wx.GridBagSizer(0, 0)
    grid.SetFlexibleDirection( wx.BOTH )
    grid.SetEmptyCellSize( wx.Size( 1,1 ) )

    topcam_light = wx.BitmapToggleButton(panel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
    topcam_light.SetBitmap(       wx.ArtProvider.GetBitmap( "camlight-on",  wx.ART_OTHER, (32,32)))
    topcam_light.SetBitmapPressed(wx.ArtProvider.GetBitmap( "camlight-off", wx.ART_OTHER, (32,32)))
    topcam_light.Bind(wx.EVT_TOGGLEBUTTON, toplight_cmd)
    grid.Add(topcam_light, pos=(0, 2), flag=wx.ALL | wx.ALIGN_RIGHT, border=5)
    
    topcam_on = wx.BitmapToggleButton(panel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
    topcam_on.SetBitmap(       wx.ArtProvider.GetBitmap("cam-on",  wx.ART_OTHER, (32,32)))
    topcam_on.SetBitmapPressed(wx.ArtProvider.GetBitmap("cam-off", wx.ART_OTHER, (32,32)))
    topcam_on.Bind(wx.EVT_TOGGLEBUTTON, lambda e: topcam.cam_enable(topcam_on.GetValue()))
    grid.Add(topcam_on, pos=(0, 0),  flag=wx.ALL | wx.ALIGN_LEFT, border=5)
    
    zoom_slider = wx.Slider(panel, value=100, minValue=100, maxValue=1000, size=(50,-1), style=wx.SL_HORIZONTAL|wx.SL_VALUE_LABEL)
    zoom_slider.Bind(wx.EVT_SLIDER, lambda e: topcam.set_zoom(e.GetEventObject().GetValue() / 100.0))
    grid.Add(zoom_slider, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=0)
    
    topcam= src.gui.camera.Camera(panel,topcam_cv_id,zoom_slider)
    grid.Add(topcam, pos=(1,0), span=(1,3), flag=wx.EXPAND  |wx.ALL, border=0)
    grid.AddGrowableCol(1)
    grid.AddGrowableRow(1)
    panel.SetSizer(grid)
    panel.Layout()
    parent_frame.aui_mgr.Update()
    return panel

def toplight_cmd(event):
    src.engine.engine.send_command("gcode/script", 
        {"script": f"TOP_LIGHT S={1 if topcam_light.GetValue() else 0}"},src.gui.error.gcode_error_callback)

def add_to_menu(menu):
    item = menu.AppendCheckItem(ID, "Topcam Panel")
    item.Check(True)
    menu.Bind(wx.EVT_MENU, on_toggle, id=ID)
    return item

def on_toggle(event):
    parent.aui_mgr.GetPane(name).Show(event.IsChecked())
    parent.aui_mgr.Update()