import wx
import wx.lib.plot
import src.engine
import logging
logger = logging.getLogger(__name__)
ID = wx.NewIdRef()
name="graph_mcu"
panel = None
pane = None
paneinfo=None
parent=None

data_sysload=[]
data_memavail=[]
canvas= [None,None]
graphics=[None,None]
line=[None,None]

data_start=None

def create(parent):
    global canvas,graphics,line
    logger.info("create graph: %s"% parent)
    panel = wx.CollapsiblePane(parent, wx.ID_ANY,"system stats (stub)",style=wx.CP_NO_TLW_RESIZE )
    panel.Collapse( False )
    sizer = wx.BoxSizer(wx.VERTICAL)
    canvas[0] = wx.lib.plot.PlotCanvas(panel.GetPane(), size=(-1,150))
    canvas[1] = wx.lib.plot.PlotCanvas(panel.GetPane(), size=(-1,150))
    for c in canvas:
        c.axesPen = wx.Pen(wx.BLUE, 1, wx.PENSTYLE_LONG_DASH)
        c.enableLegend=False
        c.enableGrid = True
        c.SetFont(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        c.SetFontSizeAxis(10)
        c.SetFontSizeLegend(10)
        # canvas.Draw(graphics)
        sizer.Add(c, 1, wx.ALL | wx.EXPAND, 5)
    panel.GetPane().SetSizer(sizer)
    panel.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, lambda e: parent.Layout())
    return panel

def update(response):
    global canvas,graphics,line,data_start
    if not ('status' in response and
            'system_stats' in response['status']): return
    if data_start is None: data_start=response['eventtime']
    xval=int(response['eventtime']-data_start)
    if "sysload" in response['status']['system_stats']:
        if len(data_sysload)>100: data_sysload.pop(0)
        data_sysload.append((xval,response['status']['system_stats']['sysload']))
        line[0] = wx.lib.plot.PolyLine(data_sysload, legend="sysload",colour='red', width=1)
        graphics[0] = wx.lib.plot.PlotGraphics([line[0]], 'SysLoad', "", 'SysLoad')
        canvas[0].Draw(graphics[0],(0 if xval<100 else xval-100,xval))
    if "memavail" in response['status']['system_stats']:
        if len(data_memavail)>100: data_memavail.pop(0)
        data_memavail.append((xval,response['status']['system_stats']['memavail']/1000000.0))
        line[1] = wx.lib.plot.PolyLine(data_memavail, legend="memavail",colour='green', width=3)
        graphics[1] = wx.lib.plot.PlotGraphics([line[1]], 'Mem Avail (megs)', "", 'memavail')
        canvas[1].Draw(graphics[1],(0 if xval<100 else xval-100,xval))


