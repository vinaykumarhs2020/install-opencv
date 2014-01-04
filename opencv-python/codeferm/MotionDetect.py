"""
Copyright (c) Steven P. Goldsmith. All rights reserved.

Created by Steven P. Goldsmith on December 23, 2013
sgoldsmith@codeferm.com
"""

import logging, sys, time, numpy, cv2, cv2.cv as cv

"""Motion detector.
    
Uses moving average to determine change percent.

sys.argv[1] = source file or will default to "../../resources/traffic.mp4" if no args passed.

@author: sgoldsmith

"""

def contours(source):
    # The background (bright) dilates around the black regions of frame
    source = cv2.dilate(source, None, iterations=15);
    # The bright areas of the image (the background, apparently), get thinner, whereas the dark zones bigger
    source = cv2.erode(source, None, iterations=10);
    # Find contours
    contours, heirarchy = cv2.findContours(source, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Add objects with motion
    movementLocations = []
    for contour in contours:
        rect = cv2.boundingRect(contour)
        movementLocations.append(rect)
    return movementLocations

# Configure logger
logger = logging.getLogger("VideoLoop")
logger.setLevel("INFO")
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(module)s %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)
# If no args passed then default to internal file
if len(sys.argv) < 2:
    url = "../../resources/traffic.mp4"
else:
    url = sys.argv[1]
videoCapture = cv2.VideoCapture(url)
logger.info("URL: %s" % url)
logger.info("Resolution: %dx%d" % (videoCapture.get(cv.CV_CAP_PROP_FRAME_WIDTH),
                               videoCapture.get(cv.CV_CAP_PROP_FRAME_HEIGHT)))
lastFrame = False
frames = 0
framesWithMotion = 0
movingAvgImg = None
totalPixels = videoCapture.get(cv.CV_CAP_PROP_FRAME_WIDTH) * videoCapture.get(cv.CV_CAP_PROP_FRAME_HEIGHT)
movementLocations = []
start = time.time()
while not lastFrame:
    ret, image = videoCapture.read()
    if ret:
        # Generate work image by blurring
        workImg = cv2.blur(image, (8, 8))
        # Generate moving average image if needed
        if movingAvgImg == None:
            movingAvgImg = numpy.float32(workImg)
        # Generate moving average image
        cv2.accumulateWeighted(workImg, movingAvgImg, .03)
        diffImg = cv2.absdiff(workImg, cv2.convertScaleAbs(movingAvgImg))
        # Convert to grayscale
        grayImg = cv2.cvtColor(diffImg, cv2.COLOR_BGR2GRAY)
        # Convert to BW
        return_val, grayImg = cv2.threshold(grayImg, 25, 255, cv2.THRESH_BINARY)
        # Total number of changed motion pixels
        motionPercent = 100.0 * cv2.countNonZero(grayImg) / totalPixels
        # Detect if camera is adjusting and reset reference if more than maxChange
        if motionPercent > 25.0:
            movingAvgImg = numpy.float32(workImg)
        movementLocations = contours(grayImg)
        # Threshold trigger motion
        if motionPercent > 2.0:
            framesWithMotion += 1
        frames += 1
    else:
        lastFrame = True
elapse = time.time() - start
logger.info("%d frames, %d frames with motion" % (frames, framesWithMotion))
logger.info("Elapse time: %4.2f seconds" % elapse)
del videoCapture
