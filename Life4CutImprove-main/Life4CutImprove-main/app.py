from flask import Flask, render_template, request, session, redirect, make_response, url_for
from werkzeug.utils import secure_filename
import sys
import os
import shutil
import time
import splitVideo as sv
from transform import execute

application = Flask(__name__)
application.config['SECRET_KEY'] = "passwd1234" #임의값

# 파일 압축 코드
def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to) 
    shutil.move('%s.%s'%(name,format), destination)
    

@application.route("/")
def index():
    return render_template("index.html")

@application.route("/", methods=['POST'])
def upload_video():
    if "chooseFile" not in request.files:
        return render_template("index.html")
    
    file = request.files['chooseFile']
    
    # 이전 파일 삭제
    directory = "static/upload_video"
    if os.path.exists(directory):
       shutil.rmtree(directory)
    os.makedirs(directory)
    
    # 임의로 파일 이름 고정, 확장자는 유지
    filename = secure_filename(file.filename)
    if filename:
        file.save(os.path.join(directory,"video"+filename[-4:]))
        return redirect("/frame")
    return render_template("index.html")

@application.route("/frame", methods=['GET','POST'])
def check_frame():
    if request.method == "GET":        
        return render_template("frame.html")
    
    elif request.method == "POST":
        # 만약 비디오 업로드가 안되었다면 index.html로 이동하기
        filelist = os.listdir("static/upload_video")
        if len(filelist) == 0:
            return redirect("/")
        
        # 저장된 비디오 이름
        filename = filelist[0]
        
        # 저장된 비디오의 프레임
        frame = request.form.get('frames')
        # frame = request.args.get('frames')

        # 비디오 이미지 저장될 위치 비우기
        directory = "static/user_image/"
        if os.path.exists(directory):
           shutil.rmtree(directory)
        os.makedirs(directory)
        number = 4
        flag = True

        # 프레임에 따라 비디오 이미지 자르기 & 저장하기
        if frame == "frame1":
            for i in range(1,9):
                os.makedirs(directory+str(i))
            flag = sv.frame1(filename)
            number = 8
        elif frame == "frame2":
            for i in range(1,5):
                os.makedirs(directory+str(i))
            flag = sv.frame2(filename)
        elif frame == "frame3":
            for i in range(1,5):
                os.makedirs(directory+str(i))
            flag = sv.frame3(filename)
        elif frame == "frame4":
            for i in range(1,5):
                os.makedirs(directory+str(i))
            flag = sv.frame4(filename)
        elif frame == "frame5":
            for i in range(1,5):
                os.makedirs(directory+str(i))
            flag = sv.frame5(filename)
        
        if not flag:
            return render_template("frame.html")
        
        return render_template("choice.html", number = number)


@application.route("/choice", methods=['GET','POST'])
def choice():
    if request.method == "GET":
        return render_template("choice.html")
    
    elif request.method == "POST":
        # 선택된 영상 번호들
        choice_list = request.form.getlist('choice')
        
        result = []
        for choice in choice_list:
            #choice에 해당하는 이미지 폴더 번호
            choice_numb = choice[0]
            image_root = os.path.join("static/user_image/",choice_numb)
            result.append("user_image/"+choice_numb+"/000001.jpg")
        
        res = make_response(render_template("background.html", result = result, sel = len(result)))
        res.set_cookie('choice_list', ",".join(choice_list))
        res.set_cookie('result_list', ",".join(result))
        
        return res
            

        
@application.route("/background", methods=['GET','POST'])
def background():
    if request.method == "GET":
        result = request.cookies.get('result_list').split(",")
        return render_template("background.html", result = result, sel = len(result))
    elif request.method == "POST":
        choice_list = request.cookies.get('choice_list').split(",")
        result = request.cookies.get('result_list').split(",")
        
        directory = "static/result"
        if not os.path.exists(directory):
               os.makedirs(directory)
        
        for i in range(len(choice_list)):
            # 선택된 배경 주소
            bg = request.form.get('background'+str(i))
            if not bg:
                return render_template("background.html", result = result, sel = len(result))
            
            #choice에 해당하는 이미지 폴더 번호
            choice_numb = choice_list[i][0]
            image_root = os.path.join("static/user_image",choice_numb)
            
            # 모델에 넣기
            FRAMES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static","user_image",choice_numb)
            SR_FRAMES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static","sr_frames")
            OUTPUT_VIDEO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static","result","result%d.mp4" % (i+1))   
            
            if bg[-4:] == "none":
                print("none_bg")
                # time.sleep(5)
                execute(False, None, FRAMES_PATH, SR_FRAMES_PATH, OUTPUT_VIDEO_PATH)
            else:
                # print("with_bg")
                BACKGROUND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "bg_image", bg[-4:]+".jpg")
                execute(True, BACKGROUND_PATH, FRAMES_PATH, SR_FRAMES_PATH, OUTPUT_VIDEO_PATH)
                # time.sleep(5)
                
            directory = "static/sr_frames"
            if os.path.exists(directory):
                shutil.rmtree(directory)
        
        make_archive('static/result', 'static/result_video/result.zip')
        
        directorys = ["static/user_image","static/result"]
        for directory in directorys:
            if os.path.exists(directory):
                shutil.rmtree(directory)
        
        return render_template("result.html")    

    

    
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, debug = True)
