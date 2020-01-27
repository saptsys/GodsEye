import cv2
from pathlib import Path
from detect.plateDetect import PlateDetect
from detect.yolo import Yolo

class CarDetect():
    def __init__(self):
        print("car")
        # cascadePath =  str(Path(__file__).parent.parent / 'cascades/car.xml')
        # self.carCascade = cv2.CascadeClassifier(cascadePath)
        self.plateDetect = PlateDetect()
        self.inc = 1
        self.yolo = Yolo(confThreshold=0.7,nmsThreshold=0.7,inpWidth=416,inpHeight=416,detectType="vehicle")
        self.yolo.ConfModel(coco="./data/yolo/vehicle/coco.names",cfg="./data/yolo/vehicle/yolov3-tiny.cfg",weights="./data/yolo/vehicle/yolov3-tiny_30000.weights")


    def getCords(self,frame):
        # p1 = cv2.getTrackbarPos('p1','parameters')
        # p2 = cv2.getTrackbarPos('p2','parameters')
        # p3 = cv2.getTrackbarPos('p3','parameters')

        # p = float(str(p1)+'.'+str(p2))
        # cords = self.carCascade.detectMultiScale(frame,5.1,2)
        cords = self.yolo.detect(frame)
        return cords

    def drawCords(self,frame,cords):
        for x,y,h,w in cords:
            cv2.rectangle(frame,(x,y),(h,w),(255,0,0),2)
        return frame
        
    
    def fetchPlateNumber(self,frame,cords):
        for x,y,h,w in cords:
            car = frame[y:w,x:h]
            plateCords = self.plateDetect.detect(car)
            if(len(plateCords) == 4):
                px,py,ph,pw = plateCords
                plate = car[py:pw,px:ph]
                cv2.imwrite("../detected/plate"+str(inc)+".jpg",plate)
                cv2.imshow("plate",cords)
        # return frame
        pass
        


    

    # def cleanImage