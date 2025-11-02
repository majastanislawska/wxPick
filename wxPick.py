#!/usr/bin/env python
import logging
import src.main
from cv2_enumerate_cameras import enumerate_cameras

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )
    for camera_info in enumerate_cameras():
        print(f'{camera_info.index}: {camera_info.name}')
    src.main.main()