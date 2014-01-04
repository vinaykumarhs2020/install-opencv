"""
Copyright (c) Steven P. Goldsmith. All rights reserved.

Created by Steven P. Goldsmith on December 24, 2013
sgoldsmith@codeferm.com
"""

import logging, sys, time, cv2, cv2.cv as cv

"""Histogram of Oriented Gradients ([Dalal2005]) object detector.

sys.argv[1] = source file or will default to "../../resources/walking.mp4" if no args passed.

@author: sgoldsmith

"""

# Configure logger
logger = logging.getLogger("VideoLoop")
logger.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(module)s %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)
outputFile = "../../output/people-detect-python.avi"
# If no args passed then default to internal file
if len(sys.argv) < 2:
    url = "../../resources/walking.mp4"
else:
    url = sys.argv[1]
videoCapture = cv2.VideoCapture(url)
logger.info("Input file: %s" % url)
logger.info("Output file: %s" % outputFile)
logger.info("Resolution: %dx%d" % (videoCapture.get(cv.CV_CAP_PROP_FRAME_WIDTH),
                               videoCapture.get(cv.CV_CAP_PROP_FRAME_HEIGHT)))
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
videoWriter = cv2.VideoWriter(outputFile, cv.CV_FOURCC(*'DIVX'), videoCapture.get(cv.CV_CAP_PROP_FPS),
                              (int(videoCapture.get(cv.CV_CAP_PROP_FRAME_WIDTH)), int(videoCapture.get(cv.CV_CAP_PROP_FRAME_HEIGHT))), True)
lastFrame = False
frames = 0
framesWithPeople = 0
start = time.time()
while not lastFrame:
    ret, image = videoCapture.read()
    if ret:
        foundLocations, foundWeights = hog.detectMultiScale(image, winStride=(8, 8), padding=(32, 32), scale=1.05)
        if len (foundLocations) > 0:
            framesWithPeople += 1
            i = 0
            for x, y, w, h in foundLocations:
                # Draw rectangle around fond object
                cv2.rectangle(image, (x, y), (x + w, y + h), (0,255,0),2)
                # Print weight
                cv2.putText(image, "%1.2f" % foundWeights[i], (x, y-4), cv2.FONT_HERSHEY_PLAIN, 1.5, (255,255,255), thickness=2, lineType=cv2.CV_AA)
                i += 1
    else:
        lastFrame = True
    videoWriter.write(image)
    frames += 1

elapse = time.time() - start
logger.info("%d frames, %d frames with people" % (frames, framesWithPeople))
logger.info("Elapse time: %4.2f seconds" % elapse)
del videoCapture
del videoWriter
