import os
import wx
import wx.svg
import logging
logger = logging.getLogger(__name__)
artmap={"app-icon": "restart-emestop",
    "restart-emestop":"restart-emestop",
    "restart-firmware":"restart-firmware",
    "restart":"restart",
    "arrow-cw":"arrow-clockwise",
    "number-square-zero":"number-square-zero",
    "arrow-ccw": 'arrow-counter-clockwise',
    "cam-on": "video-camera",
    "cam-off":"video-camera-slash",
    "camlight-on": "lightning",
    "camlight-off": "lightning-slash",
    "state-ready":"thumbs-up",
    "state-error":"thumbs-down",
    "state-startup":"hand-waving",
    "state-shutdown":"hand-palm",
    "state-unknown":"question",
    "jog-N" :"arrow-square-up",
    "jog-NE":"arrow-square-up-right",
    "jog-E" :"arrow-square-right",
    "jog-SE":"arrow-square-down-right",
    "jog-S" :"arrow-square-down",
    "jog-SW":"arrow-square-down-left",
    "jog-W" :"arrow-square-left",
    "jog-NW":"arrow-square-up-left",
    "jog-Z+":"arrow-square-up",
    "jog-Z0":"number-square-zero",
    "jog-Z-":"arrow-square-down",
    "disconnected":"plugs",
    "connected":"plugs-connected"
}
class myArtProvider(wx.ArtProvider):
    def __init__(self):
        wx.ArtProvider.__init__(self)

    def CreateBitmap(self, artid, client, size):
        bmp = wx.NullBitmap
        logging.info("my art provider %s %s %s"%(artid, client, size))
        if artid in artmap.keys():
            bmp=self.create_scaled_bitmap(artid, size)
        return bmp
    def create_scaled_bitmap(self, name: str, size) -> wx.Bitmap:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fname=os.path.join(base_dir, f'{artmap[name]}.svg')
        return wx.svg.SVGimage.CreateFromFile(fname).ConvertToScaledBitmap(size)
