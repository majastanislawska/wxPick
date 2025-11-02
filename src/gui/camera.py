import wx
import cv2,numpy
import logging
logger = logging.getLogger(__name__)

def demonstrate_properties(cap):
    print("\nTesting Video Capture Properties:")
    caplist=[(eval(f"cv2.{k}"),k) for k in cv2.__dict__.keys() if k.startswith("CAP_PROP")]
    for prop_id,k in sorted(caplist, key=lambda a: a[0]):
        print("%s %s %s"%(prop_id, k, cap.get(prop_id)))

class Camera(wx.StaticBitmap):
    def __init__(self, parent, camera_id,zoom_slider):
        super().__init__(parent, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size(-1,-1), 0 )
        self.camera_id= camera_id
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
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            logging.error(f"Failed to open camera {self.camera_id}")
            raise ValueError(f"Failed to open camera {self.camera_id}")
        # demonstrate_properties(self.cap)
        checks=[]
        checks.append(self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640.0))
        checks.append(self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480.0))
        checks.append(self.cap.set(cv2.CAP_PROP_AUTOFOCUS,1))
        checks.append(self.cap.set(cv2.CAP_PROP_SETTINGS, 1))
        w=self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h=self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        checks.append(w)
        checks.append(h)
        num=self.cap.get(cv2.CAP_PROP_SAR_NUM)
        den=self.cap.get(cv2.CAP_PROP_SAR_DEN)
        checks.append(num)
        checks.append(den)
        self.aspect_ratio =w/h
        self.resolution=(int(w),int(h))
        self.is_enabled=True
        savedsize=self.GetSize()
        self.SetBitmap(self.bitmap)
        self.SetSize(savedsize)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        checks.append(self.timer.Start(self.get_framerate()))
        logging.info("cam_start: %s"%checks)


    def cam_stop(self):
        self.is_enabled=False
        self.timer.Stop()
        self.cap.release()
        self.Unbind(wx.EVT_PAINT)
        savedsize=self.GetSize()
        self.SetBitmap(wx.ArtProvider.GetBitmap("cam-off", wx.ART_OTHER,(48,48)))
        self.SetSize(savedsize)
        self.Refresh()

    def cam_enable(self, enable):
        if enable: self.cam_start()
        else: self.cam_stop()

# get frame
    def on_timer(self, event):
        ret, frame = self.cap.read()
        if not ret: return
        frame_h, frame_w = frame.shape[:2]
        self.aspect_ratio = frame_w / frame_h
        # Process frame
        #frame = self.processor.process(frame)
        cw,ch = self.GetSize()
        self.width = int(min(cw, ch * self.aspect_ratio))
        self.height = int(min(ch, cw / self.aspect_ratio))
        if self.zoom_level>1:
            crop_w = int(frame_w / self.zoom_level)
            crop_h = int(frame_h / self.zoom_level)
            start_x = (frame_w - crop_w) // 2
            start_y = (frame_h - crop_h) // 2
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

    def get_framerate(self):
        return int(self.cap.get(cv2.CAP_PROP_FPS))

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

# [{'width': 320, 'height': 180, 'subtypeName': 'svuy'}, 
#  {'width': 320, 'height': 180, 'subtypeName': 'v024'}, 
#  {'width': 320, 'height': 240, 'subtypeName': 'svuy'}, 
#  {'width': 320, 'height': 240, 'subtypeName': 'v024'}, 
#  {'width': 424, 'height': 240, 'subtypeName': 'v024'}, 
#  {'width': 640, 'height': 360, 'subtypeName': 'v024'}, 
#  {'width': 640, 'height': 480, 'subtypeName': 'svuy'}, 
#  {'width': 640, 'height': 480, 'subtypeName': 'v024'}, 
#  {'width': 848, 'height': 480, 'subtypeName': 'v024'}, 
#  {'width': 960, 'height': 540, 'subtypeName': 'v024'}, 
#  {'width': 1280, 'height': 720, 'subtypeName': 'v024'}, 
#  {'width': 1600, 'height': 1200, 'subtypeName': 'v024'}, 
#  {'width': 1920, 'height': 1080, 'subtypeName': 'v024'}, 
#  {'width': 1920, 'height': 1080, 'subtypeName': 'svuy'}, 
#  {'width': 2592, 'height': 1944, 'subtypeName': 'v024'}, 
#  {'width': 2592, 'height': 1944, 'subtypeName': 'svuy'}, 
#  {'width': 3264, 'height': 2448, 'subtypeName': 'v024'}, 
#  {'width': 3264, 'height': 2448, 'subtypeName': 'svuy'}]
# CAP_PROP_POS_MSEC       =0, //!< Current position of the video file in milliseconds.
# CAP_PROP_POS_FRAMES     =1, //!< 0-based index of the frame to be decoded/captured next.
# CAP_PROP_POS_AVI_RATIO  =2, //!< Relative position of the video file: 0=start of the film, 1=end of the film.
# CAP_PROP_FRAME_WIDTH    =3, //!< Width of the frames in the video stream.
# CAP_PROP_FRAME_HEIGHT   =4, //!< Height of the frames in the video stream.
# CAP_PROP_FPS            =5, //!< Frame rate.
# CAP_PROP_FOURCC         =6, //!< 4-character code of codec. see VideoWriter::fourcc .
# CAP_PROP_FRAME_COUNT    =7, //!< Number of frames in the video file.
# CAP_PROP_FORMAT         =8, //!< Format of the %Mat objects returned by VideoCapture::retrieve().
# CAP_PROP_MODE           =9, //!< Backend-specific value indicating the current capture mode.
# CAP_PROP_BRIGHTNESS    =10, //!< Brightness of the image (only for those cameras that support).
# CAP_PROP_CONTRAST      =11, //!< Contrast of the image (only for cameras).
# CAP_PROP_SATURATION    =12, //!< Saturation of the image (only for cameras).
# CAP_PROP_HUE           =13, //!< Hue of the image (only for cameras).
# CAP_PROP_GAIN          =14, //!< Gain of the image (only for those cameras that support).
# CAP_PROP_EXPOSURE      =15, //!< Exposure (only for those cameras that support).
# CAP_PROP_CONVERT_RGB   =16, //!< Boolean flags indicating whether images should be converted to RGB.
# CAP_PROP_WHITE_BALANCE_BLUE_U =17, //!< Currently unsupported.
# CAP_PROP_RECTIFICATION =18, //!< Rectification flag for stereo cameras (note: only supported by DC1394 v 2.x backend currently).
# CAP_PROP_MONOCHROME    =19,
# CAP_PROP_SHARPNESS     =20,
# CAP_PROP_AUTO_EXPOSURE =21, //!< DC1394: exposure control done by camera, user can adjust reference level using this feature.
# CAP_PROP_GAMMA         =22,
# CAP_PROP_TEMPERATURE   =23,
# CAP_PROP_TRIGGER       =24,
# CAP_PROP_TRIGGER_DELAY =25,
# CAP_PROP_WHITE_BALANCE_RED_V =26,
# CAP_PROP_ZOOM          =27,
# CAP_PROP_FOCUS         =28,
# CAP_PROP_GUID          =29,
# CAP_PROP_ISO_SPEED     =30,
# CAP_PROP_BACKLIGHT     =32,
# CAP_PROP_PAN           =33,
# CAP_PROP_TILT          =34,
# CAP_PROP_ROLL          =35,
# CAP_PROP_IRIS          =36,
# CAP_PROP_SETTINGS      =37, //!< Pop up video/camera filter dialog (note: only supported by DSHOW backend currently. The property value is ignored)
# CAP_PROP_BUFFERSIZE    =38,
# CAP_PROP_AUTOFOCUS     =39,
# CAP_PROP_SAR_NUM       =40, //!< Sample aspect ratio: num/den (num)
# CAP_PROP_SAR_DEN       =41, //!< Sample aspect ratio: num/den (den)