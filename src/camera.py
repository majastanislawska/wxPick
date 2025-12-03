import wx
import cv2,numpy
import logging
import ctypes
import os
logger = logging.getLogger(__name__)

LIB_PATHS = ["./libopenpnp-capture.dylib",]
lib = None
for path in LIB_PATHS:
    if os.path.exists(path):
        lib = ctypes.CDLL(path)
        break
if lib is None:
    raise FileNotFoundError("libopenpnp-capture.dylib not found. Install OpenPnP or copy the dylib.")
class CapFormatInfo(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_uint32), #///< width in pixels
        ("height", ctypes.c_uint32), #///< height in pixels
        ("fourcc", ctypes.c_uint32),#///< fourcc code (platform dependent)
        ("fps",    ctypes.c_uint32), #  ///< frames per second
        ("bpp",    ctypes.c_uint32)#   ///< bits per pixel
    ]
# DLLPUBLIC CapContext Cap_createContext(void);
lib.Cap_createContext.restype = ctypes.c_void_p

# DLLPUBLIC CapResult Cap_releaseContext(CapContext ctx);
lib.Cap_releaseContext.argtypes = [ctypes.c_void_p]
lib.Cap_releaseContext.restype = ctypes.c_uint32

# DLLPUBLIC uint32_t Cap_getDeviceCount(CapContext ctx);
lib.Cap_getDeviceCount.argtypes = [ctypes.c_void_p]
lib.Cap_getDeviceCount.restype = ctypes.c_uint32

# DLLPUBLIC const char* Cap_getDeviceName(CapContext ctx, CapDeviceID index);
lib.Cap_getDeviceName.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
lib.Cap_getDeviceName.restype = ctypes.c_char_p

# DLLPUBLIC const char* Cap_getDeviceUniqueID(CapContext ctx, CapDeviceID index);
lib.Cap_getDeviceUniqueID.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
lib.Cap_getDeviceUniqueID.restype = ctypes.c_char_p

# DLLPUBLIC int32_t Cap_getNumFormats(CapContext ctx, CapDeviceID index);
lib.Cap_getNumFormats.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
lib.Cap_getNumFormats.restype = ctypes.c_uint32

# DLLPUBLIC CapResult Cap_getFormatInfo(CapContext ctx, CapDeviceID index, CapFormatID id, CapFormatInfo *info);
lib.Cap_getFormatInfo.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
lib.Cap_getFormatInfo.restype = ctypes.c_uint32

# DLLPUBLIC CapStream Cap_openStream(CapContext ctx, CapDeviceID index, CapFormatID formatID);
lib.Cap_openStream.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32]
lib.Cap_openStream.restype = ctypes.c_uint32

# DLLPUBLIC CapResult Cap_closeStream(CapContext ctx, CapStream stream);
lib.Cap_closeStream.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
lib.Cap_closeStream.restype = ctypes.c_uint32

# DLLPUBLIC uint32_t Cap_isOpenStream(CapContext ctx, CapStream stream);
lib.Cap_isOpenStream.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
lib.Cap_isOpenStream.restype = ctypes.c_uint32

# DLLPUBLIC CapResult Cap_captureFrame(CapContext ctx, CapStream stream, void *RGBbufferPtr, uint32_t RGBbufferBytes);
lib.Cap_captureFrame.argtypes = [ctypes.c_void_p,ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32]
lib.Cap_captureFrame.restype = ctypes.c_uint32

# DLLPUBLIC uint32_t Cap_hasNewFrame(CapContext ctx, CapStream stream);
lib.Cap_hasNewFrame.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
lib.Cap_hasNewFrame.restype = ctypes.c_uint32

# DLLPUBLIC uint32_t Cap_getStreamFrameCount(CapContext ctx, CapStream stream);
lib.Cap_getStreamFrameCount.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
lib.Cap_getStreamFrameCount.restype = ctypes.c_uint32

# DLLPUBLIC CapResult Cap_getPropertyLimits(CapContext ctx, CapStream stream, CapPropertyID propID, int32_t *min, int32_t *max, int *dValue);
lib.Cap_getPropertyLimits.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int) ]
lib.Cap_getPropertyLimits.restype = ctypes.c_uint32

# DLLPUBLIC CapResult Cap_setProperty(CapContext ctx, CapStream stream, CapPropertyID propID, int32_t value);
lib.Cap_setProperty.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,ctypes.c_int32]
lib.Cap_setProperty.restype = ctypes.c_uint32

# DLLPUBLIC CapResult Cap_setAutoProperty(CapContext ctx, CapStream stream, CapPropertyID propID, uint32_t bOnOff);
lib.Cap_setAutoProperty.argtypes = [ctypes.c_void_p, ctypes.c_uint32,  ctypes.c_uint32,  ctypes.c_uint32]
lib.Cap_setAutoProperty.restype = ctypes.c_uint32

# DLLPUBLIC CapResult Cap_getProperty(CapContext ctx, CapStream stream, CapPropertyID propID, int32_t *outValue);
lib.Cap_getProperty.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int32)]
lib.Cap_getProperty.restype = ctypes.c_uint32

# DLLPUBLIC CapResult Cap_getAutoProperty(CapContext ctx, CapStream stream, CapPropertyID propID, uint32_t *outValue);
lib.Cap_getAutoProperty.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int32)]
lib.Cap_getAutoProperty.restype = ctypes.c_uint32

# DLLPUBLIC void Cap_setLogLevel(uint32_t level);
lib.Cap_setLogLevel.argtypes = [ctypes.c_uint32]

# DLLPUBLIC void Cap_installCustomLogFunction(CapCustomLogFunc logFunc);
# dont need that

# DLLPUBLIC const char* Cap_getLibraryVersion();
lib.Cap_getLibraryVersion.restype = ctypes.c_char_p
props={
    'exp'   :(1,),
    'focus' :(2,),
    'zoom'  :(3,),
    'wb'    :(4,),
    'gain'  :(5,),
    'bright':(6,),
    'contr' :(7,),
    'sat'   :(8,),
    'gamma' :(9,),
    'hue'   :(10,),
    'sharp' :(11,),
    'bl'    :(12,),
    'pwrfq' :(13,)
}


def get_devices(ctx):
    count = lib.Cap_getDeviceCount(ctx)
    choices = []
    for i in range(count):
        #name = lib.Cap_getDeviceName(ctx, i)
        uid = lib.Cap_getDeviceUniqueID(ctx, i)
        #name = name.decode('utf-8') if name else f"Camera {i}"
        uid_str = uid.decode('utf-8') if uid else f"Camera {i}"
        choices.append(uid_str)
    return choices

def find_camera_by_unique_id(ctx, target_uid: str) -> int:
    count = lib.Cap_getDeviceCount(ctx)
    for i in range(count):
        uid = lib.Cap_getDeviceUniqueID(ctx, i)
        logger.info(f"findcamera {target_uid} {uid}")
        if uid and uid.decode('utf-8') == target_uid:
            return i
    return 0

def fourcc_to_str(value: int) -> str:
    return ''.join(chr((value >> (i*8)) & 0xFF) for i in range(4))

def get_format_info(ctx, camera_id, fmt_id):
    fmt_info = CapFormatInfo()
    fmt_info_ptr = ctypes.pointer(fmt_info)
    success = lib.Cap_getFormatInfo(ctx, camera_id, ctypes.c_uint32(fmt_id), fmt_info_ptr)
    if success == 0 and fmt_info_ptr:
        fmt = fmt_info_ptr.contents
        return (fmt_id,fmt.width,fmt.height,fmt.fps,fourcc_to_str(fmt.fourcc))
    logger.info(f"returning none {ctx} {camera_id} {fmt_id}")
    return None
class Camera(wx.StaticBitmap):
    def __init__(self, parent, camera_uuid,fmt_id,zoom_slider):
        super().__init__(parent, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size(-1,-1), 0 )
        self.ctx = lib.Cap_createContext()
        self.camera_uuid=camera_uuid
        self.fmt_id=fmt_id
        self.zoom_slider=zoom_slider
        self.zoom_level = 1.0
        self.aspect_ratio = 4/3 #placeholder
        # self.processor_name = processor_name
        # self.processor = self.load_processor(processor_name)
        self.bitmap = wx.NullBitmap
        self.is_enabled = False
        #off-bitmap
        self.SetBitmap(wx.ArtProvider.GetBitmap("cam-off", wx.ART_OTHER,(48,48)))
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_scroll)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

    def cam_start(self):
        self.camera_id=find_camera_by_unique_id(self.ctx,self.camera_uuid)
        # if lib.Cap_getDeviceCount(self.ctx) <= self.camera_id:
        #     raise ValueError(f"Only {lib.Cap_getDeviceCount(self.ctx)} devices found")
        count = lib.Cap_getNumFormats(self.ctx, self.camera_id)
        if self.fmt_id>count: self.fmt_id=count-1
        (_,self.frame_w,self.frame_h,self.fps,_)=get_format_info(self.ctx,self.camera_id, self.fmt_id)
        self.stream = lib.Cap_openStream(self.ctx, self.camera_id, self.fmt_id)
        if  self.stream <0:
            raise RuntimeError("Failed to open camera with openpnp-capture")  
        self.is_enabled=True
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.timer.Start(int(1000/self.fps))

    def cam_stop(self):
        self.is_enabled=False
        self.timer.Stop()
        lib.Cap_closeStream(self.ctx,self.stream)
        # lib.Cap_releaseContext(self.ctx)
        self.Unbind(wx.EVT_PAINT)
        savedsize=self.GetSize()
        self.SetBitmap(wx.ArtProvider.GetBitmap("cam-off", wx.ART_OTHER,(48,48)))
        self.SetSize(savedsize)
        self.Refresh()

    def cam_enable(self, enable):
        if enable: self.cam_start()
        else: self.cam_stop()

    def set_cam(self,val):
        running=self.is_enabled
        logger.info("set_cam %s"%(val))
        if running: self.cam_stop()
        self.camera_uuid = val
        if running: self.cam_start()

    def set_fmt(self,val):
        running=self.is_enabled
        logger.info("set_fmt %s"%(val))
        if running: self.cam_stop()
        self.fmt_id = val
        if running: self.cam_start()

    def get_frame(self):
        # Grab raw BGR24 frame
        buffer_size = self.frame_h * self.frame_w * 3
        buffer = ctypes.create_string_buffer(buffer_size)
        result = lib.Cap_captureFrame(self.ctx, self.stream,
            buffer, ctypes.c_uint32(buffer_size))
        if result != 0:
            return None
        np_frame = numpy.frombuffer(buffer, dtype=numpy.uint8).reshape(
            (self.frame_h, self.frame_w, 3))
        return np_frame.copy()

    def on_timer(self, event):
        frame = self.get_frame()
        if frame is None:  return
        self.aspect_ratio = self.frame_w / self.frame_h
        # Process frame
        #frame = self.processor.process(frame)
        cw,ch = self.GetSize()
        self.width = int(min(cw, ch * self.aspect_ratio))
        self.height = int(min(ch, cw / self.aspect_ratio))
        if self.zoom_level>1:
            crop_w = int(self.frame_w / self.zoom_level)
            crop_h = int(self.frame_h / self.zoom_level)
            start_x = (self.frame_w - crop_w) // 2
            start_y = (self.frame_h - crop_h) // 2
            #logger.info("zooming %s,%s %s,%s"%(crop_w,crop_h, self.width,self.height))
            cropped_frame = frame[start_y:start_y + crop_h, start_x:start_x + crop_w]
            scaled_frame = cv2.resize(cropped_frame, (self.width,self.height), interpolation=cv2.INTER_AREA)
        else:
            #logger.info("no zoom %s,%s %s,%s"%(frame_w,frame_h, self.width,self.height))
            scaled_frame = cv2.resize(frame, (self.width,self.height), interpolation=cv2.INTER_AREA)
        x_offset = (cw - self.width) // 2
        y_offset = (ch - self.height) // 2
        canvas = numpy.zeros((ch, cw, 3), dtype=numpy.uint8)
        canvas[y_offset:y_offset + self.height, x_offset:x_offset + self.width] = scaled_frame
        canvas_rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        self.bitmap = wx.Bitmap.FromBuffer(cw, ch, canvas_rgb)
        self.Refresh()

    def get_formats(self):
        count = lib.Cap_getNumFormats(self.ctx, self.camera_id)
        logger.info(f"Device {self.camera_id} has {count} formats")
        out=[]
        for fmt_id in range(count):
            fmt=get_format_info(self.ctx, self.camera_id, fmt_id)
            (id,w,h,fps,cc)=fmt
            logger.info(f"Format {id}: {w}x{h}@{fps}fps {cc}")
            out.append(f"{id}: {w}x{h}@{fps}fps {cc}")
        return out

    def get_limits(self,prop_id):
        """Return (min, max, default) or (0, 255, 128) if not supported"""
        min_v = ctypes.c_int32()
        max_v = ctypes.c_int32()
        def_v = ctypes.c_int32()
        res = lib.Cap_getPropertyLimits(self.ctx, self.stream, prop_id,
                                        ctypes.byref(min_v), ctypes.byref(max_v), ctypes.byref(def_v))
        if res == 0:
            return min_v.value, max_v.value, def_v.value
        return 0, 255, 128
    def get_property(self,prop_id):
        val = ctypes.c_int32()
        if lib.Cap_getProperty(self.ctx, self.stream, prop_id, ctypes.byref(val)) == 0:
            return val.value 
        else: return None
    def get_autoproperty(self,prop_id):
        val = ctypes.c_int32()
        if lib.Cap_getAutoProperty(self.ctx, self.stream, prop_id, ctypes.byref(val)) == 0:
            return val !=0
        else: return None
    def set_property(self, prop_id,value):
        lib.Cap_setProperty(self.ctx, self.stream, prop_id, value)
        logger.info("set_property %s %s"%(prop_id,value))
    def set_autoproperty(self, prop_id,value):
        lib.Cap_setAutoProperty(self.ctx, self.stream, prop_id, value)
        logger.info("set_autoproperty %s %s"%(prop_id,value))

    def on_paint(self, event):
        wx.BufferedPaintDC(self, self.bitmap)

    # def load_processor(self, processor_name):
    #     try:
    #         module = importlib.import_module(f"src.processing.{processor_name}")
    #         importlib.reload(module)
    #         return module.Processor()
    #     except (ImportError, AttributeError) as e:
    #         print(f"Failed to load processor {processor_name}: {e}")
    #         from src.processing.base_processor import BaseProcessor
    #         return BaseProcessor()

    def on_scroll(self, event):
        delta = event.GetWheelRotation() / 1200  # Normalize to ~0.1 steps
        self.zoom_level = max(1.0, min(10.0, self.zoom_level + delta))  # Zoom > 1 only
        self.zoom_slider.SetValue(int(self.zoom_level * 100))
        self.Refresh()

    def set_zoom(self, value):
        self.zoom_level = max(1.0, min(10.0, value))
        self.Refresh()