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

PERSON_ID = 0
PERSON_INFO = 1
PERSON_CONF = 2
HAT_LABEL = 3
HAT_CONF = 4

class HatDetector(object):

    DETECT_PERSON_BY_NET = 0
    DETECT_PERSON_BY_HOGSVM = 1

    # init
    def __init__(self, person_detect_type=DETECT_PERSON_BY_NET):

        self.__person_detect_type = person_detect_type

        # init person detect function

        # if use net
        if self.__person_detect_type == self.DETECT_PERSON_BY_NET:
            self.__load_yolov3()
        # if use hog
        elif self.__person_detect_type == self.DETECT_PERSON_BY_HOGSVM:
            self.__load_hog()
        # if param wrong
        else:
            raise Exception('person_detect_type_err')

        # init hat detect net
        self.__load_hat_detect_net()


    def __load_yolov3(self):
        # loading classes of yolov3
        with open(YOLOV3_NET_CLASSES, 'r') as file:
            self.__yolov3_classes = [line.strip() for line in file]
        
        # loading yolov3
        self.__yolov3 = cv.dnn.readNetFromDarknet(
            YOLOV3_NET_CONFIG,
            YOLOV3_NET_WEIGHTS
        )

        # def backend
        self.__yolov3.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        self.__yolov3.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)


    def __load_hog(self):
        self.__hog = cv.HOGDescriptor()
        self.__hog.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())


    def __load_hat_detect_net(self):
        # loading classes of hat detect net
        with open(HAT_DETECT_NET_CLASSES, 'r') as file:
            self.__hat_detect_net_classes = [line.strip() for line in file]
        
        # loading hat detect net
        self.__hat_detect_net = cv.dnn.readNetFromDarknet(
            HAT_DETECT_NET_CONFIG,
            HAT_DETECT_NET_WEIGHTS
        )

        # def backend
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
        if hatLabel == self.__hat_detect_net_classes[0]:
            cv.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 3)
        else:
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

    # Draw a frame
    def __drawFrame(self, frame, detect_result):
        # draw frame
        for i in detect_result[PERSON_ID]:
            box = detect_result[PERSON_INFO][i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            
            self.__drawPred(
                detect_result[PERSON_CONF][i],
                detect_result[HAT_LABEL][i],
                detect_result[HAT_CONF][i],
                left,
                top,
                left + width,
                top + height,
                frame
            )


    # Remove the bounding boxes with low confidence using non-maxima suppression
    # get person
    # for yolov3
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
                    height = int(height/2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append((left, top, width, height))

        # Perform non maximum suppression to eliminate redundant overlapping boxes with
        # lower confidences.

        # print(confidences)

        indices = cv.dnn.NMSBoxes(
            boxes,
            confidences,
            YOLOV3_NET_CONF_THRESHOULD,
            YOLOV3_NET_NMS_THRESHOULD
        )

        personId = []
        personInfo = []
        personConf = []

        for i, personid in zip(indices, range(len(indices))):
            i = i[0]
            personId.append(personid)
            personInfo.append(boxes[i])
            personConf.append(confidences[i])

        return [personId, personInfo, personConf]

    # get hat
    # for hat detect net
    def __getHat(self, frame, outs):
        out = outs[0]
        detection = out[0]
        noHat = detection[0][0][0]
        withHat = detection[1][0][0]
        if noHat > withHat:
            return [self.__hat_detect_net_classes[0], noHat]
        else:
            return [self.__hat_detect_net_classes[1], withHat]


    # check inside
    # for hog svm
    def __checkInside(self, o, i):
        ox, oy, ow, oh = o
        ix, iy, iw, ih = i
        return ox <= ix and oy <= iy and ox+ow >= ix+iw and oy+oh >= iy+ih


    def __non_max_suppression_fast(self, boxes, overlapThresh=0.5):
        # if there are no boxes, return an empty list
        if len(boxes) == 0:
            return []

        # if the bounding boxes integers, convert them to floats --
        # this is important since we'll be doing a bunch of divisions
        if boxes.dtype.kind == "i":
            boxes = boxes.astype("float")

        # initialize the list of picked indexes	
        pick = []

        # grab the coordinates of the bounding boxes
        x1 = boxes[:,0]
        y1 = boxes[:,1]
        x2 = boxes[:,2]
        y2 = boxes[:,3]

        # compute the area of the bounding boxes and sort the bounding
        # boxes by the bottom-right y-coordinate of the bounding box
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)

        # keep looping while some indexes still remain in the indexes
        # list
        while len(idxs) > 0:
            # grab the last index in the indexes list and add the
            # index value to the list of picked indexes
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)

            # find the largest (x, y) coordinates for the start of
            # the bounding box and the smallest (x, y) coordinates
            # for the end of the bounding box
            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])

            # compute the width and height of the bounding box
            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)

            # compute the ratio of overlap
            overlap = (w * h) / area[idxs[:last]]

            # delete all indexes from the index list that have
            idxs = np.delete(idxs, np.concatenate(([last],
                np.where(overlap > overlapThresh)[0])))

        # return only the bounding boxes that were picked using the
        # integer data type

        # print('pick:',pick)
        # return [boxes[pick].astype("int"), pick]
        return pick


    def __detect_person_by_yolov3(self, frame):
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

        return [personId, personInfo, personConf]


    def __detect_person_by_hogsvm(self, frame):

        found, w = self.__hog.detectMultiScale(frame, winStride=(4, 4), scale=1.05)

        

        personId = []
        personInfo = []
        personConf = []

        pick = self.__non_max_suppression_fast(found)

        personid = 0
        for pickid in pick:
            if w[personid][0] >= 0:
                found[pickid][3] = int(found[pickid][3] / 2)

                personId.append(personid)
                personInfo.append(found[pickid])
                personConf.append(w[pickid][0])

                personid += 1

        # personId = range(len(personInfo))
        # personConf = [0 for i in personId]
        # print(personConf)

        # number = 0
        # for f, weight in zip(found, w):
        #     if weight[0] >= 0.75:
        #         f[3] = int(f[3]/2)
        #         personInfo.append(f)
        #         personConf.append(weight[0])
        #         personId.append(number)
        #         number += 1
        
        # print(conf)

        # indices = cv.dnn.NMSBoxes(
        #     found,
        #     conf,
        #     YOLOV3_NET_CONF_THRESHOULD,
        #     YOLOV3_NET_NMS_THRESHOULD
        # )

        # personId = []
        # personInfo = []
        # personConf = []

        # for i, personid in zip(indices, range(len(indices))):
        #     i = i[0]
        #     personId.append(personid)
        #     personInfo.append(found[i])
        #     personConf.append(w[i])

        return [personId, personInfo, personConf]

        # found_number = []
        # found_filtered = []
        # found_weight = []

        # n = 0

        # print(found)

        # for ri, r in enumerate(found):
        #     for qi, q in enumerate(found):
        #         print(ri, qi)
        #         if ri != qi and self.__checkInside(r, q):
        #             break
        #         else:
        #             found_number.append(n)
        #             found_filtered.append(r)
        #             found_weight.append(0)
        #             n += 1

        # print(found_filtered)
        # print(n)

        # return [found_number, found_filtered, found_weight]


    def __detect_hat_by_darknet19(self, frame, left, top, width, height):
        # Create a 4D blob from a person img.
        blob_hat = cv.dnn.blobFromImage(
            frame[top:top+height, left:left+width],
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

        label_result, conf_result = self.__getHat(frame, outs_hat)
        
        return [label_result, conf_result]


    def __detect_person(self, frame):

        if self.__person_detect_type == self.DETECT_PERSON_BY_NET:
            return self.__detect_person_by_yolov3(frame)
        
        if self.__person_detect_type == self.DETECT_PERSON_BY_HOGSVM:
            return self.__detect_person_by_hogsvm(frame)


    def __detect_hat(self, frame, left, top, width, height):
        return self.__detect_hat_by_darknet19(frame, left, top, width, height)

    
    def __detectSingleFrame(self, frame):

        # detect person
        personId, personInfo, personConf = self.__detect_person(frame)

        # save hat info
        hatLabel = []
        hatConf = []

        # detect hat
        for i in personId:
            box = personInfo[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]

            # detect hat
            label_result, conf_result = self.__detect_hat_by_darknet19(frame, left, top, width, height)

            hatLabel.append(label_result)
            hatConf.append(conf_result)
        
        return [personId, personInfo, personConf, hatLabel, hatConf]


    def __checkFile(self, path):
        # check if the file exeist
        if not os.path.isfile(path):
            raise Exception("Input image file " + path + " doesn't exist")


    def detectImageFile(self, path, outputPath=0):
        
        # check file
        self.__checkFile(path)

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

            detect_result = self.__detectSingleFrame(frame)

            self.__drawFrame(frame, detect_result)
            
            if outputPath:
                cv.imwrite(outputPath, frame.astype(np.uint8))

            # cv.imshow('test', frame)
    

    def detectVedioFile(self, path, outputPath=0):
        # check file
        self.__checkFile(path)

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

        detect_count = 0

        detect_result = []

        total_timer = cv.getTickCount()

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

            timer = cv.getTickCount()

            # if we needs detect frame
            if detect_count == 0:
                # personId, personInfo, personConf, hatLabel, hatConf = self.__detectSingleFrame(frame)
                detect_result = self.__detectSingleFrame(frame)

                # init tracker
                tracker = cv.MultiTracker_create()
                
                # add multi tracker
                for i in detect_result[PERSON_ID]:
                    tracker.add(cv.TrackerKCF_create(), frame, detect_result[PERSON_INFO][i])
                
                # reset count down
                detect_count = 7

                print('detect', end='\n')
            # if we needs predict frame
            else:
                # predict frame
                trackerResult, trackerInfo = tracker.update(frame)

                # update person info
                for i, newPersonInfo in zip(detect_result[PERSON_ID], trackerInfo):
                    left = int(newPersonInfo[0])
                    top = int(newPersonInfo[1])
                    width = int(newPersonInfo[2])
                    height = int(newPersonInfo[3])
                    if left < 0: left = 0
                    if top < 0: top = 0
                    detect_result[PERSON_INFO][i] = [left, top, width, height]

                # count down
                detect_count -= 1

                print('tracker', end='\n')
            
            # draw frame
            self.__drawFrame(frame, detect_result)

            done_frame += 1

            # show info

            result_fps = cv.getTickFrequency() / (cv.getTickCount() - timer)
            total_time = (cv.getTickCount() - total_timer) / cv.getTickFrequency()

            cv.putText(frame, "[i7-7700HQ 2.80GHz] [GTX1050ti] [net:KCF=1:7]", (25,25), cv.FONT_HERSHEY_SIMPLEX, 0.6, (50,170,50), 2)
            cv.putText(frame, "[net1: yolov3] [net2: darknet19]", (25,50), cv.FONT_HERSHEY_SIMPLEX, 0.6, (50,170,50), 2)
            cv.putText(frame, "FPS : " + str(int(result_fps)), (25,75), cv.FONT_HERSHEY_SIMPLEX, 0.6, (50,170,50), 2)
            cv.putText(frame, "cost : " + str(int(total_time)) + "s", (25,100), cv.FONT_HERSHEY_SIMPLEX, 0.6, (50,170,50), 2)

            cv.imshow("Test", frame)

            print('[%3.2f/100.00] %d of %d frame has done!' % (done_frame/total_frame*100, done_frame, total_frame), end='\r')

            # write vedio file
            
            vid_writer.write(frame.astype(np.uint8))


# for test
if __name__ == "__main__":
    # os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    hatDetector = HatDetector(HatDetector.DETECT_PERSON_BY_NET)

    for i in range(11):
        code = i+1
        hatDetector.detectImageFile('./testFile/test_img_'+str(code)+'.jpg', './testFile/test_img_'+str(code)+'_result_hog.jpg')
    # hatDetector.detectVedioFile('./testFile/test_vedio_2.mp4', './testFile/test_vedio_2_result.mp4')
