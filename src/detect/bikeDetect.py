import cv2
from pathlib import Path

class BikeDetect():
    def __init__(self):
        print("bike")
        cascadePath =  str(Path(__file__).parent.parent / 'cascades/bike.xml')
        self.bikeCascade = cv2.CascadeClassifier(cascadePath)


    def getCords(self,frame):
        coords = self.bikeCascade.detectMultiScale(frame,1.1,4)
        return coords

    def drawCords(self,frame,coords):
        for x,y,h,w in coords:
            cv2.rectangle(frame,(x,y,h,w),(0,0,255),2)
        return frame