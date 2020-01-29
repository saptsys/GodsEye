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
        self.yolo.ConfModel(
                coco="./data/yolo/vehicle/vehicle.names",
                cfg="./data/yolo/vehicle/vehicle.cfg",
                weights="./data/yolo/vehicle/vehicle60000.weights")


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
        plateCords = self.plateDetect.detect(frame)
        if(plateCords):
            self.drawCords(frame,plateCords)
            px,py,ph,pw = plateCords[0]
            plate = frame[py:pw,px:ph]
            cv2.imwrite("../detected/plate"+str(self.inc)+".jpg",plate)
            cv2.imshow("plate",plate)
            print("plate Detected!!")
            self.inc += 1
            return plate
        # plateCords = []
        # for x,y,h,w in cords:
        #     car = frame[y:w,x:h]
        #     plateCords = self.plateDetect.detect(frame)
        #     if(plateCords):
        #         self.drawCords(frame,plateCords)
        #         px,py,ph,pw = plateCords[0]
        #         plate = frame[py:pw,px:ph]
        #         cv2.imwrite("../detected/plate"+str(self.inc)+".jpg",plate)
        #         cv2.imshow("plate",plate)
        #         print("plate Detected!!")
        #         self.inc += 1
        #         return plate
        # return plateCords


    

    # def cleanImage