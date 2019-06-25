
    
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 21:14:47 2019
@author: Constellation Group
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
import csv
import math


def FindStars(name):
    print("ProcessImage")
    npim = ProcessImage(name)
    
    print("FrameMaker")
    clid, clim = FrameMaker(npim)
    
    print("ClusterStart")
    clid, centers = ClusterStart(clid, clim, npim)
    
    print("Stars found: ", centers.shape[0])
    
    distances = Distances(centers)
    ratios = Ratios(distances) 
    angles = Angles(distances)
    
    
    print("ReadDir")              
    constellations = ReadDir()

    return clid, clim, centers, constellations, ratios, angles



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

    
    #plt.imshow(npim) # Puts the array data in a plot to display.
    #plt.gray() # Sets the colour option to gray.
    #plt.show() # Show the image.
    
    
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

def ClusterStart(clid, clim, npim):
    cont = True # State variable that indicates if there has been a change in the clustering
    inc  = 1
    while cont:
        cont = False
        for n in range(1,clid.shape[0]-2): # For each row of the id matrix
            for m in range(1,clid.shape[1]-2): # For each column of the id matrix
                if -1 <clid[n, m]: # Checks if the location is valid
                    check = np.zeros((1,0)) # Creates a matrix that will hold the values of the matrix cells surrounding the current one
                
                    for i in range(n-1,n+2): # Checks around cell in quastion
                        for j in range(m-1,m+2):
                        
                            if clid[i,j]>0: # Will append all non-zero positive values surrounding the cell in question
                                check = np.append(check, np.array([[clid[i,j]]]), axis = 1)
                    if check.shape[1] == 0: # If checking matrix is empty, then that means that all the surrounding, valid cells are all zero
                        minimum = inc # in this case, the value here will be given as inc
                        inc = inc + 1 # inc increases
                        clid[n,m] = minimum
                        cont = True
                        
                    else:
                        minimum = np.amin(check)
                        
                        if minimum < clid[n,m] or clid[n,m]==0:
                            clid[n,m] = minimum
                            cont = True

                    
    centers = np.zeros((inc,4))
    for n in range(1,clid.shape[0]-2):
            for m in range(1,clid.shape[1]-2):
                if clid[n,m] > 0:
                    centers[int(clid[n,m])-1,0] = centers[int(clid[n,m])-1,0] + n
                    centers[int(clid[n,m])-1,1] = centers[int(clid[n,m])-1,1] + m
                    centers[int(clid[n,m])-1,2] = centers[int(clid[n,m])-1,2] + int(clim[n,m])
                    centers[int(clid[n,m])-1,3] = centers[int(clid[n,m])-1,3] + 1
    
    C = np.zeros((0,4))
    
    size_limit = 10 # Threshold for cluster size 
    for n in range(centers.shape[0]):
        if centers[n,3] > size_limit: 
            C = np.append(C,np.array([centers[n,:]]), axis = 0)
            
    for n in range(C.shape[0]):
        C[n][2] = C[n][2]/C[n][3]
        for m in range(C.shape[1]-2):
            C[n][m] = C[n][m]/C[n][3] -1
            
    
    # The following sorts by total brightness
    cont = True
    while cont:
        cont = False
        for n in range(C.shape[0]-1):
            if C[n,2]*C[n,3] < C[n+1,2]*C[n+1,3]:
                cont = True
                replace = np.array(([C[n+1,:],C[n,:]]))
                C[n,:] = replace[0,:]
                C[n+1,:] = replace[1,:]
    
    
            
    plt.imshow(npim)
    
    for n in range(C.shape[0]):
        plt.scatter(x=[C[n,1]], y=[C[n,0]], c='r', s=10)
    plt.show()
            
    return clid, C

def Distances(centers): #Creates a distances matrix
    distances = np.zeros((centers.shape[0],centers.shape[0]))
    for n in range(centers.shape[0]):
        for m in range(centers.shape[0]):
            if n!=m:
                distances[n,m] = math.sqrt((centers[n,0]-centers[m,0])**2+(centers[n,1]-centers[m,1])**2)    
    return distances


def Ratios(distances): #Creates the ratios matrix
    ratios = np.zeros((distances.shape[0],distances.shape[0],distances.shape[0]))
 
    for n in range(distances.shape[0]):
        for m in range(distances.shape[0]):
            for p in range(distances.shape[0]):
                if n!=m and n!=p and m!=p and distances[n,m]!=0 and distances[m,p]!=0 and distances[n,p]!=0:
                    ratios[n,m,p] = distances[n,m]/distances[m,p]
    
    return ratios

def Angles(distances): #Creates an angles matrix
    angles = np.zeros((distances.shape[0],distances.shape[0],distances.shape[0]))
    for n in range(distances.shape[0]):
        for m in range(distances.shape[0]):
            for p in range(distances.shape[0]):
                if n!=m and n!=p and m!=p and distances[n,m]!=0 and distances[m,p]!=0 and distances[n,p]!=0:
                    angles[n,m,p] = np.arccos((distances[n,m]**2+distances[m,p]**2-distances[n,p]**2)/(2*distances[n,m]*distances[m,p]))
                    
    return angles

    
    

def RatiosFromDistances(distances):
    ratios = np.zeros((distances.shape[0],distances.shape[0],distances.shape[0])) # Creates an empty array to gold the ratios.
    for n in range(distances.shape[0]):
        for m in range(distances.shape[0]):
            for p in range(distances.shape[0]):
                if n!=m and n!=p and m!=p:
                    ratios[n,m,p] = distances[n,m]/distances[m,p]
    return ratios

def ReadDir(): # Finds the .csv files 
    dirs = np.asarray(os.listdir(os.getcwd()))
    files = np.zeros((0,2))
    for n in range(dirs.shape[0]):
        if ".csv" in dirs[n]: # Appends to the list all the 
            files = np.append(files, np.array([[dirs[n],0]]),axis = 0)
    return files

class ConstellationFinder:
    def __init__(self, imratios, dbratios, imangles, dbangles, centers):
        self.imratios = imratios
        self.dbratios = dbratios
        self.centers = centers
        self.imangles = imangles
        self.dbangles = dbangles
    
    def CompareRatios(self):
        length = self.centers.shape[0]
        brightness = np.zeros((length, 1))
        count = 0
        for n in range(length):
            brightness[n] = self.centers[n][2]*self.centers[n][3] # Finds the total brightness for each star.
        brightest = np.argmax(brightness, axis = 0) # Finds the ID of thebrightest star.
        for nim in range(self.imratios.shape[0]): # For stars branching off from m in some direction.
            for pim in range(self.imratios.shape[0]): # For stars brannhing off from m in some direction.
                if nim != pim:
                    for ndb in range(self.dbratios.shape[0]):
                        for mdb in range(self.dbratios.shape[0]):
                            for pdb in range(self.dbratios.shape[0]):
                                if ndb != mdb and ndb != pdb and mdb != pdb:
                                    if self.imratios[nim, brightest, pim] >= 0.9999*self.dbratios[ndb, mdb, pdb] and self.imratios[nim, brightest, pim] <= 1.0001*self.dbratios[ndb, mdb, pdb]:
                                        print(self.imratios[nim, brightest, pim])
                                        print(self.dbratios[ndb, mdb, pdb])
                                        count = count +1
        print(count)
        
        
        
    
    


