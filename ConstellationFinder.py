
    
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
import sys
import time

def FindStars(name):
    npim = ProcessImage(name)
    print("FrameMaker")
    clid, clim = FrameMaker(npim)
    
    print("ClusterStart")
    clid, centers = ClusterStart(clid, clim, npim)
    
    print(centers.shape[0])
    
    print("Ratios")
    ratios, distances, angles = Ratios(centers)   
    
    print("ReadDir")              
    constellations = ReadDir()
    
    constellations = FindConf(constellations,ratios, distances, centers, name, angles)

    constellations = FindConf(constellations,ratios, distances)

    return clid, clim, centers, constellations, ratios 



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
                    centers[int(clid[n,m])-1,2] = centers[int(clid[n,m])-1,2] + int(clid[n,m])
                    centers[int(clid[n,m])-1,3] = centers[int(clid[n,m])-1,3] + 1
    
    C = np.zeros((0,4))
    
    size_limit =5 # Threshold for cluster size 
    for n in range(centers.shape[0]):
        if centers[n,3] > size_limit: 
            C = np.append(C,np.array([centers[n,:]]), axis = 0)
            
    for n in range(C.shape[0]):
        C[n][2] = C[n][2]/C[n][3]
        for m in range(C.shape[1]-2):
            C[n][m] = C[n][m]/C[n][3] -1
            
    plt.imshow(npim)
    
    for n in range(C.shape[0]):
        plt.scatter(x=[C[n,1]], y=[C[n,0]], c='r', s=10)
    plt.show()
            
    return clid, C

def Ratios(centers): #Creates the ratios matrix
    distances = np.zeros((centers.shape[0],centers.shape[0]))
    ratios = np.zeros((centers.shape[0],centers.shape[0],centers.shape[0]))
    angles = np.zeros((centers.shape[0],centers.shape[0],centers.shape[0]))
    for n in range(centers.shape[0]):
        for m in range(centers.shape[0]):
            if n!=m:
                distances[n,m] = math.sqrt((centers[n,0]-centers[m,0])**2+(centers[n,1]-centers[m,1])**2) 
    for n in range(centers.shape[0]):
        for m in range(centers.shape[0]):
            for p in range(centers.shape[0]):
                if n!=m and n!=p and m!=p:
                    ratios[n,m,p] = distances[n,m]/distances[m,p]
                    angles[n,m,p] = np.arccos((distances[n,m]**2+distances[m,p]**2-distances[n,p]**2)/(2*distances[n,m]*distances[m,p]))
                    
                    
    
    return ratios, distances, angles

def ReadDir(): # Finds the .csv files 
    dirs = np.asarray(os.listdir(os.getcwd()))
    files = np.zeros((0,2))
    for n in range(dirs.shape[0]):
        if ".csv" in dirs[n]: # Appends to the list all the 
            files = np.append(files, np.array([[dirs[n],0]]),axis = 0)
    return files

def FindConf(constellations,ratios,distances, centers, name, angles):
    
    for file in range(constellations.shape[0]): # Begins to check all the .csv files
        print(constellations[file,0]) 
        with open(constellations[file,0], newline='') as csvfile: #https://stackoverflow.com/questions/46614526/how-to-import-a-csv-file-into-a-data-array
            data = list(csv.reader(csvfile))
        data = np.asarray(data) # converts the list into a numpy array
        data = data[1:data.shape[0]-1,1:data.shape[1]-1] # Reshapes to exclude names
        data = data.astype(np.float) # Converts to float array
         
        locationratios = np.zeros((2,3))
        minimumratios = -1 
        locationangles = np.zeros((2,3))
        minimumangles = -1 
        
        for n in range(data.shape[0]):
            for m in range(data.shape[0]):
                for p in range(data.shape[0]):
                    if n!=m and n!=p and m!=p and data[n,m]!=0 and data[m,p]!=0:
                        if (np.abs(ratios - data[n,m]/data[m,p])).min() <minimumratios or minimumratios == -1:
                            minimumratios = (np.abs(ratios - data[n,m]/data[m,p])).min()
                            
                            minlocation = (np.abs(ratios - data[n,m]/data[m,p])).argmin()
 
                            minz = np.floor(minlocation/ratios.shape[0]**2)
                            miny = np.floor(((minlocation-(minz*ratios.shape[0]**2))/ratios.shape[0]))
                            minx = minlocation - minz*ratios.shape[0]**2 - ratios.shape[0]*miny
                            locationratios = np.array(([[n,m,p],[minz,miny,minx]]))
                            
                        
                        if (np.abs(angles - np.arccos((data[n,m]**2+data[m,p]**2-data[n,p]**2)/(2*data[n,m]*data[m,p])))).min() <minimumangles or minimumangles == -1:
                            minimumangles = (np.abs(angles - np.arccos((data[n,m]**2+data[m,p]**2-data[n,p]**2)/(2*data[n,m]*data[m,p])))).min()
                            
                            minlocation = (np.abs(angles - np.arccos((data[n,m]**2+data[m,p]**2-data[n,p]**2)/(2*data[n,m]*data[m,p])))).argmin()
 
                            minz = np.floor(minlocation/angles.shape[0]**2)
                            miny = np.floor(((minlocation-(minz*angles.shape[0]**2))/angles.shape[0]))
                            minx = minlocation - minz*angles.shape[0]**2 - angles.shape[0]*miny
                            locationangles = np.array(([[n,m,p],[minz,miny,minx]]))                        
                        
           
                        
                        
                        
        
        
        print(minimumratios)
        print(locationratios)
        print(float(data[int(locationratios[0,0]),int(locationratios[0,1])])/float(distances[int(locationratios[1,0]),int(locationratios[1,1])])-float(data[int(locationratios[0,1]),int(locationratios[0,2])])/float(distances[int(locationratios[1,1]),int(locationratios[1,2])]))
        print(minimumangles)
        print(locationangles)
        im = plt.imread(name)
        implot = plt.imshow(im)
        plt.scatter(x=[centers[int(locationratios[1,0]),1],centers[int(locationratios[1,1]),1],centers[int(locationratios[1,2]),1]], y=[centers[int(locationratios[1,0]),0],centers[int(locationratios[1,1]),0],centers[int(locationratios[1,2]),0]], c='r', s=40)
        plt.scatter(x=[centers[int(locationangles[1,0]),1],centers[int(locationangles[1,1]),1],centers[int(locationangles[1,2]),1]], y=[centers[int(locationangles[1,0]),0],centers[int(locationangles[1,1]),0],centers[int(locationangles[1,2]),0]], c='b', s=20)
        plt.show()
        
        
    return constellations
    

    

