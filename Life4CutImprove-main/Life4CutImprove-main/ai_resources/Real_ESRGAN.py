from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from gfpgan import GFPGANer
import os
import cv2
import time


def Real_ESRGAN(HR_image_path, LR_image_path):
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
    # 확대 정도
    netscale = 4
    # HR_image 저장 경로
    output_path = HR_image_path

    upsampler = RealESRGANer(
            scale=netscale,
            # ESRGAN 모델 경로
            model_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'realesrgan', 'weights', 'RealESRGAN_x4plus.pth'),
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half= not 'fp16')

    # face_enhancing
    face_enhancer = GFPGANer(
        # GFPGAN 모델 경로
        model_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'realesrgan', 'weights', 'GFPGANv1.3.pth'),
        upscale=4,
        arch='clean',
        channel_multiplier=2,
        bg_upsampler=upsampler)

    os.makedirs(output_path, exist_ok=True)

    suffix = ''
    # LR_image path
    paths = LR_image_path
    print("start",time.strftime('%X', time.localtime(time.time())))
    for cur_path in os.listdir(paths):
        imgname, extension = cur_path[:-4], cur_path[-4:]
        # print('Testing', imgname)

        img = cv2.imread(paths + '/' + cur_path, cv2.IMREAD_UNCHANGED)

        if len(img.shape) == 3 and img.shape[2] == 4:
            img_mode = 'RGBA'
        else:
            img_mode = None

        try:
            _, _, output = face_enhancer.enhance(img, has_aligned=False, only_center_face=False, paste_back=True)
        except RuntimeError as error:
            print('Error', error)
            print('If you encounter CUDA out of memory, try to set --tile with a smaller number.')
        else:
            extension = extension[1:]

            if img_mode == 'RGBA':  # RGBA images should be saved in png format
                extension = 'png'
            if suffix == '':
                save_path = os.path.join(HR_image_path + '/', f'{imgname}.{extension}')
            else:
                save_path = os.path.join(HR_image_path + '/', f'{imgname}_{suffix}.{extension}')

            cv2.imwrite(save_path, output)
    print("end",time.strftime('%X', time.localtime(time.time())))