# coding:utf-8

import cv2 as cv
import numpy as np
import os

YOLOV3_NET_CONFIG = 'data/yolov3.cfg'
YOLOV3_NET_WEIGHTS = 'data/yolov3.weights'
YOLOV3_NET_CLASSES = 'data/coco.names'
YOLOV3_NET_CONF_THRESHOULD = 0.5
YOLOV3_NET_NMS_THRESHOULD = 0.4
YOLOV3_NET_INPUT_WIDTH = 608
YOLOV3_NET_INPUT_HEIGHT = 608
PERSON_CLASSID = 0

HAT_DETECT_NET_CONFIG = 'data/darknet19.cfg'
HAT_DETECT_NET_WEIGHTS = 'data/darknet19.backup'
HAT_DETECT_NET_CLASSES = 'data/names.list'
HAT_DETECT_NET_CONF_THRESHOULD = 0.5
HAT_DETECT_NET_NMS_THRESHOULD = 0.4
HAT_DETECT_NET_INPUT_WIDTH = 256
HAT_DETECT_NET_INPUT_HEIGHT = 256

class HatDetector(object):

    # loading net data
    def __init__(self):

        # loading classes of yolov3
        with open(YOLOV3_NET_CLASSES, 'r') as file:
            self.__yolov3_classes = [line.strip() for line in file]

        # loading classes of hat detect net
        with open(HAT_DETECT_NET_CLASSES, 'r') as file:
            self.__hat_detect_net_classes = [line.strip() for line in file]

        # loading yolov3
        self.__yolov3 = cv.dnn.readNetFromDarknet(
            YOLOV3_NET_CONFIG,
            YOLOV3_NET_WEIGHTS
        )

        # loading hat detect net
        self.__hat_detect_net = cv.dnn.readNetFromDarknet(
            HAT_DETECT_NET_CONFIG,
            HAT_DETECT_NET_WEIGHTS
        )

        self.__yolov3.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        self.__yolov3.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)

        self.__hat_detect_net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        self.__hat_detect_net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)


    # Get the names of the output layers
    def __getOutputsNames(self, net):
        # Get the names of all the layers in the network
        layersNames = net.getLayerNames()
        # Get the names of the output layers, i.e. the layers with unconnected outputs
        return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    
    # Draw the predicted bounding box
    def __drawPred(self, personConf, hatLabel, hatConf, left, top, right, bottom, frame):
        # Draw a bounding box.
        cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)
        
        # label = '%.2f' % conf

        label = 'Person:%.2f %s:%.2f' % (personConf, hatLabel, hatConf)

        # Get the label for the class name and its confidence
        # if classes:
        #     assert(classId < len(classes))
        #     label = '%s:%s' % (classes[classId], label)

        # Display the label at the top of the bounding box
        labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(top, labelSize[1])
        cv.rectangle(
            frame,
            (left, top - round(1.5*labelSize[1])),
            (left + round(1.5*labelSize[0]), top + baseLine),
            (255, 255, 255),
            cv.FILLED
        )
        cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 1)

    # Remove the bounding boxes with low confidence using non-maxima suppression
    def __postprocess(self, frame, outs):
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]

        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        classIds = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = np.argmax(scores)
                # we only needs person
                if not classId == PERSON_CLASSID:
                    continue
                confidence = scores[classId]
                if confidence > YOLOV3_NET_CONF_THRESHOULD:
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
        indices = cv.dnn.NMSBoxes(
            boxes,
            confidences,
            YOLOV3_NET_CONF_THRESHOULD,
            YOLOV3_NET_NMS_THRESHOULD
        )
        for i in indices:
            i = i[0]
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            self.__drawPred(
                classIds[i],
                self.__yolov3_classes,
                confidences[i],
                left,
                top,
                left + width,
                top + height,
                frame
            )
    
    # Remove the bounding boxes with low confidence using non-maxima suppression
    # get person
    def __getPerson(self, frame, outs):
        frameHeight = frame.shape[0]
        frameWidth = frame.shape[1]

        # Scan through all the bounding boxes output from the network and keep only the
        # ones with high confidence scores. Assign the box's class label as the class with the highest score.
        classIds = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = np.argmax(scores)

                # we only needs person
                if not classId == PERSON_CLASSID:
                    continue

                confidence = scores[classId]
                if confidence > YOLOV3_NET_CONF_THRESHOULD:
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    if left < 0: left = 0
                    if top < 0: top = 0
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        # Perform non maximum suppression to eliminate redundant overlapping boxes with
        # lower confidences.
        indices = cv.dnn.NMSBoxes(
            boxes,
            confidences,
            YOLOV3_NET_CONF_THRESHOULD,
            YOLOV3_NET_NMS_THRESHOULD
        )
        return [indices, boxes, confidences]

    # get hat
    def __getHat(self, frame, outs):
        out = outs[0]
        detection = out[0]
        noHat = detection[0][0][0]
        withHat = detection[1][0][0]
        if noHat > withHat:
            return [self.__hat_detect_net_classes[0], noHat]
        else:
            return [self.__hat_detect_net_classes[1], withHat]

    
    def __detectSingleFrame(self, frame):
        # Create a 4D blob from a frame.
        blob_person = cv.dnn.blobFromImage(
            frame,
            1/255,
            (YOLOV3_NET_INPUT_WIDTH, YOLOV3_NET_INPUT_HEIGHT),
            [0,0,0],
            1,
            crop=False
        )

        # use yolov3 search person

        # Sets the input to the network
        self.__yolov3.setInput(blob_person)

        # Runs the forward pass to get output of the output layers
        outs_person = self.__yolov3.forward(
            self.__getOutputsNames(self.__yolov3)
        )

        # Remove the bounding boxes with low confidence
        # get person
        personId, personInfo, personConf = self.__getPerson(frame, outs_person)

        # detect hat
        for i in personId:
            i = i[0]
            box = personInfo[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]

            # print(personInfo[i])

            # use darknet19 detect security hat

            # cv.imshow('test',frame[top:top+int(height/2), left:left+width])

            # Create a 4D blob from a person img.
            blob_hat = cv.dnn.blobFromImage(
                frame[top:top+int(height/2), left:left+width],
                1/255,
                (HAT_DETECT_NET_INPUT_WIDTH, HAT_DETECT_NET_INPUT_HEIGHT),
                [0,0,0],
                1,
                crop=False
            )


            # Sets the input to the network
            self.__hat_detect_net.setInput(blob_hat)
            
            # Runs the forward pass to get output of the output layers
            outs_hat = self.__hat_detect_net.forward(
                self.__getOutputsNames(self.__hat_detect_net)
            )

            hatLabel, hatConf = self.__getHat(frame, outs_hat)

            # draw info
            self.__drawPred(
                personConf[i],
                hatLabel,
                hatConf,
                left,
                top,
                left + width,
                top + int(height/2),
                frame
            )

        # Put efficiency information. The function getPerfProfile returns the overall time for inference(t) and the timings for each of the layers(in layersTimes)
        # t, _ = self.__yolov3.getPerfProfile()
        # label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
        # cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))



    def detectImageFile(self, path, outputPath=0):
        # check if the file exeist
        if not os.path.isfile(path):
            print("Input image file ", path, " doesn't exist")

        # open file
        cap = cv.VideoCapture(path)

        # process file
        while cv.waitKey(1) < 0:
            # get frame from the video
            hasFrame, frame = cap.read()

            # Stop the program if reached end of video
            if not hasFrame:
                print("Done processing !!!")
                cv.waitKey(3000)
                # Release device
                cap.release()
                break

            self.__detectSingleFrame(frame)
            
            if outputPath:
                cv.imwrite(outputPath, frame.astype(np.uint8))


            cv.imshow('test', frame)
    

    def detectVedioFile(self, path, outputPath=0):
        # check if the file exeist
        if not os.path.isfile(path):
            print("Input image file ", path, " doesn't exist")

        # open file
        cap = cv.VideoCapture(path)

        # get total frame number
        total_frame = cap.get(7)

        fps = cap.get(5)

        # init vedio writer
        vid_writer = cv.VideoWriter(
            outputPath,
            cv.VideoWriter_fourcc('H', '2', '6', '4'),
            fps,
            (
                round(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
                round(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
            )
        )

        # process file
        done_frame = 0

        while cv.waitKey(1) < 0:
            # get frame from the video
            hasFrame, frame = cap.read()

            # Stop the program if reached end of video
            if not hasFrame:
                print("Done processing !!!")
                cv.waitKey(3000)
                # Release device
                cap.release()
                break

            self.__detectSingleFrame(frame)

            vid_writer.write(frame.astype(np.uint8))

            done_frame += 1

            print('[%.2f] %d of %d frame has done!' % (done_frame/total_frame*100, done_frame, total_frame), end='\r')
            
            # if outputPath:
            #     cv.imwrite(outputPath, frame.astype(np.uint8))


            # cv.imshow('test', frame)

# for test
if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    hatDetector = HatDetector()
    # hatDetector.detectImageFile('./testFile/test_img_3.jpg', './testFile/test_img_3_result.jpg')
    hatDetector.detectVedioFile('./testFile/test_vedio.mp4', './testFile/test_vedio_result.avi')
