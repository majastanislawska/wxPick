import wx
import cv2
import numpy
import time
import src.gui.panel.topcam
import logging
#src.engine logger have handler that puts into log notebook
logger = logging.getLogger("src.engine") 

ID = wx.NewIdRef()
name="Focus"
panel = None
parent=None
btn=None
running = False
last_result =(0,0,0)
#fill thiis dict with your results
calibration_table = {
        895:  -11,
        835: -10,
        819:   -9,
        800:   -8,
        765:   -7,
        735:   -6,
        695:   -5,
        655:   -4,
        635:   -3,
        612:   -2,
        582:   -1,
        512:    0, # pcb level
        0:     10
    }

def create(parent:wx.ScrolledWindow):
    global name,panel,btn
    panel = wx.CollapsiblePane(parent, wx.ID_ANY,"Focus",style=wx.CP_NO_TLW_RESIZE )
    panel.Collapse( False )
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    btn = wx.Button(panel.GetPane(), label="Start smart Focus")
    sizer.Add(btn, 0, wx.ALIGN_LEFT | wx.ALL, 5)
    btn2 = wx.Button(panel.GetPane(), label="Clear overlay")
    sizer.Add(btn2, 0, wx.ALIGN_LEFT | wx.ALL, 5)
    panel.GetPane().SetSizer(sizer)
    panel.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, lambda e: parent.Layout())
    btn.Bind(wx.EVT_BUTTON,autofocus_hill_climb)
    btn2.Bind(wx.EVT_BUTTON,clear_overlay)
    return panel

def clear_overlay(evt):
    src.gui.panel.topcam.topcam.set_frameoverlay(None)
    src.gui.panel.topcam.topcam.canvas_overlays.remove(canvas_overlay)

def autofocus_hill_climb(evt):
    global running,btn
    btn.Enable(False)
    running = True
    results={}
    if not src.gui.panel.topcam.topcam.is_enabled:
        src.gui.panel.topcam.cam_enable(True)
    src.gui.panel.topcam.topcam.canvas_overlays.append(canvas_overlay)
    src.gui.panel.topcam.topcam.set_autoproperty(2,True) #autofocus
    src.gui.panel.topcam.topcam.set_autoproperty(1,True) #autoexposure
    src.gui.panel.topcam.topcam.set_autoproperty(4,True) #auto_whitebalance
    src.gui.panel.topcam.topcam.set_autoproperty(2,False) #autofocus
    src.gui.panel.topcam.topcam.set_autoproperty(1,False) #autoexposure
    src.gui.panel.topcam.topcam.set_autoproperty(4,False) #auto_whitebalance
    src.gui.panel.topcam.topcam.set_property(1,625) # exposure time in ms
    src.gui.panel.topcam.topcam.set_property(2,1023) # focus to reset?
    src.gui.panel.topcam.topcam.set_property(4,4800) # whitebalance
    # src.gui.panel.topcam.topcam.set_property(7,41) #contrast
    # src.gui.panel.topcam.topcam.set_property(11,8) #sharpness
    wx.CallLater(500, _hill_climb_step, pos=[0], step=128, best_score=-1, results=results)

def _hill_climb_step( pos, step, best_score, results):
    logger.info(f"Focus: pos={pos}, step={step}, best_score={best_score}")
    src.gui.panel.topcam.topcam.set_property(2,pos[-1])
    #two-step to let camera move.
    wx.CallLater(220, _evaluate_step, pos, step, best_score, results)

def _evaluate_step(pos, step, best_score, results):
    global last_result
    cur_pos= pos[-1]
    frame = src.gui.panel.topcam.topcam.get_raw_frame()
    time.sleep(0.1)  # wait before next frame grab
    frame =cv2.addWeighted(frame,0.5,src.gui.panel.topcam.topcam.get_raw_frame(),0.5,0)
    # frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 15)
    # cv2.imshow("autofocus input", frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cx=int(src.gui.panel.topcam.topcam.raw_optical_cx)
    cy=int(src.gui.panel.topcam.topcam.raw_optical_cy)
    #half of size of square to be analyzed
    s=int(src.gui.panel.topcam.topcam.frame_h/4)
    ROI = numpy.s_[cy-s:cy+s, cx-s:cx+s]
    roi = gray[ROI]
    # cv2.imshow("autofocus roi", roi)
    #pick algo
    # (score, heatmap)=brenner(roi)
    # (score, heatmap)=tenengrad(roi)
    # (score, heatmap)=variance_of_laplacian(roi)
    (score, heatmap)=energy_of_laplacian(roi)
    # (score, heatmap)=normalized_variance(roi)
    # (score, heatmap)=canny_edge_density(roi)
    heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    # cv2.imshow("autofocus heatmap", heatmap_color)
    # full_heatmap = numpy.zeros_like(frame)
    #we need to place heatmap into full frame for undistortion to work properly
    frame[ROI] = heatmap_color
    # cv2.imshow("autofocus full heatmap", full_heatmap)
    undistorted_heatmap = src.gui.panel.topcam.topcam.undistort_frame(frame)
    # cv2.imshow("autofocus undistorted heatmap", undistorted_heatmap)
    src.gui.panel.topcam.topcam.set_frameoverlay(undistorted_heatmap)
    logger.info(f"Pos {pos} cur:{cur_pos:4d} → score {score:8.3f} best {best_score:8.3f} {step}")
    last_result=(cur_pos, 0, score)
    if cur_pos in results:  results[cur_pos].append(score)
    else:                   results[cur_pos] = [score]
    if score > best_score:
        # logger.info(f" New best score!")
        candidate_pos = cur_pos + int(step)
        candidate_pos = max(0, min(1023, candidate_pos))
        pos.append(candidate_pos)
        wx.CallLater(100, _hill_climb_step,pos,step,score,results)
    else:
        if abs(step)<=1: #no point going sub resolution
            if step>0: #do scan in other direction
                wx.CallLater(100, _hill_climb_step, pos, -128,best_score,results)
            else: finalize_focus(cur_pos,best_score,results)
            return
        pos.pop()  # remove last (worse) position
        new_step = step * 0.5
        candidate_pos = pos[-1] + int(new_step)
        candidate_pos = max(0, min(1023, candidate_pos))
        pos.append(candidate_pos)
        wx.CallLater(100, _hill_climb_step, pos,new_step,best_score,results)

def finalize_focus(final_pos, best_score,results):
    global running,btn,last_result
    best_pos = final_pos
    for p in sorted(results.keys()):
        scores = results[p]
        max = None #max(scores)
        if best_score==max: best_pos=p
        logger.info(f"pos {p} max={max}, {scores}")
    if best_pos != final_pos:
        logger.info(f"AUTOFOCUS: moving to best pos {best_pos} from {final_pos}")
        final_pos=best_pos
    src.gui.panel.topcam.topcam.set_property(2,final_pos)
    distance = interpolate_distance(final_pos)
    logger.info(f"AUTOFOCUS DONE → pos {final_pos}, distance {distance:.2f} mm")
    btn.Enable(True)
    last_result=(final_pos, distance, None)
    running = False
    # src.gui.panel.topcam.cam_enable(False)

def interpolate_distance(pos):
    positions = sorted(calibration_table.keys())
    if pos <= positions[0]: return calibration_table[positions[0]]
    if pos >= positions[-1]: return calibration_table[positions[-1]]
    # Find interval
    for i in range(len(positions)-1):
        p1, p2 = positions[i], positions[i+1]
        if p1 <= pos <= p2:
            d1 = calibration_table[p1]
            d2 = calibration_table[p2]
            fraction = (pos - p1) / (p2 - p1)
            # If either d1 or d2 is zero → linear interpolation
            if d1 == 0 or d2 == 0: return d1 + fraction * (d2 - d1)
            # Normal case: both non-zero → interpolate in 1/d space (more physically correct)
            inv_dist = (1-fraction)/d1 + fraction/d2
            return 1.0 / inv_dist
    return 0.0  # fallback (should never hit)


def canvas_overlay(w,h,fx,fy,canvas_rgb):
    pos, dist, score = last_result
    # 1. Big green text
    text = f"{dist:.1f} mm"
    cv2.putText(canvas_rgb, text, (10, h-25), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 6)
    cv2.putText(canvas_rgb, text, (10, h-25), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 2)
    # 2. Small info
    cv2.putText(canvas_rgb, f"pos: {pos} score: {score}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)


# --------------------------------------------------------------
# TUNABLE PARAMETERS – change these once for your camera/PCB
# --------------------------------------------------------------
SOBEL_KSIZE = 3                         # 3 or 5 – 3 is faster & enough
GAUSS_BLUR_FOR_VOLAPLACIAN = (5, 5)     # helps on very noisy sensors

def brenner(roi):
    diff = roi[:, 2:] - roi[:, :-2]
    score = numpy.mean(diff * diff)
    # heatmap: absolute difference
    heatmap = numpy.abs(diff).astype(numpy.uint8)
    heatmap = cv2.resize(heatmap, (roi.shape[1], roi.shape[0]))
    return float(score), heatmap

def tenengrad(roi, ksize=SOBEL_KSIZE):
    gx = cv2.Sobel(roi, cv2.CV_64F, 1, 0, ksize=ksize)
    gy = cv2.Sobel(roi, cv2.CV_64F, 0, 1, ksize=ksize)
    grad = numpy.sqrt(gx*gx + gy*gy)
    score = grad.mean()                 # 
    # score = grad.var() #– mean is more stable apparently
    heatmap = numpy.clip(grad / numpy.percentile(grad, 99) * 255, 0, 255).astype(numpy.uint8)
    return float(score), heatmap

def variance_of_laplacian(roi):
    blurred = cv2.GaussianBlur(roi, GAUSS_BLUR_FOR_VOLAPLACIAN, 0)
    lap = cv2.Laplacian(blurred, cv2.CV_64F)
    score = lap.var()
    heatmap = numpy.abs(lap)
    heatmap = numpy.clip(heatmap / numpy.percentile(heatmap, 99) * 255, 0, 255).astype(numpy.uint8)
    return float(score), heatmap

# ----------------------------------------------------------------
# 4. Energy of Laplacian (sum of squared response) – very sharp peaks
# ----------------------------------------------------------------
def energy_of_laplacian(roi):
    blurred = cv2.GaussianBlur(roi, GAUSS_BLUR_FOR_VOLAPLACIAN, 0)
    lap = cv2.Laplacian(blurred, cv2.CV_64F)
    score = numpy.sum(lap * lap)
    heatmap = numpy.abs(lap)
    heatmap = numpy.clip(heatmap / numpy.percentile(heatmap, 95) * 255, 0, 255).astype(numpy.uint8)
    return float(score), heatmap

# ----------------------------------------------------------------
# 5. Normalized Gray-Level Variance (very robust to illumination changes)
# ----------------------------------------------------------------
def normalized_variance(roi):
    mean = roi.mean()
    if mean == 0:
        return 0.0, numpy.zeros_like(roi, dtype=numpy.uint8)
    score = roi.var() / mean
    # simple edge-like heatmap
    edges = cv2.Canny(roi, 50, 150)
    heatmap = edges
    return float(score), heatmap

# Tunable params for this method
CANNY_LOW = 0     # Lower = catches more weak edges
CANNY_HIGH = 30    # Higher = ignores noise
BLUR_SIZE = (7, 7) # Larger = more noise suppression (try (5,5) for faster)
BLUR_SIGMA = 1.5   # Gaussian sigma (1.0–2.0; lower = sharper but noisier)
def canny_edge_density(roi):
    blurred = cv2.GaussianBlur(roi, BLUR_SIZE, BLUR_SIGMA)
    edges = cv2.Canny(blurred, CANNY_LOW, CANNY_HIGH, apertureSize=3)
    # Density score (nonzero edges / total pixels)
    nonzero_count = numpy.count_nonzero(edges)
    size = edges.shape[0] * edges.shape[1]
    score = float(nonzero_count) / size
    score= score*1000
    heatmap_color = cv2.applyColorMap(edges, cv2.COLORMAP_JET)
    return score, heatmap_color
