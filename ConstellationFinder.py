# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 21:14:47 2019

@author: ander and nelson
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def FindStars(name):
    npim = ProcessImage(name)
    clid, clim = FrameMaker(npim)
    centers = ClusterStart(clid, clim)
    for n in range(centers.shape[0]):
        for m in range(centers.shape[1]-1):
            centers[n][m] = centers[n][m]/centers[n][3]
 

    implot = plt.imshow(npim)


    for n in range(centers.shape[0]):
        plt.scatter([centers[n][1]-1], [centers[n][0]-1], c='r', s=1)

    plt.show()
    
    return npim, clid, clim, centers



def ProcessImage(imagename):
    im = Image.open(imagename).convert("L") # Opens a .jpg file containing some picture of the night sky and converts it to grayscale.
    npim = np.array(im) # Converts the image to a numpy array
    dim = npim.shape # Takes the dimensions of theimage numpy array.
    
    greyval = np.zeros(256) # Vector that will count how often each greyscale value occurs.
    
    for i in range(dim[0]): # For each row of the image
        for j in range(dim[1]): # For each element of each row.
            val = npim[i][j] # Take the greyscale value.
            greyval[val] = greyval[val]+1 # Add one count to the amount of occurences of this greyscale value.
    
    pixn = dim[0]*dim[1] # Number of pixels.
    percent = 0.01 #Percetage
    thresh = percent*pixn # Threshold of how many pixels to keep. Now set to 1 percent of all pixels.
    threshbool = False # Boolean to be used for the while-loop.
    ii = 255 # Reverse grayscale counter.
    abovethresh = 0 # Counts how many pixels are in the one percent.
    
    while not threshbool:
        abovethresh = abovethresh+greyval[ii] # Adds the number of counts of some greyscale value to the number of counts within the one percent.
        if abovethresh>thresh:
            threshbool = True # Changes the boolean to true to stop the while loop if the threshold number of counts has been reached.
            threshgray = ii # Stores the current grayscale counter to perform the filtering later.
        else:
            ii = ii-1 # Lowers the grayscale counter by one to count the number of occurences of a lower grayscale value.
    print("Threshold at ",percent*100,"%: ",threshgray,". Actual percentage: ",100*abovethresh/pixn,"%")
    
    for i in range(dim[0]): # For every row of the image.
        for j in range(dim[1]): # For every element of the row.
            if npim[i][j]<threshgray: # If the greyscale value is above the threshold greyscale value.
                npim[i][j] = 0 # Change the greyscale value to 0.

    
    plt.imshow(npim) # Puts the array data in a plot to display.
    plt.gray() # Sets the colour option to gray.
    plt.show() # Show the image.
    
    
    return npim

def FrameMaker(npim):
    imdim = npim.shape # Takes the dimensions of the image numpy array.
    
    #clid = np.zeros(imdim[0]+2, imdim[1]+2, 2) # Creates the cluster identification array, with an additional frame and a dimension pixel and clusterID.
    clim = np.append(np.zeros((imdim[0], 1)), npim, axis = 1) # Appends a column of zeroes on the left of the image array.
    clim = np.append(clim, np.zeros((imdim[0], 1)), axis = 1) # Appends a column of zeroes on the right of the cluster ID array.
    clim = np.append(np.zeros((1, imdim[1]+2)), clim, axis = 0) # Appends a row of zeroes on the top of the cluster ID array.
    clim = np.append(clim, np.zeros((1, imdim[1]+2)), axis = 0) # Appends a row of zeroes on the bottom of the cluster ID array.
    cldim = clim.shape # Takes the dimensions of the cluster identification array.
    
    #clim = np.append(clim, np.zeros((cldim[0], clid[1], 2)), axis = 2)
    clid = np.zeros((cldim[0], cldim[1])) # Creates an array to hold the cluster identifications per pixel.
    for n in range(cldim[0]): # For all rows in cldim.
        for m in range(cldim[1]): # For all elements in each row of cldim.
            if clim[n, m]==0:
                clid[n, m] = -1 # The element of clid is assigned the value -1 if clim is 0 for this n, m.
    
    
    return clid, clim

def ClusterStart(clid, clim):
    inc = 0 # Keeps track of the cluster number.
    centers = np.zeros((0, 4)) # Creates an array of zeroes to store cluster info.
    for n in range(1, clid.shape[0]-2):
        for m in range(1, clid.shape[1]-2):
            if clid[n, m]==0:
                #print("Found cluster")
                centers, clid = ClusterSize(clid, clim, centers, n, m, inc)
                inc = inc+1
                #print(inc)
    print("Clusters identified: ",centers.shape[0])
    return centers

def ClusterSize(clid, clim, centers, n, m, inc):
    #print(inc)
    clid[n, m] = inc # Numbers the found cluster.
    if  inc>=centers.shape[0]: # Implies that cluster has been identified.
        #print(centers.shape[0])
        centers = np.append(centers, np.array([[n, m, clim[n, m], 1]]), axis = 0) # Adds a row with one cluster's information.
        #print(centers)
        #print(centers.shape[0])
    else: # Implies that the cluster creation hsa already started in a previous iteration.
        centers[inc, 0] = centers[inc, 0]+n # Update the center's x-value.
        centers[inc, 1] = centers[inc, 1]+m # Update the center's y-value.
        centers[inc, 2] = centers[inc, 2]+clim[n, m] # Update the centers'brightness.
        centers[inc, 3] = centers[inc, 3]+1 # Update the cluster's amount of pixels.
    if clid[n-1, m]==0:
        centers, clid = ClusterSize(clid, clim, centers, n-1, m, inc)
    if clid[n+1, m]==0:
        centers, clid = ClusterSize(clid, clim, centers, n+1, m, inc)
    if clid[n-1, m-1]==0:
        centers, clid = ClusterSize(clid, clim, centers, n-1, m-1, inc)
    if clid[n-1, m+1]==0:
        centers, clid = ClusterSize(clid, clim, centers, n-1, m+1, inc)
    if clid[n+1, m-1]==0:
        centers, clid = ClusterSize(clid, clim, centers, n+1, m-1, inc)
    if clid[n+1, m+1]==0:
        centers, clid = ClusterSize(clid, clim, centers, n+1, m+1, inc)
    if clid[n, m+1]==0:
        centers, clid = ClusterSize(clid, clim, centers, n, m+1, inc)
    if clid[n, m-1]==0:
        centers, clid = ClusterSize(clid, clim, centers, n, m-1, inc)
    return centers, clid
