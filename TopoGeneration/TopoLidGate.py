# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 17:32:05 2024

@author: Zoe.Chan
"""

#%%
#from .processingMods import processingMods as pm
import configparser
import processingMods as pm
import outputModsTopoLidGate as ooom
import outputMods as omONE

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
OPTION1: Only get HKSAR topo : HKSARTopoOverlay=False; CustomTOPOpath=""
OPTION2: Only get Custom topo: HKSARTopoOverlay=False; CustomTOPOpath="path of custom topo"; Smoothening can be applied: SMOOTHEN =True
OPTION3: Overlay Custom Topo on HKSARTopoOverlay topo: HKSARTopoOverlay=True; CustomTOPOpath="path of custom topo"; Smoothening can be applied: SMOOTHEN =True
'''
HKSARTopo=True ; OverlayCriteria='low' #  Overlay criteria to keep the lowest Z topo {'low','high',}
# CUSTOM_TOPO=True; CustomDIR=r'c:\Users\zoe.chan\Desktop\Zoe\SandyRidge\Model\Data\TestData'
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
        self.gridResolution=0.5
        self.df=df
        
    def getCoords(self):
        return self.xCoords[0],self.xCoords[1],self.yCoords[0],self.yCoords[1]
    
    def getDFxyz(self):
        return self.df[['X', 'Y','Z']]
    
    def putInLidElement(self, lid):
        self.lid=lid
    def getLidElement(self):
        return self.lid[['X', 'Y','Z']]

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

def CountNAN(col):
    nan_count = col.isna().sum()
    print(f"Number of NaN values in 'Column1': {nan_count}")

def MergeTopo(dfBase, OverlayObjs, Criteria='low'):
           
    df=dfBase.copy();df['Lid']=np.nan;df['SurfaceZ']=df['Z']+0.1
    
    for i,Obj in enumerate(OverlayObjs):
        xmin,xmax,ymin,ymax=Obj.getCoords()
        dfBaseRegion=df[(df['X']>xmin)&(df["X"]<xmax)&(df['Y']>ymin)&(df['Y']<ymax)].reset_index(drop=True)
        dfoverlay=Obj.getDFxyz().copy()
        
        tree = cKDTree(dfBaseRegion[['X', 'Y']])
        distances, indices = tree.query(dfoverlay[['X','Y']], k=1)
        dfoverlay['CenterIndex'] = indices
        MinZinGroup = dfoverlay.groupby('CenterIndex')['Z'].min().reset_index()
        MinZinGroup.columns = ['CenterIndex', 'min_z']
        dfBaseRegion=dfBaseRegion.reset_index().rename(columns={'index': 'CenterIndex'})
        
        Merge = pd.merge(dfBaseRegion, MinZinGroup, on='CenterIndex', how='left').dropna(subset="min_z")
        Merge['Z']=Merge.apply(lambda x: min(x['Z'],x["min_z"]) if x['min_z']!=np.nan else x["Z"],axis=1)
        Merge['Lid']=i+10
        
        df_merged = pd.merge(df, Merge, on=['X', 'Y'], how='left', suffixes=('', '_R'))
        df['Z'] = df_merged['Z_R'].combine_first(df['Z'])
        df['Lid']=df_merged["Lid_R"].combine_first(df['Lid'])
        
        topo=df[['X','Y','Z','Lid','SurfaceZ']]
        print(f'{i}------topo-----')
    groups=df.groupby('Lid')
    print([(i,len(dff)) for i, dff in groups] )
    return topo

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
        if OverlayCriteria: 
            topo=MergeTopo(dfBase=dfBase, OverlayObjs=CustomTopoObjs, Criteria=OverlayCriteria)
        
    if (not HKSARTopo) & CUSTOM_TOPO:
        topo=CustomTopoObjs.getDFxyz()
           
    if HKSARTopo & (not CUSTOM_TOPO): 
        topo=GetHKSARtopo()

    if SetZeroReference: SetZeroReferenceGrid(topo) 
    
    groups=topo.groupby("Lid"); print('There is these many groups in compare topo folder',groups.ngroups)
    ooom.writeLSDynaKeyFile(topo, settingsObj)
    topo[['X','Y','Z']].to_csv(os.path.join(os.path.dirname(os.getcwd()),'Data','Topography.xyz'), sep='\t', index=False, header=False)
    

    end_time = time.time()
    print(f"Program runtime: {end_time-start_time} seconds")
