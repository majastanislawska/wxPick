import wx
import src.engine
import src.camera
import src.gui.error
import wx.propgrid
import logging
logger = logging.getLogger(__name__)
#config
topcam_cam_uuid='USB Camera (Generic) 0x141340000bda3036'
topcam_fmt_id=11
topcam_framerate=30
openenpnp_config_path="~.openpnp2/machine.xml"
openpnp_camera_name="TopCam"
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
    
    topcam= src.camera.Camera(panel,topcam_cam_uuid,topcam_fmt_id,zoom_slider)
    topcam.load_calib_from_openpnp(openenpnp_config_path, openpnp_camera_name)
    grid.Add(topcam, pos=(1,0), span=(1,3), flag=wx.EXPAND  |wx.ALL, border=0)
    grid.AddGrowableCol(1)
    grid.AddGrowableRow(1)
    panel.SetSizer(grid)
    panel.Layout()
    parent_frame.aui_mgr.Update()
    return panel

def cam_enable(enable):
    topcam_on.SetValue(enable)
    if enable: topcam.cam_start()
    else: topcam.cam_stop()

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
class SingleChoiceDialogAdapter(wx.propgrid.PGEditorDialogAdapter):
    def __init__(self, choices):
        wx.propgrid.PGEditorDialogAdapter.__init__(self)
        self.choices = choices
    def DoShowDialog(self, propGrid, property):
        s = wx.GetSingleChoice("Select Camera", "Cammera Selection", self.choices)
        if s:
            self.SetValue(s)
            return True
        return False
class SelectCameraProp(wx.propgrid.StringProperty):
    def __init__(self, label, name=wx.propgrid.PG_LABEL, value=''):
        wx.propgrid.StringProperty.__init__(self, label, name, value)
    def DoGetEditorClass(self):
        return wx.propgrid.PropertyGridInterface.GetEditorByName("TextCtrlAndButton")
    def GetEditorDialog(self):
        choices=src.camera.get_devices(topcam.ctx)
        return SingleChoiceDialogAdapter(choices)

def topcam_pg_callback(p:wx.propgrid.PGProperty):
    global topcam_cam_uuid, topcam_fmt_id, topcam
    label=p.GetLabel()
    name=p.GetName()
    val=p.GetValue()
    dispstr = p.GetDisplayedString()
    logger.warning("topcam_pg_callback. %s %s %s"%(name,label,val))
    match name:
        case "topcam_cam_id":
            topcam_cam_uuid = val
            pg=p.GetGrid()
            topcam.set_cam(val)
            running=topcam.is_enabled
            #we got to start stream in order to get prop values
            if not running: topcam.cam_start()
            prop=pg.GetProperty("topcam_fmt_id")
            choices = wx.propgrid.PGChoices()
            for  value,label in topcam.get_formats().items():
                choices.Add(label, wx.NullBitmap, value)
            prop.SetChoices(choices)
            for key,val in src.camera.props.items():
                logging.info(f"regenerating fr new cam {key} {val}")
                update_prop(pg,topcam,key,val)
            if not running: topcam.cam_stop()
        case "topcam_fmt_id":
            topcam_fmt_id=val
            logging.info(f"topcam_fmt_id {val}")
            topcam.set_fmt(val)
        case "topcam_autoexp":    topcam.set_autoproperty(src.camera.props['exp'][0],p.GetValue())
        case "topcam_exp":        topcam.set_property(    src.camera.props['exp'][0],p.GetValue())
        case "topcam_autofocus":  topcam.set_autoproperty(src.camera.props['focus'][0],p.GetValue())
        case "topcam_focus":      topcam.set_property(    src.camera.props['focus'][0],p.GetValue())
        case "topcam_autozoom":   topcam.set_autoproperty(src.camera.props['zoom'][0],p.GetValue())
        case "topcam_zoom":       topcam.set_property(    src.camera.props['zoom'][0],p.GetValue())
        case "topcam_autowb":     topcam.set_autoproperty(src.camera.props['wb'][0],p.GetValue())
        case "topcam_wb":         topcam.set_property(    src.camera.props['wb'][0],p.GetValue())
        case "topcam_autogain":   topcam.set_autoproperty(src.camera.props['gain'][0],p.GetValue())
        case "topcam_gain":       topcam.set_property(    src.camera.props['gain'][0],p.GetValue())
        case "topcam_autobright": topcam.set_autoproperty(src.camera.props['bright'][0],p.GetValue())
        case "topcam_bright":     topcam.set_property(    src.camera.props['bright'][0],p.GetValue())
        case "topcam_autocontr":  topcam.set_autoproperty(src.camera.props['contr'][0],p.GetValue())
        case "topcam_contr":      topcam.set_property(    src.camera.props['contr'][0],p.GetValue())
        case "topcam_autosat":    topcam.set_autoproperty(src.camera.props['sat'][0],p.GetValue())
        case "topcam_sat":        topcam.set_property(    src.camera.props['sat'][0],p.GetValue())
        case "topcam_autogamma":  topcam.set_autoproperty(src.camera.props['gamma'][0],p.GetValue())
        case "topcam_gamma":      topcam.set_property(    src.camera.props['gamma'][0],p.GetValue())
        case "topcam_autohue":    topcam.set_autoproperty(src.camera.props['hue'][0],p.GetValue())
        case "topcam_hue":        topcam.set_property(    src.camera.props['hue'][0],p.GetValue())
        case "topcam_autosharp":  topcam.set_autoproperty(src.camera.props['sharp'][0],p.GetValue())
        case "topcam_sharp":      topcam.set_property(    src.camera.props['sharp'][0],p.GetValue())
        case "topcam_autobl":     topcam.set_autoproperty(src.camera.props['bl'][0],p.GetValue())
        case "topcam_bl":         topcam.set_property(    src.camera.props['bl'][0],p.GetValue())
        case "topcam_autopwr":    topcam.set_autoproperty(src.camera.props['pwrfq'][0],p.GetValue())
        case "topcam_pwr":        topcam.set_property(    src.camera.props['pwrfq'][0],p.GetValue())

def add_prop(pg,callback,key,val):
    (prop_id,)=val
    #name, label. label is id
    prop=wx.propgrid.BoolProperty(f"topcam auto{key}", f"topcam_auto{key}")
    prop.SetAttribute("UseCheckbox", True)
    prop.SetClientData(callback)
    prop.Enable(False)
    pg.Append(prop)
    prop=wx.propgrid.IntProperty(f"topcam {key}", f"topcam_{key}")
    prop.SetEditor("SpinCtrl")
    prop.SetClientData(callback)
    prop.Enable(False)
    pg.Append(prop)

def update_prop(pg:wx.propgrid.PropertyGridManager,cam,key,val):
    (prop_id,)=val
    label=f"topcam_{key}"
    autolabel=f"topcam_auto{key}"
    auto_v = cam.get_autoproperty(prop_id)
    if auto_v is None: pg.EnableProperty(autolabel, False)
    else:
        pg.EnableProperty(autolabel, True)
        pg.SetPropertyValue(autolabel,auto_v)
    cur_v = cam.get_property(prop_id)
    if cur_v is None: pg.EnableProperty(label, False)
    else:
        pg.EnableProperty(label, True)
        pg.SetPropertyValue(label,cur_v)
        min_v, max_v, def_v = cam.get_limits(prop_id)
        pg.SetPropertyHelpString(label,f"min:{min_v} def:{def_v} max:{max_v}")
        pg.SetPropertyAttribute(label,"Min", min_v)
        pg.SetPropertyAttribute(label,"Max", max_v)

def make_config(pg: wx.propgrid.PropertyGridManager):
    #we got to start stream in order to get prop values
    topcam.cam_start()
    pg.Append( wx.propgrid.PropertyCategory("Topcam Config") )
    prop=SelectCameraProp("topcam_cam_id", "topcam_cam_id", topcam_cam_uuid)
    prop.SetClientData(topcam_pg_callback)
    prop.SetEditor("SingleChoiceDialogAdapter")
    pg.Append(prop)
    prop=wx.propgrid.EnumProperty("Video Format","topcam_fmt_id",[],[],topcam_fmt_id)
    prop.SetClientData(topcam_pg_callback)
    choices = wx.propgrid.PGChoices()
    for  value,label in topcam.get_formats().items():
        choices.Add(label, wx.NullBitmap, value)
    prop.SetChoices(choices)
    prop.SetValue(topcam_fmt_id)
    pg.Append(prop)
    # fmt_prop = SelectFormatProp("Video Format","topcam_fmt_id", str(topcam_fmt_id))
    # fmt_prop.SetClientData(topcam_pg_callback)
    # pg.Append(fmt_prop)
    for key,val in src.camera.props.items():
        logging.info(f"generating {key} {val}")
        add_prop(pg,topcam_pg_callback,key,val)
        update_prop(pg,topcam,key,val)

    pg.Append( wx.propgrid.FloatProperty("topcam_Float",value=100.0) )
    pg.Append( wx.propgrid.BoolProperty("topcam_Bool",value=True) )
    topcam.cam_stop()