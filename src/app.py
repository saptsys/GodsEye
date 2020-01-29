import time
from pathlib import Path
import regionSelector

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
        self.__regionSelector = regionSelector(self.camera.read()[1])
        self.winName = 'GodsEye'
        cv2.namedWindow(self.winName, cv2.WINDOW_NORMAL)
                
    def run(self):
        fps = 0

        #run


        while 1:
            start_time = time.time()
            hasFrame,frame = self.camera.read()
            gray = cv2.resize(frame,(int(frame.shape[1]/resizeBy),int(frame.shape[0]/resizeBy)))
            # gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

            # carCords = self.carDetect.getCords(gray)
            # bikeCords = np.multiply(self.bikeDetect.getCords(gray), resizeBy)

            # frame = self.carDetect.drawCords(frame,carCords)
            plateCords = self.carDetect.fetchPlateNumber(frame,frame)
            # self.carDetect.drawCords(frame,plateCords)
            # frame = self.bikeDetect.drawCords(frame,bikeCords)

            frame = cv2.putText(frame,str(str(fps)+" fps"),(10,30),cv2.FONT_ITALIC,0.5,(255,255,0),1)
            # print(carCords)
            cv2.imshow('GodsEye',frame)

            # Stop the program if reached end of video
            if not hasFrame:
                print("Done processing !!!")
                cv.waitKey(3000)
                break

            if(cv2.waitKey(1) & 0xFF == ord('q')):
                break

            fps = int(1.0 / (time.time() - start_time))

        cv2.destroyAllWindows()
        self.camera.release()

    def gray(self,frame):
        return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    def __del__(self):
        pass
