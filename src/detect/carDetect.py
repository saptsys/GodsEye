import cv2
from pathlib import Path
class CarDetect():
    def __init__(self):
        print("car")
        cascadePath =  str(Path(__file__).parent.parent / 'cascades/car.xml')
        print(cascadePath)
        self.carCascade = cv2.CascadeClassifier("D:\opencv\cascade\car.xml")

    def getCords(self,frame):
        frame = self.gray(frame)
        print(self.carCascade.empty())
        coords = self.carCascade.detectMultiScale(frame,1.1,4)
        return coords

    def drawCords(self,frame,coords):
        for x,y,h,w in coords:
            cv2.rectangle(frame,(x,y,h,w),(255,255,0),2)
        return frame
    
    def gray(self,frame):
        return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)