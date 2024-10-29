# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 17:32:05 2024

@author: Zoe.Chan
"""

#%%
#from .processingMods import processingMods as pm
import configparser
import processingMods as pm
import outputMods as om
import visualisationMods as vm
import pandas as pd
import numpy as np
import scipy
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
import time
import os
import glob

'''
OPTION1: Only get HKSAR topo : HKSARTopo=False; CUSTOM_TOPO=False
OPTION2: Only get Custom topo: HKSARTopo=False; CustomTOPOpath="path of custom topo"
OPTION3: Overlay Custom Topo on HKSARTopoOverlay topo: HKSARTopoOverlay=True; CustomTOPOpath="path of custom topo"
'''
HKSARTopo=True ; OverlayCriteria='low' #  Overlay criteria to keep the lowest Z topo {'low','high',}
CUSTOM_TOPO=True; CustomDIR=os.path.join(os.path.dirname(os.getcwd()),"Data")
SetZeroReference=True

# Program Start
config = configparser.ConfigParser()
config.read('config.ini')
settingsObj = pm.processConfig(config)

def GetCSVFiles(dir):
    print(dir)
    return glob.glob(os.path.join(dir, '*.csv'))

def ProcessInputTopo(df):
    # Check for existence of XYZ coord as a correct input file
    if "//X" in df.columns: df.rename(columns={'//X': 'X'}, inplace=True)
    if not all([x in df.columns for x in ['X','Y','Z']]): 
        print("Wrong InputFile!"); return 
    df.dropna(inplace=True)
    df.sort_values(by = ['Y', 'X'])
    return df

class CustomSettings: 
    def __init__(self, PATH):
        if PATH.endswith('.xlsx'): df=pd.read_excel(PATH,engine='python', sep=None)
        else: df=pd.read_csv(PATH,engine='python', sep=None)
        df=ProcessInputTopo(df)
        print(df.shape, df.columns)
        
        self.df_raw = df
        self.xCoords=[df['X'].min(),df['X'].max()]
        self.yCoords=[df['Y'].min(),df['Y'].max()]
        self.size=df.shape
        resolution=(df['X'].max()-df['X'].min())/len(df["X"])
        self.gridResolution=0.5
        self.df=df
        
    def getCoords(self):
        return self.xCoords[0],self.xCoords[1],self.yCoords[0],self.yCoords[1]
    def getDFxyz(self):
        return self.df[['X', 'Y','Z']]
    
    def GridSmoothening(self):
        
        def dataFrameSortingAndCleanup(df):
            df = df.dropna()
            df = df.sort_values(by = ['Y', 'X'])
            df = df.reset_index(drop = True)
            return df

        df= self.df
        xDist = np.diff(self.xCoords)[0]
        yDist = np.diff(self.yCoords)[0]

        xNoOfCells = int(xDist / self.gridResolution)
        yNoOfCells = int(yDist / self.gridResolution)
        
        xi = \
            np.linspace(min(self.xCoords),
                        max(self.xCoords),
                        xNoOfCells)
        yi = \
            np.linspace(min(self.yCoords),
                        max(self.yCoords),
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
        self.df = dfHiRes

        return dfHiRes
    
    def decreaseResolutionMin(self):
        df2=self.df.copy()
        df2= df2.sort_values(by=['Y', 'X']).reset_index(drop=True)
        print(self.gridResolution,0.5/self.gridResolution)
        Xinterval=(self.xCoords[1]-self.xCoords[0])/0.5
        Yinterval=(self.yCoords[1]-self.yCoords[0])/0.5
        interval=max(Xinterval,Yinterval);print(interval)
        print(df2.head(5))
        # Group by every 5 rows and get the row with the minimum 'Z' in each group
        result_df = df2.groupby(df2.index // interval).apply(lambda group: group.loc[group['Z'].idxmin()]).reset_index(drop=True)
        self.df=result_df
        print(f"decrease resolution ing----------------{result_df.shape}")
        return self.df
    
    def Smoothening(self,SmoothenWindowsLength=3):
        df2 = self.df.sort_values(by=['Y', 'X']).reset_index(drop=True)
        df2["Z"] = savgol_filter(df2["Z"], window_length=SmoothenWindowsLength, polyorder=1)
        self.df=df2
        return self.df

def Plot3DofTopoObj(df,focus_obj=settingsObj,title='test'):
    fig,ax = plt.subplot(111, projection='3d')
    xmin,xmax,ymin,ymax=focus_obj.getCoords()
    
    df2=df[(df['X']>xmin)&(df["X"]<xmax)&(df['Y']>ymin)&(df['Y']<ymax)]
    
    ax.scatter(df2['X'], df2['Y'], df2['Z'], c='r', marker='o')
    fig.savefig(f'{CustomDIR}{title}.png')
    plt.show()       

def GetHKSARtopo():   
    df=pm.getsortedDataframe(settingsObj)
    df=ProcessInputTopo(df)
    return df 

def CheckReferencing(baseMap, overlayMap):
    # Check wether overlaymap is on base map if basemap availible
    baseCoord=[baseMap.xCoords,baseMap.yCoords]
    overlayCoord=[overlayMap.xCoords,overlayMap.yCoords]
    def isInRange(target, min, max):
        return min <= target and max >= target
    xInRange=all([isInRange(x,baseCoord[0][0],baseCoord[0][1]) for x in overlayCoord[0]])
    yInRange=all([isInRange(x,baseCoord[1][0],baseCoord[1][1]) for x in overlayCoord[1]])
    return xInRange and yInRange


def MergeTopo(dfBase, OverlayObjs, Criteria='low'):
    df=dfBase.copy()
    for Obj in OverlayObjs:
        xmin,xmax,ymin,ymax=Obj.getCoords()
        dfBaseRegion=df[(df['X']>xmin)&(df["X"]<xmax)&(df['Y']>ymin)&(df['Y']<ymax)].reset_index(drop=True)
        dfoverlay=Obj.getDFxyz().copy()
        
        tree = cKDTree(dfBaseRegion[['X', 'Y']])
        distances, indices = tree.query(dfoverlay[['X','Y']], k=1)
        dfoverlay['CenterIndex'] = indices
        MinZinGroup = dfoverlay.groupby('CenterIndex')['Z'].min().reset_index()
        MinZinGroup.columns = ['CenterIndex', 'min_z']
        
        dfBaseRegion=dfBaseRegion.reset_index().rename(columns={'index': 'CenterIndex'})
        Merge = pd.merge(dfBaseRegion, MinZinGroup, on='CenterIndex', how='left')

        Merge['Z']=Merge.apply(lambda x: min(x['Z'],x["min_z"]) if x['min_z']!=np.nan else x["Z"],axis=1)
        print(Merge[['X', 'Y','Z']])
        
        df_merged = pd.merge(df, Merge, on=['X', 'Y'], how='left', suffixes=('', '_R'))
        df['Z'] = df_merged['Z_R'].combine_first(df['Z'])

    return df[['X','Y','Z']]

def SetZeroReferenceGrid(df):
    x_translate=settingsObj.xCoords[0]
    y_translate=settingsObj.yCoords[0]
    df['X']=df["X"]-x_translate
    df["Y"]=df["Y"]-y_translate
    return df

if __name__ == "__main__":
    start_time = time.time()
    if CUSTOM_TOPO:
        CustomTOPOpathList=GetCSVFiles(CustomDIR)
        print(CustomTOPOpathList)
        CustomTopoObjs=[CustomSettings(customPath) for customPath in CustomTOPOpathList]
    
    if HKSARTopo & CUSTOM_TOPO:
        dfBase=GetHKSARtopo()
        if OverlayCriteria: topo=MergeTopo(dfBase=dfBase, OverlayObjs=CustomTopoObjs, Criteria=OverlayCriteria)
        
    if (not HKSARTopo) & CUSTOM_TOPO:
        topo=CustomTopoObjs.getDFxyz()       
    if HKSARTopo & (not CUSTOM_TOPO): topo=GetHKSARtopo()

    if SetZeroReference: topo=SetZeroReferenceGrid(topo)
    
    topo.to_csv(f"{CustomDIR}ModifiedTopo.csv", index=False)
        
    om.writeLSDynaKeyFile(topo, settingsObj)
    vm.threeDimPlot(topo)
    vm.twoDimColorMap(topo)
    end_time = time.time()
    print(f"Program runtime: {end_time-start_time} seconds")
