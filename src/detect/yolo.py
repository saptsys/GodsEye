import cv2
import numpy as np

class Yolo():
    def __init__(self,confThreshold=0.7,nmsThreshold=0.7,inpWidth=416,inpHeight=416,detectType="vehicle"):
        # Initialize the parameters
        self.confThreshold =  confThreshold #Confidence threshold
        self.nmsThreshold = nmsThreshold  #Non-maximum suppression threshold
        self.inpWidth =   inpWidth     #Width of network's input image
        self.inpHeight =  inpHeight    #Height of network's input image
        self.detectType = detectType

    def ConfModel(self,coco,cfg,weights):
        # Give the configuration and weight files for the model and load the network using them.
        classesFile = coco;
        self.classes = None
        with open(classesFile, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')

        self.modelConfiguration = cfg
        self.modelWeights = weights
        self.net = cv2.dnn.readNetFromDarknet(self.modelConfiguration, self.modelWeights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    
    # Get the names of the output layers
    def getOutputsNames(self,net):
        # Get the names of all the layers in the network
        layersNames = net.getLayerNames()
        # Get the names of the output layers, i.e. the layers with unconnected outputs
        return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    # Draw the predicted bounding box
    def drawPred(self,frame,classId, conf, left, top, right, bottom):
        # Draw a bounding box.
        # cv2.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)
        # label = '%.2f' % conf
        
        # # Get the label for the class name and its confidence
        # if self.classes:
        #     label = '%s:%s' % (self.classes[classId], label)
        #     assert(classId < len(self.classes))
        classes = self.classes[classId]
        #Display the label at the top of the bounding box
        # labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        # top = max(top, labelSize[1])
        # cv2.rectangle(frame, (left, top - round(1.5*labelSize[1])), (left + round(1.5*labelSize[0]), top + baseLine), (255, 255, 255), cv2.FILLED)
        # cv2.putText(frame, label, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 1)
        # cv2.imshow("god",frame)
        if(self.detectType == "vehicle"):
            return [ left, top, right, bottom ] , classes
        elif(self.detectType == "ocr"):
            return [ left-10, top-10, right+10, bottom+10 ] , classes
        else:
            return [ left, top, right, bottom ] , classes
        
    # Remove the bounding boxes with low confidence using non-maxima suppression
    def postprocess(self,frame, outs):
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]

        classIds = []
        confidences = []
        boxes = []
        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        classIds = []
        confidences = []
        boxes = []
        cords = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if confidence > self.confThreshold:
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        # Perform non maximum suppression to eliminate redundant overlapping boxes with
        # lower confidences.
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confThreshold, self.nmsThreshold)
        preds = ""
        for i in indices:
            i = i[0]
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            cord,pred = self.drawPred(frame,classIds[i], confidences[i], left, top, left + width, top + height)
            cords.append(cord)
            preds = preds + pred
        # print(preds)
        return cords,preds
    
    def detect(self,frame):
        # Create a 4D blob from a frame.
        blob = cv2.dnn.blobFromImage(frame, 1/255, (self.inpWidth, self.inpHeight), [0,0,0], 1, crop=False)

        # Sets the input to the network
        self.net.setInput(blob)

        # Runs the forward pass to get output of the output layers
        outs = self.net.forward(self.getOutputsNames(self.net))

        # Remove the bounding boxes with low confidence
        cords,pred = self.postprocess(frame, outs)
        # Put efficiency information. The function getPerfProfile returns the overall time for inference(t) and the timings for each of the layers(in layersTimes)
        # t, _ = self.net.getPerfProfile()
        # label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
        # cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
        return cords,pred