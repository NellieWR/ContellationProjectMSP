
    
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


def FindStars(name, perc = 0.01, sizelim = 10):
    print("ProcessImage")
    npim = ProcessImage(name, percent = perc)
    
    print("FrameMaker")
    clid, clim = FrameMaker(npim)
    
    print("ClusterStart")
    clid, centers = ClusterStart(clid, clim, npim, size_limit = sizelim)
    
    print("Stars found: ", centers.shape[0])
    
    distances = Distances(centers)
    ratios = Ratios(distances) 
    angles = Angles(distances)
    
    
    print("ReadDir")              
    constellations = ReadDir()

    return npim, clid, clim, centers, constellations, ratios, angles

def OpenDatabase(filename):
    distances = np.genfromtxt(filename, delimiter = ',')
    distances = np.delete(distances, 0, 0)
    distances = np.delete(distances, 0, 1)
    ratios = Ratios(distances)
    angles = Angles(distances)
    
    return distances, ratios, angles

def ProcessImage(imagename, percent = 0.01):
    im = Image.open(imagename).convert("L") # Opens a .jpg file containing some picture of the night sky and converts it to grayscale.
    npim = np.array(im) # Converts the image to a numpy array
    dim = npim.shape # Takes the dimensions of theimage numpy array.
    
    greyval = np.zeros(256) # Vector that will count how often each greyscale value occurs.
    
    for i in range(dim[0]): # For each row of the image
        for j in range(dim[1]): # For each element of each row.
            val = npim[i][j] # Take the greyscale value.
            greyval[val] = greyval[val]+1 # Add one count to the amount of occurences of this greyscale value.
    
    pixn = dim[0]*dim[1] # Number of pixels.
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

def ClusterStart(clid, clim, npim, size_limit = 10):
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
    def __init__(self, imratios, dbratios, imangles, dbangles, centers, npim, threshpercent = 50): # Automatically called when an instance of this object is created.
        self.imratios = imratios
        self.dbratios = dbratios
        self.centers = centers
        self.imangles = imangles
        self.dbangles = dbangles
        self.npim = npim
        self.threshpercent = threshpercent
    
    def CompareRatios(self):
        length = self.centers.shape[0] # Takes the amount of stars identified in the image.
        brightness = np.zeros((length, 1)) # Initialises a matrix that will be used to calculate brightness for each star.
        count = 0 # Initialises a counter for how many ratio matches have been found.
        for n in range(length): # Loop te calculate brightness.
            brightness[n] = self.centers[n][2]*self.centers[n][3] # Finds the total brightness for each star.
        brightest = np.argmax(brightness, axis = 0) # Finds the ID of thebrightest star.
        
        stars = np.zeros((length, 1)) # Array that will store which stars are identified as potiential constellation stars, and how often each is identified.
        plt.imshow(self.npim) # Initialises a plot with the processed constellation image in there.
        plt.scatter(x=[self.centers[brightest,1]],y=[self.centers[brightest,0]],c = 'r', s = 10) # Adds the brightest star as a scatter point.
        for nim in range(self.imratios.shape[0]): # For stars branching off from the brightest in some direction in the image.
            for pim in range(self.imratios.shape[0]): # For stars branching off from the brightest in some direction in the image.
                if nim != pim: # Duplicate index numbers along different axes should not be checked.
                    for ndb in range(self.dbratios.shape[0]): # For stars branching off from some mdb in some direction in the database.
                        for mdb in range(self.dbratios.shape[0]): # mdb that stars are branching off of for the ratios.
                            for pdb in range(self.dbratios.shape[0]): # For stars branching off from some mdb in some direction in the database.
                                if ndb != mdb and ndb != pdb and mdb != pdb: # Duplicate index numbers along different axes shouldn not be checked.
                                    upperratio = self.imratios[nim, brightest, pim] <= 1.01*self.dbratios[ndb, mdb, pdb] # Bool to check for ratio agreement to some upper bound.
                                    lowerratio = self.imratios[nim, brightest, pim] >= 0.99*self.dbratios[ndb, mdb, pdb] # Bool to check for ratio agreement to some lower bound.
                                    upperangle = self.imangles[nim, brightest, pim] <= 1.01*self.dbangles[ndb, mdb, pdb] # Bool to check for angle agreement to some upper bound.
                                    lowerangle = self.imangles[nim, brightest, pim] >= 0.99*self.dbangles[ndb, mdb, pdb] # Bool to check for angle agreement to some lower bound.
                                    if lowerratio and upperratio and lowerangle and upperangle: # Checks if all the bools are true.
                                        #print(self.imratios[nim, brightest, pim])
                                        #print(self.dbratios[ndb, mdb, pdb])
                                        count = count +1 # Add one to the matching ratio counter.
                                        #plt.scatter(x=[self.centers[nim,1],self.centers[pim,1]],y=[self.centers[nim,0],self.centers[pim,0]],c = 'r', s = 10) # Adds the stars that make the ratio to the scatter plot.
                                        stars[nim, 0] = stars[nim, 0]+1
                                        stars[pim, 0] = stars[pim, 0]+1
        print(count)
        print(stars)
        stars = stars.astype(int) # Changes the data type of stars to integers.
        
        matches = np.zeros((length, 1)) # Will count the amount of matches for each star.
        for m in range(length): # Picks a star in imratios/imangles to compare ratios or angles from.
            if stars[m] != 0: # Checks if a star is even considered part of a constellation.
                for nim in range(self.imratios.shape[0]): # For stars branching off from m in some direction in the image.
                    for pim in range(self.imratios.shape[0]): # For stars branching off from m in some direction in the image.
                        if nim != pim: # Duplicate index numbers along different axes should not be checked.
                            for ndb in range(self.dbratios.shape[0]): # For stars branching off from some mdb in some direction in the database.
                                for mdb in range(self.dbratios.shape[0]): # mdb that stars are branching off of for the ratios.
                                    for pdb in range(self.dbratios.shape[0]): # For stars branching off from some mdb in some direction in the database.
                                        if ndb != mdb and ndb != pdb and mdb != pdb: # Duplicate index numbers along different axes shouldn not be checked.
                                            upperratio = self.imratios[nim, m, pim] <= 1.01*self.dbratios[ndb, mdb, pdb] # Bool to check for ratio agreement to some upper bound.
                                            lowerratio = self.imratios[nim, m, pim] >= 0.99*self.dbratios[ndb, mdb, pdb] # Bool to check for ratio agreement to some lower bound.
                                            upperangle = self.imangles[nim, m, pim] <= 1.01*self.dbangles[ndb, mdb, pdb] # Bool to check for angle agreement to some upper bound.
                                            lowerangle = self.imangles[nim, m, pim] >= 0.99*self.dbangles[ndb, mdb, pdb] # Bool to check for angle agreement to some lower bound.
                                            if upperratio and lowerratio and upperangle and lowerangle: # Checks if all the bools are true.
                                                matches[m] = matches[m]+1 # Adds one to the amount of matches found for this star.
                                                
        print(matches)
        matchesperstar = (self.dbratios.shape[0]-1)*(self.dbratios.shape[0]-2) # Calculates how many ratios one star can be a part of.
        percentages = np.zeros((length, 1)) # Array that will store the percentage of ratios that match for each star.
        for n in range(length): # For-loop to calculate the percentage of matches that a star made w.r.t. how many it could have made.
            percentages[n] = matches[n]/matchesperstar*100 # Calculates a percentage.
        print(percentages)
        
        for n in range(length): # For-loop to plot the stars that have made more than 50% of ratio matches it could have made.
            if percentages[n]>=self.threshpercent: # Checks the percentage threshold.
                plt.scatter(x=self.centers[n, 1], y=self.centers[n, 0], c = 'r', s = 10) # Plots a star
        plt.show() # Shows the image.
        
        
        
    
    


