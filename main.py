import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '4'

import cv2
import tr
import numpy as np
import matplotlib.pyplot as plt
from utils.local_utils import detect_lp
from os.path import splitext,basename
from keras.models import model_from_json
from keras.preprocessing.image import load_img, img_to_array
from keras.applications.mobilenet_v2 import preprocess_input
import glob
import pandas as pd
def load_model(path):
    try:
        path = splitext(path)[0]
        with open('%s.json' % path, 'r') as json_file:
            model_json = json_file.read()
        model = model_from_json(model_json, custom_objects={})
        model.load_weights('%s.h5' % path)
        print("Loading model successfully...")
        return model
    except Exception as e:
        print(e)
        
def preprocess_image(img,resize=False):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img / 255
    if resize:
        img = cv2.resize(img, (224,224))
    return img

def get_plate(image_path, Dmax=608, Dmin = 608):
    vehicle = preprocess_image(image_path)
    ratio = float(max(vehicle.shape[:2])) / min(vehicle.shape[:2])
    side = int(ratio * Dmin)
    bound_dim = min(side, Dmax)
    try:
        _ , LpImg, _, cor = detect_lp(wpod_net, vehicle, bound_dim, lp_threshold=0.5)
        return vehicle, LpImg, cor
    except:
        return False

wpod_net_path = "models/npr-net.json"
wpod_net = load_model(wpod_net_path)

def do_process(frame):
    
    vehicle, LpImg,cor = get_plate(frame)
    if (len(LpImg)): #check if there is at least one license image

        plate_image = cv2.convertScaleAbs(LpImg[0], alpha=(170.0))

        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(7,7),0)
        binary = cv2.threshold(gray, 195, 255,4)[1]
        binary = binary[30:-30,:]
        binary = cv2.resize(binary,(int(binary.shape[1]),int(binary.shape[0]*0.6)))

        # plate_image = plate_image[30:-30,:]
        # plate_image=cv2.resize(plate_image,(int(plate_image.shape[1]),int(plate_image.shape[0]*0.6)))
        res=tr.recognize(binary)

        return res

def video_process(vid_path,sampling_period=1,print_out=True,save_file=True):
    cap = cv2.VideoCapture(vid_path)
    num_frame=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps_=cap.get(cv2.CAP_PROP_FPS)
    if num_frame < 1:
        return f'{vid_path} doesnt exist!'
    plates_={'second':[],'plate_num':[],'score':[]}
    for i in range(int(num_frame)):
        ret, frame = cap.read()
        if i%int(fps_*sampling_period)==0:
            try:
                res_=do_process(frame)
                sec_=i/int(fps_)
                plates_['score'].append(res_[1])
                plates_['plate_num'].append(res_[0])
                plates_['second'].append(sec_)
                if print_out:
                    print(f"sec {sec_} --> plate num: {res_[0]}  OCR confidence: {res_[1]}")
            except:
                pass
    df=pd.DataFrame(plates_)
    if save_file:
        file_name_=vid_path.split('/')[1].split('.')[0]


        uniq_list = []
        CONFIDENCE_THRESH = 0.90
        TIME_DIFFER = 10

        correct = 0
        incorrect = 0
        p_sec = -10
        for i in range(df.shape[0]):
            n_sec = df.iloc[i]['second']
            
            if df.iloc[i]['score'] > CONFIDENCE_THRESH:
                search = df.iloc[i]['plate_num']
                if not any(e[1] == search for e in uniq_list):
                    if abs(p_sec - n_sec) > TIME_DIFFER:
                        uniq_list.append([df.iloc[i]['second'], df.iloc[i]['plate_num']])
                        p_sec = df.iloc[i]['second']
                        
                        if len(uniq_list) > 1:
                            score = str(correct + 1) + '/' + str(correct + 1 +incorrect)
                            uniq_list[-2].append(score)
                            correct = 0
                            incorrect = 0
                        
                else:
                    correct += 1
            else:
                incorrect += 1
                
        score = str(correct + 1) + '/' + str(correct + 1 +incorrect)            
        uniq_list[-1].append(score)
        str2save=''
        for i in range(len(uniq_list)):
            str2save+=f'Car #{i+1}: first seen={str(uniq_list[i][0])} sec *** plate #={uniq_list[i][1]} *** score={uniq_list[i][2]}\n'
        with open(f"outputs/{file_name_}.txt", "w") as text_file:
            text_file.write(str2save)
        print(f"the output saved to: outputs/{file_name_}.txt")