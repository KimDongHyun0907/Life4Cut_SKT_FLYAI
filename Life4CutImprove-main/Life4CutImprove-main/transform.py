import sys
sys.path.append("ai_resources")

import os
from bgrmat import *
from Real_ESRGAN import *

sys.path.append("..")

def execute(isChangeBackground: bool, background_path, frames_path, sr_frames_path, output_video_path):
    # framesFromVideo(input_video_path, frames_path)
    Real_ESRGAN(sr_frames_path, frames_path)
    if isChangeBackground:
        ml = mattedList(sr_frames_path, PRECISION, DEVICE)
        composeToVideo(ml, cv2.imread(background_path, cv2.IMREAD_COLOR), frames_path, output_video_path, DEVICE)
    else:
        framesToVideo(output_video_path, sr_frames_path)
    print("end",time.strftime('%X', time.localtime(time.time())))
if __name__ == "__main__":
    FRAMES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames")
    SR_FRAMES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sr_frames")
    BACKGROUND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bgr.jpg")
    INPUT_VIDEO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample", "data", "videocr1.mp4")
    OUTPUT_VIDEO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result.mp4")
    execute(False, INPUT_VIDEO_PATH, BACKGROUND_PATH, FRAMES_PATH, SR_FRAMES_PATH, OUTPUT_VIDEO_PATH)
