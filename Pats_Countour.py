# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 13:20:09 2019

@author: Patrick
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import imutils
from imutils import perspective
from imutils import contours

img = cv2.imread("capture.jpg")
imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
imgray = cv2.GaussianBlur(imgray, (5, 5), 0)


edged = cv2.Canny(imgray, 50, 50)
edged = cv2.dilate(edged, None, iterations=1)
edged = cv2.erode(edged, None, iterations=1)

cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
(cnts, _) = contours.sort_contours(cnts)

for c in cnts:
	if cv2.contourArea(c) > 1000:
		box = cv2.minAreaRect(c)
		box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
		box = np.array(box, dtype="int")
		cv2.drawContours(img, [box.astype("int")], -1, (0, 255, 0), 2)
		continue
    


plt.imshow(img)
plt.gray()
plt.show()
