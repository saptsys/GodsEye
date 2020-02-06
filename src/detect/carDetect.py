import cv2
from pathlib import Path
from detect.plateDetect import PlateDetect
from detect.PlateOCR import PlateOCR
from detect.yolo import Yolo
import numpy as np
class CarDetect():
    def __init__(self):
        # cascadePath =  str(Path(__file__).parent.parent / 'cascades/car.xml')
        # self.carCascade = cv2.CascadeClassifier(cascadePath)
        self.plateDetect = PlateDetect()
        self.inc = 1
        self.yolo = Yolo(confThreshold=0.7,nmsThreshold=0.7,inpWidth=416,inpHeight=416,detectType="vehicle")
        self.yolo.ConfModel(
                coco="./data/yolo/vehicle/vehicle.names",
                cfg="./data/yolo/vehicle/vehicle.cfg",
                weights="./data/yolo/vehicle/vehicle60000.weights")
        self.ocr = PlateOCR()


    def getCords(self,frame):
        # p1 = cv2.getTrackbarPos('p1','parameters')
        # p2 = cv2.getTrackbarPos('p2','parameters')
        # p3 = cv2.getTrackbarPos('p3','parameters')

        # p = float(str(p1)+'.'+str(p2))
        # cords = self.carCascade.detectMultiScale(frame,5.1,2)
        cords,pred = self.yolo.detect(frame)
        # print(pred)
        return cords

    def drawCords(self,frame,cords):
        # print(np.shape(cords))
        for x,y,h,w in cords:
            cv2.rectangle(frame,(x,y),(h,w),(255,0,0),2)
        return frame
        
    def drawPlateCords(self,frame,carCords,cords):
        if(len(cords)!=0):
            for x,y,h,w in cords[0]:
                cv2.rectangle(frame,(x,y),(h,w),(255,0,0),2)
        return frame
    
    def detectNumberPlate(self,roi,cords):
        plateCords,pred = self.plateDetect.detect(roi)
        # plateCords = []
        # for x,y,h,w in cords:
        #     car = frame[y:w,x:h]
        #     plate = self.plateDetect.detect(car)

        #     if(len(plate) != 0):
        #         plateCords.append(plate)
        #         # print(np.shape(plateCords))
        #         # print(np.array(plateCords))
        #         px,py,ph,pw = plate[0]
        #         plate = frame[py:pw,px:ph]
        #         cv2.imwrite("./data/detected/plate"+str(self.inc)+".jpg",plate)
        #         # cv2.imshow("plate",plate)
        #         print("plate Detected!!")
        #         self.inc += 1
        # px,py,ph,pw = plateCords[0]
        # plate = roi[py:pw,px:ph]
        return plateCords
    # def cleanImage

    def plateOCR(self,frame,plates):
        for x,y,h,w in plates:
            plate = frame[y:w,x:h]
            cords,pred,status = self.ocr.detect(plate)
            if(status):
                # print(pred)
                pass
        pass
