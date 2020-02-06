
import cv2
import numpy as np
from detect.yolo import Yolo
import re


class PlateOCR():
    def __init__(self):
        self.plate_regex = re.compile(r'^[A-Z]{2}[0-9]{1,2}(?:[A-Z])?(?:[A-Z]*)?[0-9]{4}$')
        self.all_states = ['AP', 'AR', 'AS', 'BR', 'CG', 'GA', 'GJ', 'HR', 'HP', 'JK', 'JH', 'KA', 'KL', 'MP', 'MH', 'MN', 'ML', 'MZ', 'NL', 'OR', 'PB', 'RJ', 'SK', 'TN', 'TR', 'UK', 'UP', 'WB', 'TS', 'AN', 'CH', 'DH', 'DD', 'DL', 'LD', 'PY']

        self.yolo = Yolo(confThreshold=0.6,nmsThreshold=0.4,inpWidth=200,inpHeight=200,detectType="ocr")
        self.yolo.ConfModel(coco="./data/yolo/ocr/ocr.names",cfg="./data/yolo/ocr/ocr.cfg",weights="./data/yolo/ocr/ocr.weights")

    def detect(self,img):
        status,img = self.preprocess(img)
        if(status):
            cords,label,conf = self.yolo.detect(img)
            if(len(cords) == 10):
                # cv2.imshow("plate",img)
                # print(cords)
                # print(np.array(cords))
                labelOrder = np.argsort(np.array(cords)[:,0])
                label = list(label)
                tempLabel = [None]*10
                for i,at in enumerate(labelOrder):
    	            tempLabel[i] = label[at]
                label = ''.join(map(str,tempLabel))
                print(str(self.isValid(label))+"  "+label+"  accuracy: "+ str(sum(conf)/10))
                cv2.waitKey()
                return cords,label,True
            else:
                return [],[],False

        else:
            return [],[],False

    def isValid(self,label):
        return True if self.all_states.__contains__(label[:2]) and self.plate_regex.match(label) else False

    def preprocess(self,img):
        cv2.imshow('pre-process',img)
        img = self.scale_frame(img,500)
        kernel = np.ones((3,3),np.uint8)
        img = cv2.dilate(img,kernel)
        cv2.imshow('pre-process dilate',img)
        return True,img

    def scale_frame(self,frame,scale_percent):
        _,frame = cv2.threshold(self.gray(frame),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        result = cv2.resize(frame, dim, interpolation = cv2.INTER_LINEAR) 

        return cv2.merge((result,result,result))

    def gray(self,frame):
        return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    # def preProcess(self,plateCords):
    #     if plateCords is not None:
    #         plate = self.scale_frame(plateCords,500)
    #         contours,_ = cv2.findContours(plate,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #         img = cv2.drawContours(np.zeros((plate.shape[0],plate.shape[1],3)), contours, -1, (0,0,255), 1)
    #         for ctr in contours:
    #             x,y,w,h = cv2.boundingRect(ctr)
    #             if w<h:
    #                 img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
    #         cv2.imshow('plate',plate)
    #     pass
        
    def ratioCheck(self,area, width, height):

        ratio = float(width) / float(height)
        if ratio < 1:
            ratio = 1 / ratio

        aspect = 4.7272
        min = 15*aspect*15  # minimum area
        max = 125*aspect*125  # maximum area

        rmin = 3
        rmax = 6

        if (area < min or area > max) or (ratio < rmin or ratio > rmax):
            return False
        return True

    def isMaxWhite(self,plate):
        avg = np.mean(plate)
        if(avg>=115):
            return True
        else:
            return False

    def validateRotationAndRatio(self,rect):
        (x, y), (width, height), rect_angle = rect

        if(width>height):
            angle = -rect_angle
        else:
            angle = 90 + rect_angle

        if angle>15:
            return False

        if height == 0 or width == 0:
            return False

        area = height*width
        if not ratioCheck(area,width,height):
            return False
        else:
            return True