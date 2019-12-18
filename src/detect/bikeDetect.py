import cv2
class BikeDetect():
    def __init__(self):
        print("bike")
    
    def getCords(self,frame):
        return [[10,20,30,40]]

    def drawCords(self,frame,coords):
        for x,y,h,w in coords:
            cv2.rectangle(frame,(x,y,h,w),(255,255,0),2)
        return frame