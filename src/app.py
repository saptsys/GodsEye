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
        print("k")
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
            # gray = cv2.resize(frame,(int(frame.shape[1]/resizeBy),int(frame.shape[0]/resizeBy)))
            # gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            carCords = self.carDetect.getCords(roi)
            # bikeCords = np.multiply(self.bikeDetect.getCords(gray), resizeBy)

            frame = self.carDetect.drawCords(roi,carCords)
            # plateCords = self.carDetect.fetchPlateNumber(roi,frame)
            # self.carDetect.drawCords(frame,plateCords)
            # frame = self.bikeDetect.drawCords(frame,bikeCords)

            frame = cv2.putText(roi,str(str(fps)+" fps"),(10,30),cv2.FONT_ITALIC,0.5,(255,255,0),1)
            # print(carCords)
            cv2.imshow('GodsEye',self.__regionSelector.undoROI(orignal_frame,roi))

            # Stop the program if reached end of video
            if not hasFrame:
                print("Done processing !!!")
                cv.waitKey(3000)
                break

            # if(cv2.waitKey(1) & 0xFF == ord('q')):
            #     break

            fps = int(1.0 / (time.time() - start_time))

        cv2.destroyAllWindows()
        self.camera.release()

    def gray(self,frame):
        return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    def __del__(self):
        pass
