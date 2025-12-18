import wx
import cv2
import numpy
import src.gui.autocomplete
import src.gui.panel.topcam
import src.kicad
import logging
logger = logging.getLogger("src.engine")

ID = wx.NewIdRef()
name="Pattern Matching"
panel = None
parent=None
btn=None
btn2=None
footp=None
autocomplete=None
heatmap=None
footprints={}
datapoints=[]
fiducials =[]

def create(parent:wx.ScrolledWindow):
    global name,panel,btn,btn2
    global footp,autocomplete,footprints
    panel = wx.CollapsiblePane(parent, wx.ID_ANY,"Pattern Matching",style=wx.CP_NO_TLW_RESIZE )
    panel.Collapse( False )
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(wx.StaticText(panel.GetPane(), label="footprint:"))
    footp = wx.TextCtrl(panel.GetPane(), value="")
    footprints=src.kicad.find_footprint_files("")
    autocomplete = src.gui.autocomplete.TextCtrlCompleter(footp, 
        items=footprints.keys(),
        match_func=lambda p,i: p.lower() in i.lower())
    sizer.Add(footp, 0, wx.ALL | wx.EXPAND, 5)
    btn = wx.Button(panel.GetPane(), label="pattern test")
    sizer.Add(btn, 0, wx.CENTER | wx.ALL, 5)
    btn2 = wx.Button(panel.GetPane(), label="Clear overlay")
    sizer.Add(btn2, 0, wx.CENTER | wx.ALL, 5)
    panel.GetPane().SetSizer(sizer)
    panel.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, lambda e: parent.Layout())
    btn.Bind(wx.EVT_BUTTON,pattern_test)
    btn2.Bind(wx.EVT_BUTTON,clear_overlay)
    return panel

def pattern_test(evt):
    name=footp.GetValue()
    (footprint,_)=src.kicad.load_footprint_data(footprints[name])
    frame=numpy.zeros((200, 200, 3), dtype=numpy.uint8)
    template=src.kicad.draw_overlay(frame,footprint,10,-45,100,100)
    cv2.imshow("footprint", frame)
    cv2.imshow("template", template)


def clear_overlay(evt):
    src.gui.panel.topcam.topcam.set_frameoverlay(None)
    src.gui.panel.topcam.topcam.canvas_overlays.remove(canvas_overlay)

def canvas_overlay(w,h,fx,fy,canvas_rgb):
    pass