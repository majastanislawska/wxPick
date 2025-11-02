import wx
import wx.lib.plot
import src.engine
import logging
logger = logging.getLogger(__name__)
ID = wx.NewIdRef()
name="graph_temp"
panel = None
pane = None
paneinfo=None
parent=None

colors=['red','green','blue']
data={}
canvas= None
graphics=None
line_color={}
line={}
data_start=None

def create(parent):
    global canvas,graphics,line
    logger.info("create graph: %s"% parent)
    panel = wx.CollapsiblePane(parent, wx.ID_ANY,"Temperature",style=wx.CP_NO_TLW_RESIZE )
    panel.Collapse( False )
    sizer = wx.BoxSizer(wx.VERTICAL)
    canvas = wx.lib.plot.PlotCanvas(panel.GetPane(), size=(-1,250))
    canvas.axesPen = wx.Pen(wx.BLUE, 1, wx.PENSTYLE_LONG_DASH)
    canvas.enableLegend=True
    canvas.enableGrid = True
    canvas.SetFont(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    canvas.SetFontSizeAxis(10)
    canvas.SetFontSizeLegend(10)
    sizer.Add(canvas, 1, wx.ALL | wx.EXPAND, 5)
    panel.GetPane().SetSizer(sizer)
    panel.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, lambda e: parent.Layout())
    return panel

def update(response):
    global canvas,graphics,line,data, line_color,data_start
    if not 'status' in response: return
    if data_start is None: data_start=response['eventtime']
    xval=int(response['eventtime']-data_start)
    sensors=[x for x in response['status'].keys() if x.startswith("temperature_sensor")]
    color=0
    for sensor in sensors:  
        if not sensor in data.keys():
            data[sensor]=[]
            line_color[sensor]=colors.pop()
        if len(data[sensor])>250: data[sensor].pop(0)
        data[sensor].append((xval,response['status'][sensor]['temperature']))
        line[sensor] =wx.lib.plot.PolyLine(data[sensor], legend=sensor.split()[1],colour=line_color[sensor], width=1)
        color+=1
    graphics = wx.lib.plot.PlotGraphics(list(line.values()), "Temperature", "", 'temperature')
    canvas.Draw(graphics,(0 if xval<100 else xval-100,xval))
