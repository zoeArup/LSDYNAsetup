# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 10:27:44 2024

@author: Saoirse.Goodwin
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
import re
import time

import imageio
from matplotlib.ticker import AutoMinorLocator

# Please adjust path handling
# e.g. using my favorite os.getcwd()
path = os.getcwd()
file1 = "SolidCoords.csv"
file2 = "Solid_Extra_3.csv"
file3 = "Topography.xyz"

figDir = os.path.join(os.getcwd(), 'FIGS')

# To pick one or more timesteps to show
# Bonnie please check JS output of "Solid_Extra_3.csv" and improve
# documentation for this...
#timesteps   = np.arange(0,6,1)
timesteps = np.arange(0,10,1)
translate = [812577.0, 815838.63]
#translate = [0., 0.]

solidHeight = 0.5
gridSize    = 2

topoContourStepSize = 10
flowContourStepSize = 1
axisInterval = 25
ticksEvery1 = 100
ticksEvery2 = 20

caseTitle = 'Simulation_8_B_H1_Sh2_Sr4_R2_0_5'

fps = 2 # for GIF

#%%
def importTopo(path, file):
    # Import the topography data.
    filePath = os.path.join(path,file)
    df = pd.read_csv(filePath, 
                     sep = '\t')
    
    return df

def importALESolids(path, file):
    # Import the topography data.
    filePath = os.path.join(path,file)
    df = pd.read_csv(filePath, 
                     sep = ',', 
                     comment = '$', 
                     header = None, 
                     names=["ID", "x", "y", "z"])
    
    return df

def importFlow(path, file):    
    # Import the flow data. This is a bit harder because
    # we need to transpose the dataframe and set the header names.
    # Maybe later we adjust the JS output to be consistent. 
    filePath = os.path.join(path,file)
    
    df = pd.read_csv(filePath, sep = ',').T
    
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    
    # Deal with the index column being set as the solid cell index. 
    # (Not necessary for current version of the code, but it would be 
    # if the topo and flow dataframes are not both sorted in the same way.)
    df = df.reset_index()
    # Rename it as 'index'.
    df = df.rename(columns={"index" : "ID"})
    
    # Move ID colmn tto end to simplify working with timestep indices.
    df['ID'] = df.pop("ID")

    
    return df

def getXYZ(df, zName, interpolationMethod):
    # Do the interpolation to get a 2D array of points for the x, y and z 
    # positions. Note that we need to use interpolation.
    # Bonnie: see if we can do some smoothing on the topography, because
    # it currently looks horrendous. 
    # also please find a way of setting the interpolated values outside
    # of the original domain to nan, so that they aren't shown.
    x = np.linspace(min(df['x']), max(df['x']), int((max(df['x']) - min(df['x'])) / gridSize))
    y = np.linspace(min(df['y']), max(df['y']), int((max(df['y']) - min(df['y'])) / gridSize))
    
    print("max x", max(df['x']))
    print("min x", min(df['x']))
    print("x", len(x))
    print("y", len(y))
    # Classic meshgrid-griddata one-two combo.
    X, Y = np.meshgrid(x, y)
    Z = interpolate.griddata((df['x'], df['y']), df[zName], (X,Y), method=interpolationMethod, fill_value = 0)

    return (X,Y,Z)

def getStepSizeForContours(df, zName, step, manualMax):
    # For getting the step size for contours, as the name suggests.
    if manualMax == 0:
        max_level = max(df[zName])
    else:
        max_level = manualMax
    min_level = min(df[zName])
    step_level = step

    levels = np.arange(min_level, max_level + step_level, step_level)
    
    return levels


#%%
def mainProgram():
    # Import the two dataframes
    df1 = importALESolids(path, file1)
    df2 = importFlow(path, file2)
    df3 = importTopo(path, file3)
    
    #print("len df1", len(df1))
    #df1 = df1.head(500000)
    #df2 = df2.head(500000)
    
    # Get a list of the column headings
    df2Columns = df2.columns.tolist()
    
    (X1,Y1,Z1) = getXYZ(df3, 'z', interpolationMethod = 'linear')
    
    X1 += translate[0]
    Y1 += translate[1]
    # Loop through the selected timesteps.
    for timestep in timesteps:

        # Add a new column to the topography dataframe, indicating how filled
        # each cell is at a certain timestep. 
        
        #condition
        
        #print("df", sum(df2[df2Columns[timestep]] == 1))
        
        if df2[df2Columns[timestep]][0] == 1:
            
            df1['filled'] = 1 - df2[df2Columns[timestep]]
            
        else:
            
            df1['filled'] = df2[df2Columns[timestep]]
            
        
        #  df1['filled'] = 1 - df2[df2Columns[timestep]]
        
        # Add together all the 'filled' numbers for solid boxes that
        # are stacked on top of each other. 
        
        # Bonnie: you will have to do some extra processing to get 'solidHeight'
        # automatically. I suggest that you check the local box height through
        # df1['z'] (e.g. using np.diff) and add an extra column.
        # This may take a little time. Please prioritise making the graph look
        # nicer first. 
        dfout = df1.groupby(['x', 'y'], as_index=False)["filled"].sum()

        dfout['filled'] = dfout['filled'] * solidHeight
        
        # We need a 2D grid of X, Y and Z points. This does the required 
        # interpolation. 
        # Bonnie: try other interpolation methods for the topo, and/or
        # see if we can do smoothing on the Z-coords for the topo too.
        (X2,Y2,Z2) = getXYZ(dfout, 'filled', interpolationMethod = 'nearest')
        X2 += translate[0]
        Y2 += translate[1]
        # We need to define how closely spaced the contour lines are. 
        levels2 = getStepSizeForContours(dfout, 'filled', flowContourStepSize, 6)
        levels3 = getStepSizeForContours(df3, 'z', topoContourStepSize, 0)
        
        print(levels2)
        # Plot the figure. Bonnie: Please use ax1.set_aspect so that the plot
        # is not squished. Currently (10,5) is arbitrary. 
        fig = plt.figure(figsize=(10, 5), dpi = 450)
                
        myFont =   {'family'  : 'serif',
                     'serif'  : 'Arial',
                     'size'   : 10}
        
        
        plt.rc('font', **myFont)
        
        ax1 = fig.add_subplot(121)
        
        ax2 = fig.add_subplot(133)
        plt.suptitle(caseTitle + ' at $t=$' + str(int(df2Columns[timestep])) + ' s.', y=0.8)

        #axis rounding nearest 10 / 100
        #axis start from 0
        
        
        # Plot the two contours.
        ax1.contourf(X1, Y1, Z1, cmap='Greens', levels = levels3, alpha = 0.1)
        ax1.contour(X1, Y1, Z1,colors='k', linestyles='-',  linewidths=1, levels = levels3, alpha = 0.1)
        
        ax2.contourf(X1, Y1, Z1, cmap='Greens', levels = levels3, alpha = 0.1)
        ax2.contour(X1, Y1, Z1,colors='k', linestyles='-',  linewidths=1, levels = levels3, alpha = 0.1)
        
        #print(Z1)
        Z2[Z2 < 0.01] = np.nan
        
        #print(Z2)
        CS = ax1.contourf(X2, Y2, Z2, cmap='copper', levels = levels2)
        ax1.contour(X2, Y2, Z2, colors='k',      linestyles='--', linewidths=0.5, levels = levels2)
        
        cbar = plt.colorbar(CS, label = "Depth (m)", orientation = 'horizontal', aspect = 40)
        
        ax2.contourf(X2, Y2, Z2, cmap='copper', levels = levels2)
        ax2.contour(X2, Y2, Z2, colors='k',      linestyles='--', linewidths=0.5, levels = levels2)


        ax1.set_aspect('equal')
        ax2.set_aspect('equal')
        
        # maybe leave out -- Saoirse
        max_y_rounded = np.floor((max(df1['y']) + translate[1]) / axisInterval) * axisInterval 
        min_y_rounded = np.ceil((min(df1['y']) + translate[1]) / axisInterval) * axisInterval
        max_x_rounded = np.floor((max(df1['x']) + translate[0]) / axisInterval) * axisInterval
        min_x_rounded = np.ceil((min(df1['x']) + translate[0]) / axisInterval) * axisInterval

        # ax1.set_xlim([min_x_rounded, max_x_rounded])
        # ax1.set_ylim([min_y_rounded, max_y_rounded])
        ax2.set_xlim([812050.0, 812100.0])
        ax2.set_ylim([815930.0, 815970.0])
        
        majorTicksX1 = np.arange(min_x_rounded, max_x_rounded + 1, ticksEvery1)
        majorTicksY1 = np.arange(min_y_rounded, max_y_rounded + 1 , ticksEvery1)
        ax1.set_xticks(majorTicksX1)
        ax1.set_yticks(majorTicksY1)
        
        majorTicksX2 = np.arange(812050, 812100 + 1, ticksEvery2)
        majorTicksY2 = np.arange(815930, 815970 + 1, ticksEvery2)
        ax2.set_xticks(majorTicksX2)
        ax2.set_yticks(majorTicksY2)
        
        ax2.ticklabel_format(useOffset=False)
        
        ax1.xaxis.set_minor_locator(AutoMinorLocator())
        ax1.yaxis.set_minor_locator(AutoMinorLocator())
        ax2.xaxis.set_minor_locator(AutoMinorLocator())
        ax2.yaxis.set_minor_locator(AutoMinorLocator())
        
        #ax1.set_yticklabels([abs(y) for y in list(range(-20, 25, 5))])
        
        #plt.ylim([0, max_y_rounded])
        ax1.set_xlabel('x (m)')
        ax1.set_ylabel('y (m)')
        ax2.set_xlabel('x (m)')
        ax2.set_ylabel('y (m)')

        # plt.show()
        
        # Save figure -- Bonnie please tidy this up so it's consistent with the rest
        # of the code
        if not os.path.exists(figDir):
            os.makedirs(figDir)
            
        pngName = caseTitle + '_output_' + str(int(df2Columns[timestep])).zfill(3) + '_s.png'
        pngPath = os.path.join(figDir, pngName)
        plt.savefig(pngPath, bbox_inches='tight')
        # plt.close()
#%% 
def saveGIF():

    imageFiles = [file for file in os.listdir(figDir) if file.endswith('.png')]
    gifPath = os.path.join(figDir, 'combined.gif')

    with imageio.get_writer(gifPath, mode='I', fps = fps) as writer:
        for imageFile in imageFiles:
            imagePath = os.path.join(figDir, imageFile)
            image = imageio.imread(imagePath)
            writer.append_data(image)

#%% 
mainProgram()
saveGIF()

