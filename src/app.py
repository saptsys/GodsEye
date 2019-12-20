import cv2
import numpy as np
from detect.carDetect import CarDetect
from detect.bikeDetect import BikeDetect
from pathlib import Path
import imutils
import time

class App():
    def __init__(self,camera=0):
        print("k")
        self.carDetect = CarDetect()
        self.bikeDetect = BikeDetect()
        self.camera = cv2.VideoCapture(camera)
        self.run()
        
    def run(self):
        resizeBy = 1
        f = self.camera.read()[1]
        if((f.shape[0] > 500) or (f.shape[1] > 500) ):
            print("Resized")
            resizeBy = 2
            
        #run
        while 1:
            start_time = time.time()
            _,frame = self.camera.read()

            gray = cv2.resize(frame,(int(frame.shape[1]/resizeBy),int(frame.shape[0]/resizeBy)))

            carCords = np.multiply(self.carDetect.getCords(gray) , resizeBy)
            bikeCords = np.multiply(self.bikeDetect.getCords(gray), resizeBy)

            frame = self.carDetect.drawCords(frame,carCords)
            frame = self.bikeDetect.drawCords(frame,bikeCords)

            # print(carCords)
            cv2.imshow('frame',frame)

            if(cv2.waitKey(1) & 0xFF == ord('q')):
                break
            print("FPS: {0:.2f}".format(1.0 / (time.time() - start_time)) )

        cv2.destroyAllWindows()
        self.camera.release()

    def gray(self,frame):
        return cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

    def __del__(self):
        pass