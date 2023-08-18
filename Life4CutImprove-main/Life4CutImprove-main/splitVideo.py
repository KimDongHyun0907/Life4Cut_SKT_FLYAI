import cv2
import os

def frame(name, part_image, fw, fh):
    directory = "static/upload_video"    
    vidcap = cv2.VideoCapture(os.path.join(directory,name))
    success,image = vidcap.read()

    h,w,_ = image.shape
    w1,h1,w2,h2 = part_image[-1]
    
    # 사이즈가 안맞는 프레임을 선택한 경우(수정필요..)
    if h // w != fh // fw:
        return False
    
    frame_numb = 0
    while success:
        for i in range(1,1+len(part_image)):
            w1,h1,w2,h2 = part_image[i-1]
            w1 = w1 * w // fw
            h1 = h1 * w // fw
            w2 = w2 * w // fw
            h2 = h2 * w // fw
            cv2.imwrite("static/user_image/%d/%06d.jpg" % (i,frame_numb), image[h1+1:h2,w1+1:w2,:]) 
        success,image = vidcap.read()
        frame_numb += 1
    return True

# 8개 프레임(세로)
def frame1(name):
    # 1000 * 1500
    # w1,h1,w2,h2
    part_image = [(60, 68, 490, 366),
                  (508, 68, 938, 366),
                  (60, 384, 490, 682),
                  (508, 384, 938, 682),
                  (60, 698, 490, 996),
                  (508, 698, 938, 996),
                  (60, 1013, 490, 1311),
                  (508, 1015, 938, 1313)]
    return frame(name, part_image, 1000, 1500)

def frame2(name):
    # 1000 * 667
    # w1,h1,w2,h2
    part_image = [(40, 39, 401, 328),
    			  (412, 39, 773, 328),
    			  (40, 338, 401, 627),
    			  (412, 338, 773, 627)]
    return frame(name, part_image, 1000, 667)
    
def frame3(name):
    # 1000 * 667
    # w1,h1,w2,h2
    part_image = [(89, 39, 419, 318),
                  (427, 39, 758, 318),
                  (245, 351, 577, 630),
                  (584, 351, 916, 630)]
    return frame(name, part_image, 1000, 667)
    
def frame4(name):
    # 1000 * 1500
    # w1,h1,w2,h2
    part_image = [(54, 355, 477, 864),
                  (526, 108, 949, 617),
                  (54, 855, 477, 1395),
                  (525, 638, 949, 1148)]
    return frame(name, part_image, 1000, 1500)

def frame5(name):
    # 579 * 1740
    # w1,h1,w2,h2
    part_image = [(26, 24, 553, 374),
                  (26, 399, 553, 748),
                  (26, 774, 553, 1123),
                  (26, 1149, 553, 1498)]
    return frame(name, part_image, 579, 1740)