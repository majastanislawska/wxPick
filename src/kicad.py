import cv2
import numpy
import kiutils.footprint 
import pathlib
import logging
logger = logging.getLogger("src.engine")
lib_dir = '../kicad-footprints'

def find_footprint_files(name,root_dir=lib_dir):
    root = pathlib.Path(root_dir)
    if not root.is_dir(): return []
    matches = {}
    for file_path in root.rglob("*"):
        if not file_path.is_file(): continue
        if file_path.suffix != '.kicad_mod': continue
        if name not in file_path.name: continue
        matches[str(file_path.stem)]=str(file_path)
    return matches


def load_footprint_data(filepath):
    logger.info(f"load_footprint")
    footprint = kiutils.footprint.Footprint().from_file(filepath)
    drawing_elements = []
    for i in footprint.graphicItems:
        if i.layer == 'F.SilkS' and type(i) == kiutils.footprint.FpLine:
            drawing_elements.append({
                'type': 'line',
                'start': [i.start.X, i.start.Y,1],
                'end': [i.end.X, i.end.Y,1],
                # 'width': i.width,
                'stroke': i.stroke.width,
            })
    for pad in footprint.pads:
        off_x = pad.size.X/2.0
        off_y = pad.size.Y/2.0
        points = [(pad.position.X-off_x, pad.position.Y-off_y,1),
                  (pad.position.X-off_x, pad.position.Y+off_y,1),
                  (pad.position.X+off_x, pad.position.Y+off_y,1),
                  (pad.position.X+off_x, pad.position.Y-off_y,1)]
        drawing_elements.append({
            'type': 'pad',
            'points': points,
            'shape': pad.shape,
            'number': pad.number
        })
    return drawing_elements, footprint.position


def transf_2d(angle, scale, tx, ty):
    theta = numpy.radians(angle)
    c, s = numpy.cos(theta), numpy.sin(theta)
    sx=sy=scale
    M = numpy.array([
        [c * sx, -s * sy, tx],
        [s * sx,  c * sy, ty],
        [     0,       0,  1]
    ])
    return M
def draw_overlay(frame, elements, scale, angle, x_offset, y_offset,
                  silk_color = (255, 255, 255), pad_color = (0, 0, 255)):
    M=transf_2d(angle, scale, x_offset, y_offset)
    for element in elements:
        if element['type'] == 'line':
            start = numpy.round(M.dot(element['start'])).astype(int)
            end = numpy.round(M.dot(element['end'])).astype(int)
            width_px = int(element['stroke'] * scale) or 1
            cv2.line(frame, start[:2], end[:2], silk_color, thickness=width_px)
        elif element['type'] == 'pad':
            points=numpy.round([M.dot(point)[:2] for point in element['points']])
            cv2.fillPoly(frame, numpy.array([points], dtype=numpy.int32), pad_color)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    pattern = (gray.astype(numpy.float32) - gray.mean())/gray.std()
    # cv2.imshow("color", frame)
    # cv2.imshow("gray", gray)
    # cv2.imshow("pattern", pattern)
    return pattern

