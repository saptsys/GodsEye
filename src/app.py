import time
from pathlib import Path
from regionSelector import RegionSelector
from database import Database
from CrawlData import CrawlData
from multiprocessing import Process
import sys, os, traceback, types

import cv2
import imutils
import numpy as np
import sqlite3

# from detect.bikeDetect import BikeDetect
from detect.carDetect import CarDetect

def nothing(x):
    pass

class App():
    def __init__(self,settings):
        self.settings = settings
        self.carDetect = CarDetect()
        # self.bikeDetect = BikeDetect()
        print(settings['source'])
        self.camera = cv2.VideoCapture(settings['source'])
        self.winName = settings['windowName']
        # self.database = Database(settings['dataBase'])
        self.crawlData = CrawlData(settings)

        if( not os.path.isdir(settings["storage"])):
            os.mkdir(settings["storage"])
        if( not os.path.isdir(settings["storage"]+"\\images")):
            os.mkdir(settings["storage"]+"\\images")

        self.__regionSelector = RegionSelector(self.camera.read()[1],self.winName)
        cv2.namedWindow(self.winName, cv2.WINDOW_NORMAL)
                
    def run(self):
        processes = []
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
            
            plts = self.carDetect.plateOCR(frame,plateCords)
            # self.database.insertPlates(plts)
            if len(plts) > 0:
                plts[0][1] = frame
                proc = Process(target=self.crawlData.fetch,args=(plts[0],))
                processes.append(proc)
                proc.start()
            self.carDetect.drawCords(frame,plateCords)

            frame = cv2.putText(roi,str(str(fps)+" fps"),(10,30),cv2.FONT_ITALIC,0.5,(255,255,0),1)
            cv2.imshow('GodsEye',self.__regionSelector.undoROI(orignal_frame,roi))

            # Stop the program if reached end of video
            if not hasFrame:
                print("Done processing !!!")
                cv2.waitKey(3000)
                break

            fps = int(1.0 / (time.time() - start_time))

        n = len(processes)
        for proc in processes:
            frame = cv2.putText(np.zeros((50,500,3))," Please wait, Let us finish all crawling processes("+str(n)+")",(10,30),cv2.FONT_ITALIC,0.5,(255,255,255),1)
            cv2.imshow('GodsEye',frame)
            cv2.waitKey(1)
            n-=1   
            proc.join()

        frame = cv2.putText(np.zeros((50,500,3)),"Thank You, Good Bye",(10,30),cv2.FONT_ITALIC,0.5,(255,255,255),1)
        cv2.imshow('GodsEye',frame)  
        cv2.waitKey(3000)
        cv2.destroyAllWindows()
        self.camera.release()

    def __del__(self):
        pass
