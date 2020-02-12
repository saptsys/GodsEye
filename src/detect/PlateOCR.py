
import cv2
import numpy as np
from detect.yolo import Yolo
import re


class PlateOCR():
    def __init__(self):
        self.plate_regex = re.compile(r'^[A-Z]{2}[0-9]{1,2}(?:[A-Z])?(?:[A-Z]*)?[0-9]{4}$')
        self.all_states = ['AP', 'AR', 'AS', 'BR', 'CG', 'GA', 'GJ', 'HR', 'HP', 'JK', 'JH', 'KA', 'KL', 'MP', 'MH', 'MN', 'ML', 'MZ', 'NL', 'OR', 'PB', 'RJ', 'SK', 'TN', 'TR', 'UK', 'UP', 'WB', 'TS', 'AN', 'CH', 'DH', 'DD', 'DL', 'LD', 'PY']
        self.inc = 0
        self.yolo = Yolo(confThreshold=0.6,nmsThreshold=0.4,inpWidth=200,inpHeight=200,detectType="ocr")
        self.yolo.ConfModel(coco="./data/yolo/ocr/ocr.names",cfg="./data/yolo/ocr/ocr.cfg",weights="./data/yolo/ocr/ocr.weights")

    def detect(self,img):
        status,img = self.preprocess(img)
        if(status):
            self.inc += 1
            cords,label,conf = self.yolo.detect(img)
            if(len(cords) == 10):
                # cv2.imshow("plate",img)
                # print(cords)
                # print(np.array(cords))
                cv2.imwrite("./data/img/detected/ok"+str(self.inc)+".jpg",img)
                labelOrder = np.argsort(np.array(cords)[:,0])
                label = list(label)
                tempLabel = [None]*10
                for i,at in enumerate(labelOrder):
    	            tempLabel[i] = label[at]
                label = ''.join(map(str,tempLabel))
                print(str(self.isValid(label))+"  "+label+"  accuracy: "+ str(sum(conf)/10))
                # cv2.waitKey()
                return cords,label,True
            else:
                cv2.imwrite("./data/img/detected/"+str(self.inc)+".jpg",img)
                return [],[],False

        else:
            return [],[],False

    def isValid(self,label):
        return True if self.all_states.__contains__(label[:2]) and self.plate_regex.match(label) else False


    def preprocess(self,img):
        if(self.ratioCheck(img)):
            img = self.scale_frame(img,500)
            img = self.bright(img)
            kernel = np.ones((3,3),np.uint8)
            img = cv2.dilate(img,kernel,iterations=1)
            # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

            edges = cv2.Canny(img,50,150,apertureSize = 3)
            lines = cv2.HoughLines(edges,1,np.pi/180,200)
            if(lines is not None):
                for rho,theta in lines[0]:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a*rho
                    y0 = b*rho
                    x1 = int(x0 + 1000*(-b))
                    y1 = int(y0 + 1000*(a))
                    x2 = int(x0 - 1000*(-b))
                    y2 = int(y0 - 1000*(a))

                    print("a {0},b {1},x0 {2},y0 {3}".format(str(a),str(b),str(x0),str(y0)))

                    rows,cols = img.shape[:2]
                    cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
                    cv2.imshow('before-rotated',img)
                    M = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
                    img = cv2.warpAffine(img,M,(cols,rows))
                    #y = mx+b
                    print("slop: "+str((y2-y1)/(x2-x1))+"  theta:"+str(theta))
                    cv2.imshow('rotated',img)

            return True,img
        else:
            print("Ratio not matched")
            return False,img

    def scale_frame(self,frame,scale_percent):
        frame = self.gray(frame)
        _,frame = cv2.threshold(frame,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        frame = cv2.adaptiveThreshold(frame,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,7,2)

        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        # resize image
        result = cv2.resize(frame, dim, interpolation = cv2.INTER_LINEAR) 
        return cv2.merge((result,result,result))

    def gray(self,frame):
        return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    def bright(self,img):
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        img =cv2.equalizeHist(img)
        img = cv2.medianBlur(img,7)
        # cv2.imshow("bright",img)
        return cv2.merge((img,img,img))
        
    def ratioCheck(self,img):
        height, width,_ = img.shape
        if(width > height):
            return True
        else:
            return False

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