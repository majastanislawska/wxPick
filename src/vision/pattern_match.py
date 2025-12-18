import wx
import wx.propgrid
import src.kicad
import logging
logger = logging.getLogger("src.engine")

def make_config(pg: wx.propgrid.PropertyGridManager):
    pg.Append( wx.propgrid.PropertyCategory("Pattern Matching") )
    prop=pg.Append(wx.propgrid.DirProperty("kicad_dir",
                "Path to Kicad footprint dir",
                value=src.kicad.lib_dir))
    prop.SetClientData(pg_callback)

def pg_callback(p:wx.propgrid.PGProperty):
    global lib_dir
    label=p.GetLabel()
    name=p.GetName()
    val=p.GetValue()
    # dispstr = p.GetDisplayedString()
    logger.warning("pg_callback. %s %s %s"%(name,label,val))
    match name:
        case "kicad_dir": src.kicad.lib_dir=p.GetValue()
        case _: logger.error("Unknown property name %s"%(name,))
    return
