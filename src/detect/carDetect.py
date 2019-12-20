import cv2
from pathlib import Path
class CarDetect():
    def __init__(self):
        print("car")
        cascadePath =  str(Path(__file__).parent.parent / 'cascades/car.xml')
        self.carCascade = cv2.CascadeClassifier(cascadePath)


    def getCords(self,frame):
        coords = self.carCascade.detectMultiScale(frame,1.1,9)
        return coords

    def drawCords(self,frame,coords):
        for x,y,h,w in coords:
            cv2.rectangle(frame,(x,y,h,w),(255,0,0),2)
        return frame