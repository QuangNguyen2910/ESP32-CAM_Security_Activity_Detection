import cv2
import numpy as np
import urllib.request
import pyttsx3

url = 'http://172.20.10.7/cam-hi.jpg'

cap = cv2.VideoCapture(url)
whT = 320
confThreshold = 0.5
nmsThreshold = 0.3
classesfile = 'coco.names'
classNames = []
with open(classesfile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

modelConfig = 'yolov3-tiny.cfg'
modelWeights = 'yolov3-tiny.weights'
net = cv2.dnn.readNetFromDarknet(modelConfig, modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Initialize text-to-speech engine
engine = pyttsx3.init()

def findObject(outputs, im):
    hT, wT, cT = im.shape
    bbox = []
    classIds = []
    confs = []
    max_confidence = 0
    best_idx = -1

    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                w, h = int(det[2] * wT), int(det[3] * hT)
                x, y = int((det[0] * wT) - w / 2), int((det[1] * hT) - h / 2)
                bbox.append([x, y, w, h])
                classIds.append(classId)
                confs.append(float(confidence))

                # Keep track of the object with the highest confidence
                if confidence > max_confidence:
                    max_confidence = confidence
                    best_idx = len(bbox) - 1

    # If there is a best index, output that object only
    if best_idx >= 0:
        box = bbox[best_idx]
        x, y, w, h = box[0], box[1], box[2], box[3]
        object_name = classNames[classIds[best_idx]]
        
        # Voice output for the most accurate object
        engine.say(f'Object detected: {object_name}')
        engine.runAndWait()

        cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 255), 2)
        cv2.putText(im, f'{object_name.upper()} {int(confs[best_idx] * 100)}%', 
                    (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

while True:
    img_resp = urllib.request.urlopen(url)
    imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
    im = cv2.imdecode(imgnp, -1)
    success, img = cap.read()

    blob = cv2.dnn.blobFromImage(im, 1 / 255, (whT, whT), [0, 0, 0], 1, crop=False)
    net.setInput(blob)
    layernames = net.getLayerNames()

    unconnected_out_layers = net.getUnconnectedOutLayers()
    if isinstance(unconnected_out_layers[0], list) or isinstance(unconnected_out_layers[0], np.ndarray):
        outputNames = [layernames[i[0] - 1] for i in unconnected_out_layers]
    else:
        outputNames = [layernames[unconnected_out_layers[i] - 1] for i in range(len(unconnected_out_layers))]

    outputs = net.forward(outputNames)

    findObject(outputs, im)

    cv2.imshow('Image', im)
    cv2.waitKey(1)
