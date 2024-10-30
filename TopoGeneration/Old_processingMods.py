# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 09:46:35 2024

@author: Thomas.Bush / Saoirse.Goodwin
"""

import os
import numpy as np
import pyarrow.parquet as pq
import re
import time
import scipy
import pandas as pd

#%% Create holding class.
class settings:
    pass

def processConfig(config):
    settingsObj = settings()

    settingsObj.caseToRun      = config["GENERAL"]["caseToRun"]
    settingsObj.keyFileName    = settingsObj.caseToRun
    
    settingsObj.xCoords        = \
        [int(config[settingsObj.caseToRun]["xCoordMin"]), \
         int(config[settingsObj.caseToRun]["xCoordMax"])]
    settingsObj.yCoords        = \
        [int(config[settingsObj.caseToRun]["yCoordMin"]), \
         int(config[settingsObj.caseToRun]["yCoordMax"])]

    settingsObj.outputFolder   = 'Output'
    settingsObj.parquetFile    = os.path.join('Data','HKSAR.parquet')
    settingsObj.currentPath    = os.path.dirname(os.getcwd()) 

    settingsObj = folderAdmin(settingsObj)

    settingsObj.gridResolution = float(config[settingsObj.caseToRun]["gridResolution"])

    if settingsObj.gridResolution > 1:
        settingsObj.gridResolution = int(settingsObj.gridResolution)
    verboseOutput(settingsObj)

    return settingsObj
    
#%%
def verboseOutput(settingsObj):
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    print('Model settings:')
    print(r'  Grid resolution selected: ' + str(settingsObj.gridResolution) + ' m.')
    print(r'  Total x-distance: ' + str(np.diff(settingsObj.xCoords)[0]) + ' m.')
    print(r'  Total y-distance: ' + str(np.diff(settingsObj.yCoords)[0]) + ' m.')
    print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

#%%
def reportProgress(string):
    print('')
    print(string)
    startTime = time.time()
    return startTime

def reportTime(startTime, string):
    endTime = time.time()
    print(string + "{:.2f}".format(endTime - startTime) + ' s.')

#%%
def folderAdmin(settingsObj):
    
    def createFolder(settingsObj):
        outputPath = os.path.join(settingsObj.currentPath, settingsObj.outputFolder)
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        
        return outputPath

    def getFileCounter(settingsObj):
        files = [f for f in os.listdir(settingsObj.outputPath) if os.path.isfile(os.path.join(settingsObj.outputPath, f))]

        fileCounter = 0
        for file in files:
            if settingsObj.keyFileName in file:
                # number = int(''.join([n for n in file if n.isdigit()]))
                number = int(re.search(r'\d+', file).group())
                if number > fileCounter:
                    fileCounter = number
        return fileCounter

    settingsObj.outputPath  = createFolder(settingsObj)
    settingsObj.fileCounter = getFileCounter(settingsObj)
        
    return settingsObj  

#%%
def getsortedDataframe(settingsObj):
    def getTable(settingsObj):    
        coordFilters = [
            ('X', '>=', settingsObj.xCoords[0]),
            ('X', '<=', settingsObj.xCoords[1]),
            ('Y', '>=', settingsObj.yCoords[0]),
            ('Y', '<=', settingsObj.yCoords[1])
        ]
        
        # Use the read_table function with the filters
        table = pq.read_table(os.path.join(settingsObj.currentPath, settingsObj.parquetFile), filters = coordFilters)
        
        return table
    
    def convertTableToDF(table):
        df        = table.to_pandas()
        return df
        
    def dataFrameSortingAndCleanup(df):
        df = df.dropna()
        df = df.sort_values(by = ['Y', 'X'])
        df = df.reset_index(drop = True)
        return df
    
    def decreaseResolution(df, settingsObj):
        uniqueX = df["X"].unique()
        uniqueY = df["Y"].unique()
        
        uniqueXFiltered = uniqueX[0 :: settingsObj.gridResolution]
        uniqueYFiltered = uniqueY[0 :: settingsObj.gridResolution]
    
        dfFilteredX = df[df['X'].isin(uniqueXFiltered)]
        df = dfFilteredX[dfFilteredX['Y'].isin(uniqueYFiltered)]
        df = df.reset_index(drop=True)
        
        return df

    def increaseResolution(df, settingsObj):

        xDist = np.diff(settingsObj.xCoords)[0]
        yDist = np.diff(settingsObj.yCoords)[0]

        xNoOfCells = int(xDist / settingsObj.gridResolution)
        yNoOfCells = int(yDist / settingsObj.gridResolution)
        
        xi = \
            np.linspace(min(settingsObj.xCoords),
                        max(settingsObj.xCoords),
                        xNoOfCells)
        yi = \
            np.linspace(min(settingsObj.yCoords),
                        max(settingsObj.yCoords),
                        yNoOfCells)

        zi = scipy.interpolate.griddata( \
            (df["X"], df["Y"]), df["Z"], 
            (xi[None, :], yi[:, None]), \
            method='cubic')
            
        
        xv, yv = np.meshgrid(xi, yi, indexing='ij')

        dfHiRes = pd.DataFrame(
            {'X': xv.flatten(),
              'Y': yv.flatten(),
              'Z': zi.transpose().flatten()
              })
       
        dfHiRes = dataFrameSortingAndCleanup(dfHiRes)

        return dfHiRes

    startTime = reportProgress('Preparing dataframe...')

    table = getTable(settingsObj)
    df = convertTableToDF(table)
    dfSorted = dataFrameSortingAndCleanup(df)

    if settingsObj.gridResolution > 1:
        dfSorted = decreaseResolution(dfSorted, settingsObj)
    elif settingsObj.gridResolution < 1:
        dfSorted = increaseResolution(dfSorted, settingsObj)
    
    reportTime(startTime, '  Time to prepare dataframe: ')
    
    return dfSorted
