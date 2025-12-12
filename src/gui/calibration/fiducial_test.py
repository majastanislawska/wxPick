import wx
import cv2
import numpy
import src.gui.panel.topcam
import src.vision.hough_fiducial
import src.vision.pattern_match
import collections
import logging
logger = logging.getLogger("src.engine") 

ID = wx.NewIdRef()
name="Focus"
panel = None
parent=None
btn=None
minr=None
maxr=None
hough=None
heatmap=None
datapoints=[]
fiducials =[]

def create(parent:wx.ScrolledWindow):
    global name,panel,btn,minr,maxr,hough
    panel = wx.CollapsiblePane(parent, wx.ID_ANY,"Fiducials",style=wx.CP_NO_TLW_RESIZE )
    panel.Collapse( False )
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(wx.StaticText(panel.GetPane(), label="min r:"))
    minr = wx.SpinCtrl(panel.GetPane(), value="40",style=wx.TE_PROCESS_ENTER)
    sizer.Add(minr, 0, wx.ALL | wx.EXPAND, 5)
    sizer.Add(wx.StaticText(panel.GetPane(), label="max r:"))
    maxr = wx.SpinCtrl(panel.GetPane(), value="60", style=wx.TE_PROCESS_ENTER)
    sizer.Add(maxr, 0, wx.ALL | wx.EXPAND, 5)
    sizer.Add(wx.StaticText(panel.GetPane(), label="Hough param2:"))
    hough = wx.SpinCtrl(panel.GetPane(), value="30", style=wx.TE_PROCESS_ENTER)
    sizer.Add(hough, 0, wx.ALL | wx.EXPAND, 5)
    btn = wx.Button(panel.GetPane(), label="find fiducials")
    sizer.Add(btn, 0, wx.CENTER | wx.ALL, 5)
    btn2 = wx.Button(panel.GetPane(), label="Clear overlay")
    sizer.Add(btn2, 0, wx.CENTER | wx.ALL, 5)
    panel.GetPane().SetSizer(sizer)
    panel.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, lambda e: parent.Layout())
    btn.Bind(wx.EVT_BUTTON,do_find_fiducials)
    btn2.Bind(wx.EVT_BUTTON,clear_overlay)
    return panel

def clear_overlay(evt):
    src.gui.panel.topcam.topcam.set_frameoverlay(None)
    src.gui.panel.topcam.topcam.canvas_overlays.remove(canvas_overlay)

def canvas_overlay(w,h,canvas_rgb):
    global fiducials
    for (x, y, r) in fiducials:
        cv2.circle(canvas_rgb, (int(x), int(y)), int(r), (0, 255, 255), 2)
        cv2.circle(canvas_rgb, (int(x), int(y)), 3, (0, 0, 255), -1)
        cv2.putText(canvas_rgb, f"{r:.1f}", (int(x)+10, int(y)-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

def do_find_fiducials(evt):
    global fiducials,minr,maxr,hough
    global datapoints
    cam=src.gui.panel.topcam.topcam
    min_r=int(minr.GetValue())
    max_r=int(maxr.GetValue())
    hough2=int(hough.GetValue())
    if not cam.is_enabled:
        src.gui.panel.topcam.cam_enable(True) #make pressbtn click
    cam.canvas_overlays.append(canvas_overlay)
    while True:
        circles=src.vision.hough_fiducial.hough_fiducials(cam,min_r,max_r,hough2)
        logger.info(f"detect_fiducials: {circles}")
        if circles is None or circles.size <3:  hough2-=5; continue
        # if circles.size >300:                    hough2+=5; continue
        break
