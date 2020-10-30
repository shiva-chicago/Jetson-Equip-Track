#import libraries
from imutils.video import VideoStream
import numpy as np
import cv2
import imutils
import time
from datetime import datetime

def getTimeHMS ():
    currTime = datetime.now()
    dt_string = currTime.strftime("%H:%M:%S")
    return currTime, dt_string

# Get the colour of the tag using Mac tool in HSV colour space.
# Create upper and lower bounds for the colour detected
# neon green stick note colour (large)
colourLower = (23, 56, 136)
colourUpper = (50, 255, 255)

# light green sticky note color (small) 
#colourLower = (28, 85, 128)
#colourUpper = (83, 255, 255)

# Set VideoStream parameters
resolution = (640,360)
framerate=1
centerList = []
objReturned = False
objMoved = False
objMovedCount = 0

# Initialize the webcam stream and wait for 2 seconds
# for the camera sensor to warm up
print ("Starting video stream Now. Wait for warm up.")
vidStream = VideoStream(src=0, resolution=resolution, framerate=framerate).start()
time.sleep(2.0)


# Keep looping over every frame until user exits
while True:
    time.sleep(0.5)
    # read the frame. resize and blur it
    frame = vidStream.read()
    frame = imutils.resize(frame, width=640)
    blurredframe = cv2.GaussianBlur(frame, (11, 11), 0)
    hsvframe = cv2.cvtColor(blurredframe, cv2.COLOR_BGR2HSV)

    # create a mask for the input colour within range
    # Then remove any blobs left in the mask
    mask = cv2.inRange(hsvframe, colourLower, colourUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    center = None

    # Check if a contour was found
    if len(contours) > 0:
        # Find the largest contour and make sure it is not tiny dot
        maxcontour = max(contours, key = cv2.contourArea)
        ((x,y), radius) = cv2.minEnclosingCircle (maxcontour)
        moments = cv2.moments(maxcontour)
        center = (int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"]))

        if radius > 20:
            # If center List is empty, we are starting tracking now.
            # Also remember timestamp for later
            if len(centerList) == 0:
                foundTime, dt_string = getTimeHMS()
                print("Located the equipment at: ", dt_string)

            # draw a circle to show where the object was found
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)

            # Check if Object has returned to the original point.
            if (len(centerList) > 1):
                centerDiff = abs(center[0] - centerList[0][0]) + abs(center[1] - centerList[0][1])

                if (objMoved == False) and (centerDiff >= 20) :
                    startTime, dt_string = getTimeHMS()
                    print ("Equipment was moved from original location at: ", dt_string)
                    objMoved = True
                    objMovedCount += 1

                if (objMoved == True) and (centerDiff <= 10):
                    objReturned = True

            centerList.append(center)

    # Draw a line connecting all the center points
    for i in range(1, len(centerList)):
        cv2.line(frame, centerList[i - 1], centerList[i], (0, 0, 255), 5)

    # If object was returned, initialize the centerList
    if objReturned == True:
        # Calculate time taken to return the object
        endTime, dt_string = getTimeHMS() 
        print("Equipment returned to original spot at: ", dt_string)
        returnTime = endTime - startTime
        print("Equipment was returned in: ", returnTime.seconds, " seconds.")
        print("Equipment was moved ", objMovedCount, "times.")

        # Initialize flag and list for next iteration
        print ("\nLets start a fresh track of the .\n\n")
        centerList = []
        objReturned = False
        objMoved = False

    # Show the frame with the object location
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # If user presses 'q', stop the program
    if key == ord("q"):
        break

# Stop the video camera
vidStream.stop()

# Close all the windows
cv2.destroyAllWindows()

