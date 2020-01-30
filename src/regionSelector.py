import cv2
import numpy as np 

class RegionSelector():
    def __init__(self,frame,title='Select Region'):
        self.__frame = frame # = cv2.resize(frame, (960, 540))   
        self.__title = title
        self.__height = frame.shape[0]
        self.__width = frame.shape[1]
        self.__cord_x1 = 20
        self.__cord_x2 = self.__width-22
        self.__paddings = 50
        self.__instruction = 'hello how r u'
        cv2.namedWindow(self.__title)
        cv2.setMouseCallback(self.__title,self.__mouseCallBack)
        pass
    
    def select_region(self):
        self.__isRegionSelected = False
        cv2.imshow(self.__title,self.__frame)
        cv2.waitKey()
        if not self.__isRegionSelected:
            self.__cord_x1 = 0
            self.__cord_x2 = self.__width
        cv2.destroyWindow(self.__title)

    def __mouseCallBack(self,event,cord_x,cord_y,flags,parameters):
        local_frame = None
        if event == cv2.EVENT_MOUSEMOVE and not self.__isRegionSelected:
            local_frame = self.__drawLines(cord_x,cord_y)
        elif event == cv2.EVENT_MOUSEWHEEL and not self.__isRegionSelected:
            if flags > 0:
                if self.__width > (self.__paddings*2):
                    self.__paddings += 5
            else:
                if self.__paddings >= 50:
                    self.__paddings -= 5
            local_frame = self.__drawLines(cord_x,cord_y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.__isRegionSelected = True
        elif event == cv2.EVENT_LBUTTONDOWN and self.__isRegionSelected:
            cv2.destroyWindow(self.__title)
        elif event == cv2.EVENT_RBUTTONUP:
            self.__isRegionSelected = False


        if local_frame is not None:
            # local_frame = self.__makeText(local_frame,'* single click to select, click again to confirm & close, mouse wheel to expand or shrink lines')
            cv2.imshow(self.__title,local_frame)
        pass

    def __drawLines(self,cord_x,cord_y):

        if cord_x-self.__paddings > 0:
            self.__cord_x2 = cord_x+(self.__paddings)
        if cord_x+self.__paddings < self.__width-1:
            self.__cord_x1 = cord_x-(self.__paddings)
        
        if self.__cord_x1 <= 0 :
            self.__cord_x1 = 0
        if self.__cord_x2 >= self.__width:
            self.__cord_x2 = self.__width-1

        #drawing lines
        local_frame = cv2.line(self.__frame.copy(),(self.__cord_x1,1),(self.__cord_x1,self.__height),(255,255,255),2)
        local_frame = cv2.line(local_frame,(self.__cord_x2,1),(self.__cord_x2,self.__height),(255,255,255),2)
        
        #making blur
        local_frame[:,0:self.__cord_x1+1] = cv2.GaussianBlur(local_frame[:,0:self.__cord_x1+1],(5,5),10000)
        local_frame[:,self.__cord_x2:self.__width] = cv2.GaussianBlur(local_frame[:,self.__cord_x2:self.__width],(5,5),10000)
        # local_frame[:,0:self.__cord_x1+1] = np.random.randint(0,255,(self.__height,self.__cord_x1+1,3))
        # local_frame[:,self.__cord_x2-1:self.__width] = np.random.randint(0,255,(self.__height,self.__width-self.__cord_x2+1,3))
        
        return local_frame

    def getROI(self,local_frame):
        return local_frame[:,self.__cord_x1:self.__cord_x2]

    def undoROI(self,orignal_frame,roi_frame):
        orignal_frame[:,self.__cord_x1:self.__cord_x2] = roi_frame
        return orignal_frame

# if __name__ == "__main__":
#     frame = cv2.imread('data/img/car1.jpg')
#     selection = RegionSelector(frame)
#     selection.select_region()
#     cv2.imshow('roi',selection.getROI(frame))
#     cv2.imshow('undo roi',selection.undoROI(frame,selection.getROI(frame)))
#     cv2.waitKey()
#     cv2.destroyAllWindows()

