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
    clid, centers = ClusterStart(clid, clim)
    for n in range(centers.shape[0]):
        for m in range(centers.shape[1]-1):
            centers[n][m] = centers[n][m]/centers[n][3] -1
            
    
    
    
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
    cont = True
    inc  = 1
    while cont:
        cont = False
        #print("enter")
        for n in range(1,clid.shape[0]-2):
            for m in range(1,clid.shape[1]-2):
                
                if -1 <clid[n, m]:
                    check = np.zeros((1,0))
                
                    for i in range(n-1,n+2):
                        for j in range(m-1,m+2):
                        
                            if clid[i,j]>0:
                                check = np.append(check, np.array([[clid[i,j]]]), axis = 1)
                    #print(check)
                    if check.shape[1] == 0:
                        minimum = inc
                        inc = inc + 1
                        clid[n,m] = minimum
                        cont = True
                        
                    else:
                        minimum = np.amin(check)
                        
                        if minimum < clid[n,m] or clid[n,m]==0:
                            clid[n,m] = minimum
                            cont = True
                    #print(minimum)
                        
     

    centers = np.zeros((inc,4))
    for n in range(1,clid.shape[0]-2):
            for m in range(1,clid.shape[1]-2):
                if clid[n,m] > 0:
                    centers[int(clid[n,m])-1,0] = centers[int(clid[n,m])-1,0] + n
                    centers[int(clid[n,m])-1,1] = centers[int(clid[n,m])-1,1] + m
                    centers[int(clid[n,m])-1,2] = centers[int(clid[n,m])-1,2] + int(clid[n,m])
                    centers[int(clid[n,m])-1,3] = centers[int(clid[n,m])-1,3] + 1
    
    C = np.zeros((0,4))
    for n in range(centers.shape[0]):
        if centers[n,3] !=0:
            C = np.append(C,np.array([centers[n,:]]), axis = 0)
                
    return clid, C
