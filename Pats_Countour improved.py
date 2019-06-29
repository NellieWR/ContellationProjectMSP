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
	if cv2.contourArea(c) > 100:
        
		[x,y,w,h] = cv2.boundingRect(c)
		cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,0),2)
		print (x,y,w,h)
		img[y:y+h,x:x+w,:] = 0
		continue
    


plt.imshow(img)
plt.gray()
plt.show()
