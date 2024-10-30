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
import math
import json

import imageio
from matplotlib import ticker
from scipy.signal import savgol_filter

'''
User Guide To Run: 
1. ALEContainerFile, DebrisFlowFile must be exist at the same folder with code file
2. Resolutions and graph presentation can be modified

'''
# -----------User defined Variables --------------------#

# ---------------------------------------------------------------------------------------------- #
PATH = os.getcwd()

myFont =   {'family'  : 'serif',
                'serif'  : 'Arial',
                'size'   : 10}

#%%

'''
TODO: TRANSLATE
'''
class configInfo:
    def __init__(self, caseToRun, config):
        self.caseToRun = caseToRun
        self.title=config['OutputConfig']['caseTitle']
        self.TOPO=True if config['OutputConfig']['TOPO'] else False
        
        self.ROTATE_x=config['OutputConfig']['ALEmeshRotatedAroundXaxis']
        self.TRANSLATE=config['OutputConfig']["Translate"]
        self.SoildEleHeight=config['LidNGate']['ALESoildHeight']
        
        self.Fig1Limits=[[config['Topo']['xCoordMin'],config['Topo']['xCoordMax']],[config['Topo']['yCoordMin'],config['Topo']['yCoordMax']]]
        self.zoomIn=config['OutputConfig']['ZoomInWindow']
        
        self.gridSize=config['OutputConfig']['plotResolution']
        self.topoContourStepSize=config['OutputConfig']['topoContourStepSize']
        self.flowContourStepSize=config['OutputConfig']['flowContourStepSize']
        self.OverallPlotTickerStepSize=config["OutputConfig"]["OverallPlotTickerStepSize"]
        self.ZoomInPlotTickerStepSize=config["OutputConfig"]["ZoomInPlotTickerStepSize"]
        
        self.fps=2
        
        self.TopoFile=config['OutputConfig']["customTopoPath"] if config['OutputConfig']["customTopoPath"] else os.path.join(os.path.dirname(os.getcwd()),'Data','Topography.xyz')
        
        self.dir=os.path.join(os.path.dirname(os.getcwd()),'Output')
        if config['OutputConfig']['D3Plotsubfolder']: self.dir=os.path.join(self.dir,config['OutputConfig']['D3Plotsubfolder'])
        self.d3PlotDataDir=os.path.join(self.dir,'DATA') 
        self.d3PlotDataDir=os.path.join(os.getcwd() ,'DATA') if not os.path.isdir(self.d3PlotDataDir) else self.d3PlotDataDir
        self.ALEContainerFile = os.path.join(self.d3PlotDataDir,'SolidCoords.csv')
        self.DebrisFlowFile = os.path.join(self.d3PlotDataDir,'Solid_Extra_'+str(config['OutputConfig']['SoilExtra'])+'.csv')
        self.figDir=self.CheckFolderElseCreate(os.path.join(os.path.dirname(self.d3PlotDataDir), 'FIGS'))
        print(self.figDir)
        
    def CheckFolderElseCreate(self,folder):
        if not os.path.isdir(folder): os.makedirs(folder)
        return folder
     
    def getOverallFigLimits(self,ALE_limits):
        self.Fig1Limits=[ALE_limits[0],ALE_limits[1],]
         
        
configPath=os.path.join(os.getcwd(),'config.json') 
with open(configPath, 'r') as file:
    data = json.load(file)
    caseToRun=data['caseToRun']
    configObj=configInfo(caseToRun,data[caseToRun])

#%%
def importTopo(filePath):
    # Import the topography data. and Set coord headers
    df = pd.read_csv(filePath, sep = '\t', header=None, names=['x','y','z'] )
    for m in ['x','y','z']: print(m,max(df[m]),min(df[m]))
    return df

def importALESolids(filePath):
    # Import the ALE topography data.
    df = pd.read_csv(filePath, 
                     sep = ',', 
                     comment = '$', 
                     header = None, 
                     names=["ID", "x", "y", "z"])
    axisInterval=5
    ALE_limits=[[np.floor(min(df[m])/axisInterval)*axisInterval,np.ceil(max(df[m])/axisInterval)*axisInterval] for m in ["x","y","z"]]
    configObj.getOverallFigLimits(ALE_limits)
    print("ALE boundaries",ALE_limits)
    return df

def importFlow(filePath):    
    # Import the DEBRIS flow data. Set header from timestep- elemenet ID and debris flow data in each timestep for each element
    df = pd.read_csv(filePath, sep = ',', header=0, index_col=0).T
    df = df.reset_index().rename(columns={"index" : "ID"})
    print("timesteps : ", df.columns)
    return df

# GRID SMOOTHENING NOT SOLVED~
def getXYZ(df, zName, interpolationMethod):
    df2=df.copy()
    # df2['x'] = savgol_filter(df2['x'], window_length=3, polyorder=2)
    # df2['y'] = savgol_filter(df2['y'], window_length=3, polyorder=2)
    # df2[zName] = savgol_filter(df2[zName], window_length=3, polyorder=2)
    
    xRegion=max(df['x']) - min(df['x']); yRegion=max(df['y']) - min(df['y'])
    x = np.linspace(min(df2['x']), max(df2['x']), int(xRegion / (configObj.gridSize*2)))
    y = np.linspace(min(df2['y']), max(df2['y']), int(yRegion / (configObj.gridSize*2)))

    X, Y = np.meshgrid(x, y)
    Z = interpolate.griddata((df2['x'], df2['y']), df2[zName], (X,Y), method=interpolationMethod, fill_value = 0)
    Z[Z < 0.1] = np.nan
    return (X,Y,Z)

def getXYZ_twosetp(df, zName, interpolationMethod):
    # Two Step
    xRegion=max(df['x']) - min(df['x']); yRegion=max(df['y']) - min(df['y'])
    x1 = np.linspace(min(df['x']), max(df['x']), int(xRegion / (configObj.gridSize*2)))
    y1 = np.linspace(min(df['y']), max(df['y']), int(yRegion / (configObj.gridSize*2)))
    
    x2 = np.linspace(min(df['x']), max(df['x']), int(xRegion / configObj.gridSize))
    y2 = np.linspace(min(df['y']), max(df['y']), int(yRegion / configObj.gridSize))
    
    X1, Y1 = np.meshgrid(x1, y1);X2, Y2 = np.meshgrid(x2, y2)
    Z1 = interpolate.griddata((df['x'], df['y']), df[zName], (X1,Y1), method=interpolationMethod, fill_value = 0)
    Z2 = interpolate.griddata((X1.flatten(), Y1.flatten()), Z1.flatten(), (X2,Y2), method="linear", fill_value = 0)
    
    return (X2,Y2,Z2)

# ROTATED THE TOPO
def xRotationalMatrix(xdegree):
    cos_theta = np.cos(xdegree)
    sin_theta = np.sin(xdegree)
    
    return np.array([
        [1, 0, 0],
        [0, cos_theta, -sin_theta],
        [0, sin_theta, cos_theta]
    ])
    
def surfaceLevelLocator(df_rotated):
    # Get back the coordinate of the surface elements without re-rotaing by matching the highest z coord from each rotated x,y coord group, i.e. ox== orignial x coordinate
    df_surfaceXY=df_rotated.loc[df_rotated.groupby(['x', 'y'])['z'].idxmax()]
    return df_surfaceXY[['x','y','z','ox','oy','oz']]
    
# used for debugging
def plotPoint(df,title):
    fig,ax=plt.subplots(figsize=(8,10))
    ax.scatter(df['y'], df['z'], s=1)
    plt.show()
    fig.savefig(f'point{title}.png')
    
def RotateAroundxAxis(df,xdeg):
    df=df.sort_values(by=['x', 'y','z'])
    xyz=df[['x',"y","z"]].to_numpy();remains=df[['ID','filled']].to_numpy()
    
    rotated_xyz = np.dot(xyz, xRotationalMatrix(xdeg))
    rotated_data=np.hstack((rotated_xyz,xyz,remains))
    
    colName=['x','y','z','ox','oy','oz','ID','filled']
    df_rotated=pd.DataFrame(rotated_data,index=df.index,columns=colName)
    
    df_rotated[['x','y','ox','oy','oz']] = df_rotated[['x','y','ox','oy','oz']].map(lambda x: np.round(x, 3))
    df_rotated['z']=df_rotated['z'].apply(lambda x: int(x/configObj.SoildEleHeight)*configObj.SoildEleHeight)
    return df_rotated
    
def getStepSizeForContours(df, zName, step, manualMax=0):
    # For getting the step size for contours, as the name suggests.
    if manualMax == 0:
        max_level = max(df[zName])
    else:
        max_level = manualMax
    min_level = min(df[zName])
    step_level = step

    levels = np.arange(min_level, max_level + step_level, step_level)
    
    return levels

def DepthCalculation(df_ALESoilds,df_debrisFlow,ModelTimeStep):
    df_FilledALE=df_ALESoilds.copy()  
    if (df_debrisFlow.loc[0,ModelTimeStep]== 1) :
        df_FilledALE['filled'] = 1 - df_debrisFlow[ModelTimeStep]
    else:
        df_FilledALE['filled'] = df_debrisFlow[ModelTimeStep]

    if configObj.ROTATE_x: 
        df_FilledALE=RotateAroundxAxis(df=df_FilledALE,xdeg=configObj.ROTATE_x)

    dfout = df_FilledALE.groupby(['x', 'y'], as_index=False)["filled"].sum()
    
    if configObj.ROTATE_x:
        df_surfaceEle=surfaceLevelLocator(df_rotated=df_FilledALE)
        dfout=pd.merge(df_surfaceEle,dfout,left_on=['x','y'],right_on=['x','y'])[['ox',"oy","filled"]].rename(columns={'ox': 'x', 'oy': 'y'})
        
    dfout['filled'] = dfout['filled'] * configObj.SoildEleHeight
    # print('vol','\n',dfout[dfout['filled']>0].head(5))
    return dfout

def GraphicConfig(xlim,ylim,ax,xStepSize=5,yStepSize=10):
    # xlim and y lim are [lower bound, upper bound]
    print(ylim)
    ax.set_xlim([xlim[0],xlim[1]])
    ax.set_ylim([ylim[0],ylim[1]])
    ax.set_aspect('equal')

    # majorTicksX = np.arange(xlim[0],xlim[1], ticksEvery)
    # majorTicksY = np.arange(ylim[0],ylim[1], ticksEvery)
    # ax.set_xticks(majorTicksX)
    # ax.set_yticks(majorTicksY)
    # ax.ticklabel_format(useOffset=False)
    
    ax.yaxis.set_major_locator(ticker.MultipleLocator(yStepSize))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.xaxis.set_major_locator(ticker.MultipleLocator(xStepSize))
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))

    ax.set_xticklabels([abs(int(tick))+configObj.TRANSLATE[0] for tick in ax.get_xticks()])
    ax.set_yticklabels([abs(int(tick))+configObj.TRANSLATE[1] for tick in ax.get_yticks()])
    
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')

#%%
def mainProgram():

    # Import the two dataframes
    df_ALESoilds = importALESolids(configObj.ALEContainerFile)
    df_debrisFlow = importFlow(configObj.DebrisFlowFile)
    
    if configObj.TOPO: 
        print("Topo used-------------------")
        df_topo = importTopo(configObj.TopoFile)
        # Manipulate topo
        (X1,Y1,Z1) = getXYZ(df_topo, 'z', interpolationMethod = 'linear')
        levels3 = getStepSizeForContours(df=df_topo, zName='z', step=configObj.topoContourStepSize)
        # X1 += configObj.TRANSLATE[0]
        # Y1 += configObj.TRANSLATE[1]
    
    # Loop through the selected TIMESTEPS.
    timesteps=df_debrisFlow.columns.tolist()
    for timestep in timesteps:
        if not isinstance(timestep, (int, float)): print(timestep);continue
        print("Runing Timestep",timestep)
        dfout=DepthCalculation(df_ALESoilds,df_debrisFlow,timestep)
        '''
              We need a 2D grid of X, Y and Z points. This does the required interpolation. 
        Bonnie: try other interpolation methods for the topo, and/or
        see if we can do smoothing on the Z-coords for the topo too.
        '''
    
        # plot depth of debris at coord & Blank out the ones with too small fills
        (X2,Y2,Z2) = getXYZ(dfout, 'filled', interpolationMethod = 'cubic')
        # X2 += configObj.TRANSLATE[0];Y2 += configObj.TRANSLATE[1]
        Z2[Z2 < 0.1] =  np.nan
        
        # We need to define how closely spaced the contour lines are. 
        levels2 = getStepSizeForContours(df=dfout, zName='filled', step=configObj.flowContourStepSize, manualMax=5)
         
        fig = plt.figure(figsize=(8, 5), dpi = 450)
        plt.rc('font', **myFont)
        
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        plt.suptitle(configObj.title + ' at $t=$' + str(int(timestep)) + ' s.')
        
        # Plot the two contours of topo.
        if configObj.TOPO:
            ax1.contourf(X1, Y1, Z1, cmap='Greens', levels = levels3, alpha = 0.1)
            ax1.contour(X1, Y1, Z1,colors='k', linestyles='-',  linewidths=1, levels = levels3, alpha = 0.1)
            
            ax2.contourf(X1, Y1, Z1, cmap='Greens', levels = levels3, alpha = 0.1)
            ax2.contour(X1, Y1, Z1,colors='k', linestyles='-',  linewidths=1, levels = levels3, alpha = 0.1)

        CS = ax1.contourf(X2, Y2, Z2, cmap='copper', levels = levels2)
        ax1.contour(X2, Y2, Z2, colors='k', linestyles='--', linewidths=0.5, levels = levels2)
        
        # Plot debris depth legend
        plt.colorbar(CS, label = "Depth (m)", orientation = 'horizontal', aspect = 20, ax=ax1,shrink=0.5)
        
        # Plot debris
        ax2.contourf(X2, Y2, Z2, cmap='copper', levels = levels2)
        ax2.contour(X2, Y2, Z2, colors='k',      linestyles='--', linewidths=0.5, levels = levels2)

        # Config graphs
        # GraphicConfig(xlim=ALE_xlim,ylim=ALE_ylim,ax=ax1,ticksEvery=20)
        GraphicConfig(xlim=configObj.Fig1Limits[0],ylim=configObj.Fig1Limits[1],ax=ax1,xStepSize=configObj.OverallPlotTickerStepSize[0],yStepSize=configObj.OverallPlotTickerStepSize[1])
        GraphicConfig(xlim=configObj.zoomIn[0],ylim=configObj.zoomIn[1],ax=ax2,xStepSize=configObj.ZoomInPlotTickerStepSize[0],yStepSize=configObj.ZoomInPlotTickerStepSize[1])
        
        plt.tight_layout()
        
        # Save figures
        if not os.path.exists(configObj.figDir):
            os.makedirs(configObj.figDir)
            
        pngName = configObj.title + '_output_' + str(int(timestep)).zfill(3) + '_s.png'
        pngPath = os.path.join(configObj.figDir, pngName)
        plt.savefig(pngPath, bbox_inches='tight')
        # plt.close()
        
#%% 
def saveGIF():

    imageFiles = [file for file in os.listdir(configObj.figDir) if file.endswith('.png')]
    gifPath = os.path.join(configObj.figDir, 'combined.gif')

    with imageio.get_writer(gifPath, mode='I', fps = configObj.fps) as writer:
        for imageFile in imageFiles:
            imagePath = os.path.join(configObj.figDir, imageFile)
            image = imageio.imread(imagePath)
            writer.append_data(image)

#%% 

if __name__=="__main__":   
    # Basic Folder settings
    print("Ploting---------------------------------------------------------------")
    # TOPO=False if not os.path.isfile(os.path.join(os.getcwd(),TopoFile)) else True
    mainProgram()
    saveGIF()
