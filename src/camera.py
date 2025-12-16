import wx
import cv2,numpy
import logging
import ctypes
import os
import xml.etree.ElementTree as ET
logger = logging.getLogger(__name__)

def load_openpnp_capture():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # src/gui
    lib_dir = os.path.join(base_dir, "..", "lib")
    macapp_lib_dir = os.path.join(base_dir, "..","..","..", "lib")
    candidates = [
        # Built by Makefile
        os.path.join(lib_dir, "libopenpnp-capture.dylib"),
        os.path.join(macapp_lib_dir, "libopenpnp-capture.dylib"),
        os.path.join(lib_dir, "openpnp-capture.dll"),
        os.path.join(lib_dir, "libopenpnp-capture.so"),
        # Fallback: local dev path
        "./libopenpnp-capture.dylib",
        "./openpnp-capture.dll",
        "./libopenpnp-capture.so",
    ]
    for path in candidates:
        print(f"path: {path}")
        if os.path.exists(path):
            try:
                lib = ctypes.CDLL(path)
                print(f"Loaded openpnp-capture from: {path}")
                return lib
            except Exception as e:
                print(f"Failed to load {path}: {e}")
    raise FileNotFoundError("openpnp-capture library not found.")

lib = load_openpnp_capture()

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
        self.bitmap = wx.NullBitmap
        self.is_enabled = False
        self.frameoverlay=None
        self.canvas_overlays=[] #callback(w,h,canvas_rgb)
        # placeholders for OpenPnP advanced calibration 
        self.camera_matrix = None # will be set to default in cam_start if not loaded
        self.virtual_matrix = None  # will be set to camera_matrix if not loaded
        self.dist_coeffs = numpy.zeros(5)
        self.rectification_matrix = numpy.eye(3)      # identity rotation
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
        (_,self.cam_w,self.cam_h,self.fps,_)=get_format_info(self.ctx,self.camera_id, self.fmt_id)
        logger.info(f"Starting camera {self.camera_id} format {self.fmt_id} {self.cam_w}x{self.cam_h}@{self.fps}fps")
        if self.camera_matrix is None:
            self.camera_matrix = numpy.array([
                [self.cam_w, 0.0, self.cam_w / 2],
                [0.0, self.cam_w, self.cam_h / 2],
                [0.0, 0.0, 1.0]
            ])
        if self.virtual_matrix is None:
            self.virtual_matrix = self.camera_matrix.copy()
        self.map_x, self.map_y = cv2.initUndistortRectifyMap(
            self.camera_matrix,
            self.dist_coeffs,
            self.rectification_matrix, #R rotation/tilt
            self.virtual_matrix,
            (self.cam_w,self.cam_h),
            cv2.CV_32FC1
        )
        # optical center in undistorted but not cropped frame
        self.optical_cx = self.virtual_matrix[0, 2]
        self.optical_cy = self.virtual_matrix[1, 2]
        # this is for crop to square around optical center in undistort_frame
        crop_size = int(min(
            min(self.optical_cx, (self.cam_w - self.optical_cx)),
            min(self.optical_cy, (self.cam_h - self.optical_cy))
        ))
        self.crop_size = crop_size
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

    def undistort_frame(self, frame):
        frame = cv2.remap(frame, self.map_x, self.map_y, cv2.INTER_LINEAR)
        # Crop to square around optical center
        cx = self.virtual_matrix[0, 2]
        cy = self.virtual_matrix[1, 2]
        frame = frame[int(cy - self.crop_size) : int(cy + self.crop_size),
                      int(cx - self.crop_size) : int(cx + self.crop_size)]
        self.frame_h, self.frame_w = frame.shape[:2]
        self.optical_cx = self.frame_w//2
        self.optical_cy = self.frame_h//2
        return frame  # now square, no black, optical center at (crop_size/2, crop_size/2)
        # return cv2.remap(raw_bgr, self.map_x, self.map_y, cv2.INTER_LINEAR)

    def get_frame(self):
        # Grab raw BGR24 frame
        buffer_size = self.cam_h * self.cam_w * 3
        buffer = ctypes.create_string_buffer(buffer_size)
        result = lib.Cap_captureFrame(self.ctx, self.stream,
            buffer, ctypes.c_uint32(buffer_size))
        if result != 0:
            return None
        frame = numpy.frombuffer(buffer, dtype=numpy.uint8).reshape(
            (self.cam_h, self.cam_w, 3))
        return self.undistort_frame(frame)

    def on_timer(self, event):
        frame = self.get_frame()
        cw,ch = self.GetSize()
        scaled_frame=self.process_frame(cw,ch,frame)
        self.display_frame(cw,ch,scaled_frame)

    def set_frameoverlay(self, frameoverlay):
        self.frameoverlay=frameoverlay

    def process_frame(self,cw,ch,frame):
        if frame is None:  return None
        # keep this func rectangular frame compatible
        # so it still works when croping to square in undistort_frame is ditched
        self.aspect_ratio = self.frame_w / self.frame_h
        if self.frameoverlay is not None:
            frame=cv2.addWeighted(frame, 1, self.frameoverlay, 1, 0)
        self.width = int(min(cw, ch * self.aspect_ratio))
        self.height = int(min(ch, cw / self.aspect_ratio))
        if self.zoom_level==1:
            return cv2.resize(frame, (self.width,self.height), interpolation=cv2.INTER_AREA)
        # for zooming calculate crop region centered on optical_cx, cy
        crop_w = int(self.frame_w / self.zoom_level)
        crop_h = int(self.frame_h / self.zoom_level)
        x1 = int(self.optical_cx - crop_w / 2)
        y1 = int(self.optical_cy - crop_h / 2)
        x1 = max(0, min(x1, self.frame_w - crop_w))
        y1 = max(0, min(y1, self.frame_h - crop_h))
        cropped_frame = frame[y1:y1 + crop_h, x1:x1 + crop_w]
        # and scale it to fit
        return cv2.resize(cropped_frame, (self.width,self.height), interpolation=cv2.INTER_AREA)

    def display_frame(self,cw,ch,scaled_frame):
        if scaled_frame is None:  return None
        x_offset = (cw - self.width) // 2
        y_offset = (ch - self.height) // 2
        canvas = numpy.zeros((ch, cw, 3), dtype=numpy.uint8)
        canvas[y_offset:y_offset + self.height, x_offset:x_offset + self.width] = scaled_frame
        canvas_rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
        for callback in self.canvas_overlays:
            callback(cw,ch,canvas_rgb)
        self.bitmap = wx.Bitmap.FromBuffer(cw, ch, canvas_rgb)
        self.Refresh()

    def get_formats(self):
        count = lib.Cap_getNumFormats(self.ctx, self.camera_id)
        logger.info(f"Device {self.camera_id} has {count} formats")
        out={}
        for fmt_id in range(count):
            fmt=get_format_info(self.ctx, self.camera_id, fmt_id)
            (id,w,h,fps,cc)=fmt
            logger.info(f"Format {id}: {w}x{h}@{fps}fps {cc}")
            out[id]=f"{id}: {w}x{h}@{fps}fps {cc}"
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

    def on_scroll(self, event):
        delta = event.GetWheelRotation() / 1200  # Normalize to ~0.1 steps
        self.zoom_level = max(1.0, min(10.0, self.zoom_level + delta))  # Zoom > 1 only
        self.zoom_slider.SetValue(int(self.zoom_level * 100))
        self.Refresh()

    def set_zoom(self, value):
        self.zoom_level = max(1.0, min(10.0, value))
        self.Refresh()

    def load_calib_from_openpnp(self, xml_path, camera_name='TopCam'):
        calib = load_openpnp_config(xml_path, camera_name)
        self.camera_matrix = calib['camera_matrix']
        self.dist_coeffs = calib['dist_coeffs']
        self.rectification_matrix = calib['rectification_matrix']
        self.virtual_matrix = calib['virtual_matrix']
        logger.info(f"Loaded calibration for {camera_name} from {xml_path}")

def load_openpnp_config(config_path, camera_name):
    """
    Loads OpenPnP machine.xml, finds the camera by name, extracts advanced calibration parameters.
    Returns dict with camera_matrix, dist_coeffs, rectification_matrix, virtual_matrix.
    """
    xml_path = find_openpnp_machine_xml(config_path)
    if xml_path is None:
        print("load_openpnp_config: OpenPnP machine.xml not found.")
        return None
    print(f"Loading OpenPnP calibration from: {xml_path}")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    camera_elem = None
    for cam in root.findall(".//camera"):
        if cam.get('name') == camera_name:
            camera_elem = cam
            break
    if camera_elem is None:
        raise ValueError(f"Camera '{camera_name}' not found in {xml_path}")
    calib_elem = camera_elem.find('advanced-calibration')
    if calib_elem is None:
        raise ValueError("No advanced-calibration found for this camera")
    
    def parse_matrix(elem_name):
        elem = calib_elem.find(elem_name)
        if elem is None:
            return None
        length = int(elem.get('length'))
        values = [float(v) for v in elem.text.split(', ')]
        if len(values) != length:
            raise ValueError(f"Invalid length for {elem_name}")
        return numpy.array(values).reshape(3, 3) if length == 9 else numpy.array(values)
    config = {
        'camera_matrix': parse_matrix('camera-matrix'),
        'dist_coeffs': parse_matrix('distortion-coefficients'),
        'rectification_matrix': parse_matrix('rectification-matrix'),
        'virtual_matrix': parse_matrix('virtual-camera-matrix'),
    }
    return config

def find_openpnp_machine_xml(explicit_path=None):
    """
    Find OpenPnP machine.xml, trying common locations.
    Returns Path object or None.
    """
    if explicit_path:
        path=os.path.expanduser(explicit_path)
        if os.path.isfile(path):
            return path
    home = os.path.expanduser('~')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = os.getcwd()
    candidates = [
        os.path.join(home,".openpnp2","machine.xml"),
        os.path.join(home,".openpnp","machine.xml"),
        os.path.join(cwd,"machine.xml"),
        os.path.join(cwd,".openpnp2","machine.xml"),
        os.path.join(base_dir,"..","..","machine.xml"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None