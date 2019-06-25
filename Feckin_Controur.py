# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 13:03:10 2019

@author: Patrick
"""


import cv2
import numpy as np
import matplotlib.pyplot as plt

image = cv2.imread('capture.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

ret, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
blur = cv2.medianBlur(thresh, 1)
kernel = np.ones((10, 20), np.uint8)
img_dilation = cv2.dilate(blur, kernel, iterations=1)
ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
for i, ctr in enumerate(sorted_ctrs):
    # Get bounding box
    x, y, w, h = cv2.boundingRect(ctr)
    roi = image[y:y + h, x:x + w]
    if (h > 50 and w > 50) and h < 200:

        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), 1)        
        cv2.imshow('{}.jpg'.format(i), roi)
        continue
    
cv2.imshow('capture.jpg',image)
    
plt.imshow(image)
plt.gray()
plt.show()


