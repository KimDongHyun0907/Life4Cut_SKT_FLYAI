import torch
import cv2
import numpy as np
import os
import gc
from typing import Tuple, List
from BackgroundMattingV2_model import MattingRefine


DEVICE = torch.device('cuda')
PRECISION = torch.float32
WEIGHT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BackgroundMattingV2_model", "pytorch_resnet50.pth")
BACKBONE_SCALE = 0.25
REFINE_MODE = 'sampling'
REFINE_SAMPLE_PIXELS = 80000

def framesFromVideo(video_path: str, frame_path: str):
    """
    read a video from given video_path,
    and save frames in order under given frame_path
    """
    video = cv2.VideoCapture(video_path)
    success, image = video.read()
    if not os.path.exists(frame_path):
        os.mkdir(frame_path)
    count = 0

    while success:
        # compress to (divisible by 4)
        
        # frames.append(image)
        cv2.imwrite(frame_path + "/{:09d}.png".format(count), image)
        success, image = video.read()
        count += 1

def frameListToVideo(video_path:str, frameList: List[np.ndarray]):
    """
    make a video and save to video_path
    using given list of images matrices(ndarray)
    """
    img_shape = frameList[0].shape
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (img_shape[1], img_shape[0]))
    for frame in frameList:
        out.write(frame)
    out.release()

def framesToVideo(video_path: str, frames_path: str):
    """
    make a video and save to video_path
    using images in frames_path
    """
    image_shape = cv2.imread(os.path.join(frames_path, "000000.jpg")).shape
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (image_shape[1], image_shape[0]))
    for file in os.listdir(frames_path):
        img_path = os.path.join(frames_path, file)
        out.write(cv2.imread(img_path, cv2.IMREAD_COLOR))
    out.release()

def getBackgroundFromPixel(img: np.ndarray) -> np.ndarray:
    """
    make background using left top pixel (5, 5)
    argument: img (image written from cv2, in color mode)
    """
    pix_color = img[5, 5]
    bgr = np.full(img.shape, pix_color, dtype=np.uint8)
    return bgr

def encodeForModel(img: np.ndarray, precision: torch.dtype) -> torch.Tensor:
    """
    encode an image opened by opencv to 0-1 normalized tensor
    """
    # transpose to tensor format
    img = np.transpose(img, (2, 0, 1))
    # normalize
    img = img / 255.0
    # to tensor
    img_tensor = torch.from_numpy(np.array([img])).to(precision)
    return img_tensor

def decodeFromModel(res: torch.Tensor) -> np.ndarray:
    """
    decode an image from 0-1 normalized tensor to numpy (opencv)
    """
    img = res.detach().cpu().numpy()[0]
    img = np.transpose(img, (1, 2, 0))
    img = (img * 255.0).astype(np.uint8)
    return img
    
def loadModel(precision: torch.dtype, device: torch.device, backbone_scale: float, refine_mode: str, refine_sample_pixels: int) -> MattingRefine:
    model = MattingRefine(
        backbone='resnet50',
        backbone_scale = backbone_scale,
        refine_mode = refine_mode,
        refine_sample_pixels = refine_sample_pixels,
    )
    model.load_state_dict(torch.load(WEIGHT_PATH))
    model = model.eval().to(precision).to(device)
    return model

def unloadModel(model: MattingRefine):
    del model
    gc.collect()

def runModel(model: MattingRefine, src: torch.Tensor, bgr: torch.Tensor, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    execute a background_matting model using given image,
    and return matted pha and fgr tensor
    """

    src_gpu = src.to(device)
    bgr_gpu = bgr.to(device)
    with torch.no_grad():
        pha, fgr = model(src_gpu, bgr_gpu)[:2]

    return (pha.cpu(), fgr.cpu())

def reshapeTargetBackgroundTensor(background: np.ndarray, img_shape: tuple) -> torch.Tensor:
    """
    reshape target background to the size of video,
    and return to encoded tensor
    """
    background = cv2.resize(background, (img_shape[1], img_shape[0]), interpolation=cv2.INTER_LANCZOS4)
    bgr = encodeForModel(background, PRECISION)
    return bgr

def composeBackground(pha: torch.Tensor, fgr: torch.Tensor, bgr: torch.Tensor) -> np.ndarray :
    """
    compose given bgr tensor using result tensors of model,
    and return composed image (opencv, numpy)
    """
    com = pha * fgr + (1 - pha) * bgr
    composed = decodeFromModel(com)
    return composed

def mattedList(frames_path: str, precision: torch.dtype, device: torch.device) -> List[Tuple[torch.Tensor, torch.Tensor]]:
    """
    create list of results of model with images insixe frames_path
    """
    background_remove = getBackgroundFromPixel(cv2.imread(os.path.join(frames_path , "000000.jpg"), cv2.IMREAD_COLOR))
    bgr_rm = encodeForModel(background_remove, PRECISION)
    matted_list = []
    
    model = loadModel(precision, device, BACKBONE_SCALE, REFINE_MODE, REFINE_SAMPLE_PIXELS)
    for file in os.listdir(frames_path):
        image = cv2.imread(os.path.join(frames_path, file), cv2.IMREAD_COLOR)
        frame = cv2.resize(image, (image.shape[1] - (image.shape[1] % 4), image.shape[0] - (image.shape[0] % 4)), interpolation=cv2.INTER_LANCZOS4)
        fr = encodeForModel(frame, PRECISION)
        matted_result: Tuple[torch.Tensor, torch.Tensor] = runModel(model, fr, bgr_rm, device)
        matted_list.append(matted_result)
    del model
    
    return matted_list

def composeToVideo(matted_list: List[Tuple[torch.Tensor, torch.Tensor]], target_background: np.ndarray, frames_path: str, video_path: str, device: torch.device):
    """
    compose given background using result of mattedList and save video to video_path
    """
    bgr = reshapeTargetBackgroundTensor(target_background, (matted_list[0][0].shape[2], matted_list[0][0].shape[3]))
    com_list = list(map(
            (lambda r : composeBackground(r[0], r[1], bgr)),
            matted_list
        )
    )
    frameListToVideo(video_path, com_list)

# if __name__ == "__main__":
#     framesFromVideo("./video1.avi", FRAMES_PATH)
#     ml = mattedList(FRAMES_PATH, PRECISION, DEVICE)
#     composeToVideo(ml, cv2.imread("./bgr.jpg", cv2.IMREAD_COLOR), FRAMES_PATH, VIDEO_PATH, DEVICE)
