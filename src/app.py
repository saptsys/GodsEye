import time
from pathlib import Path
from regionSelector import RegionSelector

import cv2
import imutils
import numpy as np

# from detect.bikeDetect import BikeDetect
from detect.carDetect import CarDetect

def nothing(x):
    pass

class App():
    def __init__(self,camera=0):
        self.carDetect = CarDetect()
        # self.bikeDetect = BikeDetect()
        self.camera = cv2.VideoCapture(camera)
        self.winName = 'GodsEye'
        self.__regionSelector = RegionSelector(self.camera.read()[1],self.winName)
        cv2.namedWindow(self.winName, cv2.WINDOW_NORMAL)
                
    def run(self):
        self.__regionSelector.select_region()
        fps = 0
        #run
        while cv2.waitKey(1) != 27:
            start_time = time.time()
            hasFrame,frame = self.camera.read()
            orignal_frame = frame.copy()
            roi = self.__regionSelector.getROI(frame)

            # carCords = self.carDetect.getCords(roi)
            # frame = self.carDetect.drawCords(roi,carCords)

            plateCords = self.carDetect.detectNumberPlate(roi,frame)
            
            self.carDetect.plateOCR(frame,plateCords)
            self.carDetect.drawCords(frame,plateCords)

            frame = cv2.putText(roi,str(str(fps)+" fps"),(10,30),cv2.FONT_ITALIC,0.5,(255,255,0),1)
            cv2.imshow('GodsEye',self.__regionSelector.undoROI(orignal_frame,roi))

            # Stop the program if reached end of video
            if not hasFrame:
                print("Done processing !!!")
                cv.waitKey(3000)
                break

            fps = int(1.0 / (time.time() - start_time))

        cv2.destroyAllWindows()
        self.camera.release()


    def __del__(self):
        pass
