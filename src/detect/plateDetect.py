
import numpy as np
import cv2
from detect.yolo import Yolo
# from copy import deepcopy
# from PIL import Image
# import pytesseract as tess

class PlateDetect():
    def __init__(self):
        # tess.pytesseract.tesseract_cmd = "J:/Program Files/Tesseract-OCR/tesseract.exe"
        self.yolo = Yolo(confThreshold=0.5,nmsThreshold=0.4,inpWidth=416,inpHeight=416,detectType="plate")
        self.yolo.ConfModel(coco="./data/yolo/plate/plate.names",cfg="./data/yolo/plate/plate.cfg",weights="./data/yolo/plate/plate.weights")

    def detect(self,img):
        cords = self.yolo.detect(img)
        return cords
        # #img = cv2.imread("testData/Final.JPG")
        # threshold_img = self.preprocess(img)
        # contours= self.extract_contours(threshold_img)

        # #if len(contours)!=0:
        #     #print len(contours) #Test
        #     # cv2.drawContours(img, contours, -1, (0,255,0), 1)
        #     # cv2.imshow("Contours",img)
        #     # cv2.waitKey(0)
        # self.cleanAndRead(img,contours)
        # cv2.waitKey(0)

    # def ratioCheck(area, width, height):

    #     ratio = float(width) / float(height)
    #     if ratio < 1:
    #         ratio = 1 / ratio

    #     aspect = 4.7272
    #     min = 15*aspect*15  # minimum area
    #     max = 125*aspect*125  # maximum area

    #     rmin = 3
    #     rmax = 6

    #     if (area < min or area > max) or (ratio < rmin or ratio > rmax):
    #         return False
    #     return True

    # def isMaxWhite(plate):
    #     avg = np.mean(plate)
    #     if(avg>=115):
    #         return True
    #     else:
    #         return False

    # def validateRotationAndRatio(rect):
    #     if(1==1):
    #             return True
    #     (x, y), (width, height), rect_angle = rect

    #     if(width>height):
    #         angle = -rect_angle
    #     else:
    #         angle = 90 + rect_angle

    #     if angle>15:
    #         return False

    #     if height == 0 or width == 0:
    #         return False

    #     area = height*width
    #     if not ratioCheck(area,width,height):
    #         return False
    #     else:
    #         return True