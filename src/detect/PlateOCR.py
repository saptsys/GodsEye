
import cv2
import numpy as np
from detect.yolo import Yolo
import re
import math
from scipy import ndimage
    
class PlateOCR():
    def __init__(self):
        self.plate_regex = re.compile(r'^[A-Z]{2}[0-9]{1,2}(?:[A-Z])?(?:[A-Z]*)?[0-9]{4}$')
        self.all_states = ['AP', 'AR', 'AS', 'BR', 'CG', 'GA', 'GJ', 'HR', 'HP', 'JK', 'JH', 'KA', 'KL', 'MP', 'MH', 'MN', 'ML', 'MZ', 'NL', 'OR', 'PB', 'RJ', 'SK', 'TN', 'TR', 'UK', 'UP', 'WB', 'TS', 'AN', 'CH', 'DH', 'DD', 'DL', 'LD', 'PY']
        self.inc = 0
        self.yolo = Yolo(confThreshold=0.75,nmsThreshold=0.8,inpWidth=200,inpHeight=200,detectType="ocr")
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
                # cv2.imwrite("./data/img/detected/ok"+str(self.inc)+".jpg",img)
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
                # print("<10")
                # cv2.imwrite("./data/img/detected/"+str(self.inc)+".jpg",img)
                return [],[],False

        else:
            return [],[],False

    def isValid(self,label):
        return True if self.all_states.__contains__(label[:2]) and self.plate_regex.match(label) else False


    def preprocess(self,img):
        if(self.ratioCheck(img)):
            img = self.gray(img)
            img = self.scale_frame(img,500)
            img = self.bright(img)

            # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            
            img = self.rotate(img)

            # cv2.imshow("noisy",img)  
            # img = self.removeNoise(img,thickness=8,rangePercentage=1,medianThreshold=50)


            # contours, hierarchy = cv2.findContours(self.gray(cv2.bitwise_not(img)),cv2.RETR_EXTERNAL ,cv2.CHAIN_APPROX_SIMPLE)
            # cv2.drawContours(img,contours,-1,(0,255,0),3)
            # mask = np.ones(img.shape[:2], dtype="uint8") * 255
            # for c in contours:
            #     if self.is_contour_bad(c):
            #         cv2.drawContours(mask, [c], -1, 0, -1)
            # img = cv2.bitwise_and(img, img, mask=mask)
            # cv2.imshow("Mask", mask)

            cv2.imshow('post-proces',img)
            return True,img
        else:
            print("Ratio not matched")
            return False,img

    def is_contour_bad(self,c):
        	# approximate the contour
        peri = cv2.arcLength(c, True)
        return peri < 500
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # the contour is 'bad' if it is not a rectangle
        return len(approx) == 4

    def rotate(self,img):
        edges = cv2.Canny(img,50,150,apertureSize = 3)
        lines = cv2.HoughLines(edges,1,np.pi/180,200)
        if(lines is not None):
            angles = []
            for rho,theta in lines[0]:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
                angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                angles.append(angle)
                cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
            angle = np.mean(angles)            
            img = ndimage.rotate(img, angle,cval=255)
        return img

    def removeNoise(self,img,thickness=5,rangePercentage=0.2,medianThreshold=255):
        img = self.gray(img)
        Iterator = 0
        top_end = int((img.shape[0] * rangePercentage))
        bottom_start = int( (img.shape[0] * ( -(rangePercentage-1)) ) )
        for i,position in enumerate([[0,top_end],[bottom_start,img.shape[0]]]):
            imgc = img.copy()
            imgc = imgc[position[0]:position[1],:]
            rows = imgc.shape[0]
            while True:
                if(Iterator >= rows):
                    break
                
                median = imgc[Iterator:Iterator+thickness,:].mean()
                if(median <= medianThreshold):
                    img[Iterator+position[0]:Iterator+thickness+position[0],:] = 255
                Iterator += thickness
            Iterator = 0    
        return self.gray(img,True)

    def scale_frame(self,frame,scale_percent):
        _,frame = cv2.threshold(frame,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        frame = cv2.adaptiveThreshold(frame,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,7,2)

        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        img = cv2.resize(frame, dim, interpolation = cv2.INTER_LINEAR) 
        return self.gray(img,True)

    def gray(self,frame,reverse=False):
        if(reverse):
            return cv2.merge((frame,frame,frame))
        return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    def bright(self,img):
        img = self.gray(img)
        img = cv2.equalizeHist(img)
        img = cv2.medianBlur(img,5)
        kernel = np.ones((3,3),np.uint8)
        img = cv2.dilate(img,kernel,iterations=1)
        return self.gray(img,True)
        
    def ratioCheck(self,img):
        height, width,_ = img.shape
        if(width > height):
            return True
        else:
            return False
