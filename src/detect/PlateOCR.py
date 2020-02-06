
import cv2
import numpy as np

from detect.yolo import Yolo


class PlateOCR():
    def __init__(self):
        self.yolo = Yolo(confThreshold=0.5,nmsThreshold=0.4,inpWidth=200,inpHeight=200,detectType="ocr")
        self.yolo.ConfModel(coco="./data/yolo/ocr/ocr.names",cfg="./data/yolo/ocr/ocr.cfg",weights="./data/yolo/ocr/ocr.weights")

    def detect(self,img):
        status,img = self.preprocess(img)
        if(status):
            cords,label,conf = self.yolo.detect(img)
            if(len(cords) == 10):
                cv2.imshow("plate",img)
                # print(cords)
                # print(np.array(cords))
                labelOrder = np.argsort(np.array(cords)[:,0])
                label = list(label)
                tempLabel = [None]*10
                for i,at in enumerate(labelOrder):
    	            tempLabel[i] = label[at]
                label = ''.join(map(str,tempLabel))
                print(label)
                cv2.waitKey()
                return cords,label,True
            else:
                return [],[],False

        else:
            return [],[],False

    def preprocess(self,img):
        img = self.scale_frame(img,500)
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

    def preProcess(self,plateCords):
        if plateCords is not None:
            plate = self.scale_frame(plateCords,500)
            contours,_ = cv2.findContours(plate,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            img = cv2.drawContours(np.zeros((plate.shape[0],plate.shape[1],3)), contours, -1, (0,0,255), 1)
            for ctr in contours:
                x,y,w,h = cv2.boundingRect(ctr)
                if w<h:
                    img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.imshow('plate',plate)
        pass
        
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