import numpy
import cv2
import time
import logging
logger = logging.getLogger("src.engine")

def hough_fiducials(cam,min_r,max_r,hough2):
    frame1=cam.get_frame()
    time.sleep(0.1)
    frame2=cam.get_frame()
    # cv2.imshow("frame1", frame1)
    # cv2.imshow("frame2", frame2)
    frame=cv2.addWeighted(frame1, 0.5, frame2, 0.5, 0)
    diff = cv2.normalize( cv2.absdiff(frame1, frame2), None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    # cv2.imshow("diff", diff)
    noise_map = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    noise_mask = cv2.dilate(noise_map, numpy.ones((5,5), numpy.uint8), iterations=2)  # expand noisy areas slightly
    # cv2.imshow("noise_mask", noise_mask)
    noise_blur = cv2.GaussianBlur(frame, (7,7), 0)  # strong blur for noisy spots
    # cv2.imshow("noise_blur", noise_blur)
    frame[noise_mask > 0] = noise_blur[noise_mask > 0]
    # Optional: enhance edges from diff (add back subtle boundaries)
    # edge_boost = cv2.Laplacian(noise_map, cv2.CV_8U)
    # cv2.imshow("edge_boost", edge_boost)
    # denoised = cv2.addWeighted(denoised, 1.0, cv2.cvtColor(edge_boost, cv2.COLOR_GRAY2BGR), 0.15, 0)
    # cv2.imshow("denoised2", denoised)
    gray=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("frame", gray)
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # clahe = cv2.createCLAHE(clipLimit=100.0, tileGridSize=(8,8))
    # enhanced = clahe.apply(gray)
    blurred = cv2.GaussianBlur(gray, (9, 9), 1.5)
    # blurred3 = cv2.GaussianBlur(enhanced, (9, 9), 1.5)
    # cv2.imshow("blurred", blurred)
    # cv2.imshow("blurred3", blurred3)
    # cv2.imshow("enhanced", enhanced)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT,
        dp=1.3,                    # accumulator resolution
        minDist=50,                 # min distance between circles
        param1=150,                # Canny high threshold
        param2=hough2,                 # accumulator threshold (lower = more circles)
        minRadius=min_r,maxRadius=max_r)
    num=None if circles is None else circles.size
    logger.info(f"hough_fiducials: param2={hough2} detected={num//3}") #size is times 3
    if circles is None: return None
    circles=numpy.round(circles[0, :]).astype("int")
    heatmap=numpy.zeros((cam.frame_h, cam.frame_w, 3), dtype=numpy.uint8)
    for (x, y, r) in circles:
        cv2.circle(heatmap, (int(x), int(y)), int(r), (0, 255, 255), 2)
        cv2.circle(heatmap, (int(x), int(y)), 3, (0, 0, 255), -1)
        cv2.putText(heatmap, f"{r:.1f}", (int(x)+10, int(y)-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cam.set_frameoverlay(heatmap)
    return circles
