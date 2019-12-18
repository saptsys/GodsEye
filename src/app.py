import cv2
import numpy as np
from detect.carDetect import CarDetect
from detect.bikeDetect import BikeDetect
class App():
    def __init__(self,camera=0):
        print("k")
        self.carDetect = CarDetect()
        self.bikeDetect = BikeDetect()
        self.camera = cv2.VideoCapture(camera)
        self.run()

    def run(self):       
        while 1:
            _,frame = self.camera.read()

            carCoords = self.carDetect.getCords(frame)
            bikeCoords = self.bikeDetect.getCords(frame)
            frame = self.carDetect.drawCords(frame,carCoords)
            frame = self.bikeDetect.drawCords(frame,bikeCoords)

            cv2.imshow('frame',frame)

            if(cv2.waitKey(1) & 0xFF == ord('q')):
                break

        cv2.destroyAllWindows()
        self.camera.release()

    def __del__(self):
        pass