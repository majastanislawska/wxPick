import wx
import src.engine
import logging
logger = logging.getLogger(__name__)
DISTANCES = [0.1, 1.0, 10, 50, 100]
ANGLES = [0.1, 1.0, 10, 45, 90]
SPEEDS = [100, 50, 25, 10, 5]

ID = wx.NewIdRef()
name="Jog Panel"
toolbar = None
pane = None
paneinfo=None
parent=None

btn_NW = None
btn_N = None
btn_NE = None
btn_E = None
btn_SE = None
btn_S = None
btn_SW = None
btn_W =None
#btn_home_xy = None
btn_z_plus = None
btn_z_minus = None
btn_z_zero = None
btn_a_ccw = None
btn_a_zero = None
btn_a_cw = None
btn_b_ccw = None
btn_b_zero = None
btn_b_cw = None
distance_radio = None
speed_radio = None

def create(parent_frame):
    global name,panel, pane, paneinfo, parent
    global btn_NW, btn_N, btn_NE, btn_E, btn_SE, btn_S, btn_SW, btn_W
    global btn_z_plus, btn_z_minus, btn_z_zero
    global btn_a_ccw, btn_a_zero, btn_a_cw, btn_b_ccw, btn_b_zero, btn_b_cw
    global distance_radio, speed_radio
    parent = parent_frame
    panel = wx.Panel(parent, wx.ID_ANY)
    grid = wx.GridBagSizer(0, 0)
    grid.SetFlexibleDirection( wx.BOTH )
    grid.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
    grid.SetEmptyCellSize( wx.Size(50,-1 ) )
    btn_size = (44, 34) ; border=3 # 50x40
    art_size=(24,24)
    btn_NW = wx.BitmapButton(panel, size=btn_size)
    btn_N  = wx.BitmapButton(panel, size=btn_size)
    btn_NE = wx.BitmapButton(panel, size=btn_size)
    btn_E  = wx.BitmapButton(panel, size=btn_size)
    btn_SE = wx.BitmapButton(panel, size=btn_size) 
    btn_S  = wx.BitmapButton(panel, size=btn_size) 
    btn_SW = wx.BitmapButton(panel, size=btn_size) 
    btn_W  = wx.BitmapButton(panel, size=btn_size)
    btn_NW.SetToolTip("X- Y+")
    btn_N.SetToolTip(    "Y+")
    btn_NE.SetToolTip("X+ Y+")
    btn_E.SetToolTip( "X+")
    btn_SE.SetToolTip("X+ Y-")
    btn_S.SetToolTip(    "Y-")
    btn_SW.SetToolTip("X- Y-")
    btn_W.SetToolTip( "X-")
    btn_NW.SetBitmapLabel( wx.ArtProvider.GetBitmap( "jog-NW", wx.ART_OTHER, art_size))
    btn_N.SetBitmapLabel(  wx.ArtProvider.GetBitmap( "jog-N",  wx.ART_OTHER, art_size))
    btn_NE.SetBitmapLabel( wx.ArtProvider.GetBitmap( "jog-NE", wx.ART_OTHER, art_size))
    btn_E.SetBitmapLabel(  wx.ArtProvider.GetBitmap( "jog-E",  wx.ART_OTHER, art_size))
    btn_SE.SetBitmapLabel( wx.ArtProvider.GetBitmap( "jog-SE", wx.ART_OTHER, art_size))
    btn_S.SetBitmapLabel(  wx.ArtProvider.GetBitmap( "jog-S",  wx.ART_OTHER, art_size))
    btn_SW.SetBitmapLabel( wx.ArtProvider.GetBitmap( "jog-SW", wx.ART_OTHER, art_size))
    btn_W.SetBitmapLabel(  wx.ArtProvider.GetBitmap( "jog-W",  wx.ART_OTHER, art_size))
    grid.Add(btn_NW, pos=(0,0), flag=wx.ALL,border=border)
    grid.Add(btn_N, pos=(0,1),  flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(btn_NE, pos=(0,2), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(btn_E, pos=(1,2),  flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(btn_SE, pos=(2,2), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(btn_S, pos=(2,1),  flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(btn_SW, pos=(2,0), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(btn_W, pos=(1,0),  flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    # btn_home_xy = wx.BitmapButton(panel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
    # btn_home_xy.SetBitmap( wx.ArtProvider.GetBitmap( wx.ART_GO_HOME, wx.ART_TOOLBAR ) )
    # grid.Add(btn_home_xy, pos=(1,1), flag=wx.ALL |wx.ALIGN_CENTER,border=5)

    btn_z_plus =  wx.BitmapButton(panel, size=btn_size)
    btn_z_zero =  wx.BitmapButton(panel, size=btn_size)
    btn_z_minus = wx.BitmapButton(panel, size=btn_size)
    btn_z_plus.SetBitmapLabel( wx.ArtProvider.GetBitmap( "jog-Z+", wx.ART_OTHER,art_size ) )
    btn_z_zero.SetBitmapLabel( wx.ArtProvider.GetBitmap( "jog-Z0", wx.ART_OTHER,art_size ) )
    btn_z_minus.SetBitmapLabel( wx.ArtProvider.GetBitmap( "jog-Z-", wx.ART_OTHER,art_size ) )
    btn_z_plus.SetToolTip( "Z+")
    btn_z_zero.SetToolTip( "Z=0")
    btn_z_minus.SetToolTip( "Z-")
    grid.Add(btn_z_plus,  pos=(0,3), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(btn_z_zero,  pos=(1,3), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(btn_z_minus, pos=(2,3), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    
    distance_radio = wx.RadioBox(panel, label="Dist",  choices=[f"{d}" for d in DISTANCES], size=(50,-1),majorDimension=1, style=wx.RA_SPECIFY_COLS|wx.RA_HORIZONTAL)
    speed_radio =    wx.RadioBox(panel, label="Speed", choices=[f"{s}" for s in SPEEDS],    size=(50,-1),majorDimension=1, style=wx.RA_SPECIFY_COLS|wx.RA_HORIZONTAL)
    #distance_radio.SetFont(wx.Font(6, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    #speed_radio.SetFont(wx.Font(8, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    distance_radio.SetSelection(1)
    speed_radio.SetSelection(0)
    distance_radio.SetToolTip("For rotary distances are 45 and 90 intead of 50 and 100")
    grid.Add(distance_radio, pos=(0,4), span=(3,1), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
    grid.Add(speed_radio,    pos=(0,5), span=(3,1), flag=wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL)
    grid.Add(wx.StaticText(panel, label="A:", size=(btn_size[0]*3,-1)), pos=(3,0), span=(1,3),flag=wx.EXPAND, border=0)
    grid.Add(wx.StaticText(panel, label="B:", size=(btn_size[0]*3,-1)), pos=(3,3),span=(1,3), flag=wx.EXPAND, border=0)

    btn_a_cw   = wx.BitmapButton(panel, size=btn_size)
    btn_a_zero = wx.BitmapButton(panel, size=btn_size)
    btn_a_ccw  = wx.BitmapButton(panel, size=btn_size)
    btn_a_ccw.SetBitmapLabel(  wx.ArtProvider.GetBitmap( "arrow-ccw", wx.ART_OTHER,(20,20))) #make them bit smaller
    btn_a_zero.SetBitmapLabel( wx.ArtProvider.GetBitmap( "number-square-zero", wx.ART_OTHER,art_size ))
    btn_a_cw.SetBitmapLabel(   wx.ArtProvider.GetBitmap( "arrow-cw", wx.ART_OTHER,(20,20)))
    grid.Add( btn_a_ccw, pos=(4,0), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(btn_a_zero, pos=(4,1), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(  btn_a_cw, pos=(4,2), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)

    btn_b_ccw =  wx.BitmapButton(panel, size=btn_size)
    btn_b_zero = wx.BitmapButton(panel, size=btn_size)
    btn_b_cw =   wx.BitmapButton(panel, size=btn_size)
    btn_b_ccw.SetBitmapLabel(  wx.ArtProvider.GetBitmap( "arrow-ccw", wx.ART_OTHER,(20,20) ) )
    btn_b_zero.SetBitmapLabel( wx.ArtProvider.GetBitmap( "number-square-zero", wx.ART_OTHER,art_size ) )
    btn_b_cw.SetBitmapLabel(   wx.ArtProvider.GetBitmap( "arrow-cw", wx.ART_OTHER,(20,20) ) )
    grid.Add( btn_b_ccw, pos=(4,3), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(btn_b_zero, pos=(4,4), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    grid.Add(  btn_b_cw, pos=(4,5), flag=wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,border=border)
    
    # grid.Add(wx.Button(panel, label="placeholder", size=( -1,-1 ),style=wx.BORDER_SIMPLE), pos=(0,6), span=(5,1), flag=wx.EXPAND | wx.ALL)
    # grid.Add(wx.Button(panel, label="placeholder", size=( 300,-1 ),style=wx.BORDER_SIMPLE), pos=(5,0), span=(1,6), flag=wx.EXPAND | wx.ALL)
    # grid.AddGrowableCol(6)
    
    bind_buttons()
    panel.SetSizer(grid)
    paneinfo= (wx.aui.AuiPaneInfo().Name(name).
        Left().Caption("Jog Panel").
        MaximizeButton(True).MinimizeButton(True).PinButton(True).
        BestSize( wx.Size( 300,180 ) ).
        MinSize( wx.Size( 300,180 ) ).
        # MaxSize( wx.Size( 500,500 ) ).
        Dock().DockFixed(False) )
    parent.aui_mgr.AddPane( panel,paneinfo)
    return panel

def bind_buttons():
    btn_NW.Bind(wx.EVT_BUTTON, lambda e: jog_axis("X- Y+", get_distance()))
    btn_N.Bind( wx.EVT_BUTTON, lambda e: jog_axis("Y+",    get_distance()))
    btn_NE.Bind(wx.EVT_BUTTON, lambda e: jog_axis("X+ Y+", get_distance()))
    btn_E.Bind( wx.EVT_BUTTON, lambda e: jog_axis("X+",    get_distance()))
    btn_SE.Bind(wx.EVT_BUTTON, lambda e: jog_axis("X+ Y-", get_distance()))
    btn_S.Bind( wx.EVT_BUTTON, lambda e: jog_axis("Y-",    get_distance()))
    btn_SW.Bind(wx.EVT_BUTTON, lambda e: jog_axis("X- Y-", get_distance()))
    btn_W.Bind( wx.EVT_BUTTON, lambda e: jog_axis("X-",    get_distance()))
    
    #btn_home_xy.Bind(wx.EVT_BUTTON, lambda e: send_gcode("G28 X Y"))
    
    btn_z_plus.Bind(wx.EVT_BUTTON, lambda e: jog_axis("Z", get_distance()))
    btn_z_zero.Bind(wx.EVT_BUTTON, lambda e: goto("Z",0.0))
    btn_z_minus.Bind(wx.EVT_BUTTON, lambda e: jog_axis("Z", -get_distance()))
    
    btn_a_ccw.Bind(wx.EVT_BUTTON, lambda e: jog_axis("A", -get_angle()))
    btn_a_cw.Bind(wx.EVT_BUTTON, lambda e: jog_axis("A", get_angle()))
    btn_a_zero.Bind(wx.EVT_BUTTON, lambda e: goto("A",0.0))
    
    btn_b_ccw.Bind(wx.EVT_BUTTON, lambda e: jog_axis("B", -get_angle()))
    btn_b_cw.Bind(wx.EVT_BUTTON, lambda e: jog_axis("B", get_angle()))
    btn_b_zero.Bind(wx.EVT_BUTTON, lambda e: goto("B",0.0))

def get_distance():
    return DISTANCES[distance_radio.GetSelection()]
def get_angle():
    return ANGLES[distance_radio.GetSelection()]
def get_speed():
    return SPEEDS[speed_radio.GetSelection()]

def jog_callback(data):
    #todo: pop dialog on error
    logging.info("jog_callback %s"%data)

def goto(axis, position):
    speed = get_speed()
    command = f"G90\nG1 {axis}{position:.3f} F{speed * 60}"
    src.engine.engine.queue.put(("response", {"sub":"gcode","params":{"jog":'goto',"command":command}}, None))
    src.engine.engine.send_command("gcode/script", {"script": command})

def jog_axis(axes, distance):
    speed = get_speed()
    cmd=" ".join([f"{axis}{distance:.3f}" for axis in axes.split(" ")])
    command = f"G91\nG1 {cmd} F{speed * 60}"
    logging.info("jog_axis %s"%command)
    src.engine.engine.queue.put(("response", {"sub":"gcode","params":{"jog":'jog',"command":command}}, None))
    src.engine.engine.send_command("gcode/script", {"script": command},jog_callback)

def send_gcode(command):
    src.engine.engine.queue.put(("response", {"sub":"gcode","params":{"jog":'command',"command":command}}, None))
    src.engine.engine.send_command("gcode/script", {"script": command})

def add_to_menu(menu):
    item = menu.AppendCheckItem(ID, "Jog Panel")
    item.Check(True)
    menu.Bind(wx.EVT_MENU, on_toggle, id=ID)
    return item

def on_toggle(event):
    parent.aui_mgr.GetPane(name).Show(event.IsChecked())
    parent.aui_mgr.Update()
