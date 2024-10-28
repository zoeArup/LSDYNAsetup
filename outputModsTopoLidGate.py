# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 09:50:13 2024

@author: Thomas.Bush / Saoirse.Goodwin
"""

import os
import numpy as np
import pandas as pd
import processingMods as pm
from scipy import stats

#%%
def writeLSDynaKeyFile(TOPO, settingsObj):
    startTime = pm.reportProgress('Writing LS-Dyna key file...')
    
    outputFileName = "{:02d}".format((settingsObj.fileCounter + 1)*10) + \
        "_" + settingsObj.keyFileName + "_RESN_" + \
            '{0:.2f}'.format(settingsObj.gridResolution) + "m.key"
    outputFilePath = os.path.join(settingsObj.outputPath, outputFileName)
    
    k_file = open(outputFilePath, "w")
    
    
      
    def writeStart():
        k_file.write("*KEYWORD\n")
        k_file.write("*TITLE\n")
        k_file.write(settingsObj.caseToRun + '_' + '{0:.2f}'.format(settingsObj.gridResolution) + '\n')
        
    def writeControlDataBase():
        toWrite = \
'''
*CONTROL_ALE
        -1         1         1      -1.0       0.0       0.0       0.0       0.0
       0.0       0.0       0.0       0.0         0         0       0.0         0
         0         0         0       0.0       0.0         0       0.0       0.0
         0         0         0       0.0
*CONTROL_MPP_DECOMPOSITION_DISTRIBUTE_ALE_ELEMENTS
*CONTROL_OUTPUT
         1         3         0         0       0.0         0         0         0
*CONTROL_TERMINATION
     100.0         0       0.0       0.0       0.0         0
*CONTROL_TIMESTEP
       0.0       0.5         0       0.0       0.0         0         0         0
*DATABASE_GLSTAT
      0.15         1         0         0
*DATABASE_BINARY_D3PLOT
       0.5         0         0         0         0
*DATABASE_EXTENT_BINARY
         0         0         0         0         0         0         0         0
         0         1         0         0         0         0         0         0
         0         0       0.0         0         0         0                    
         0         0         0         0         0
*DATABASE_ALE_MAT
       0.1         0         0'''
        k_file.write(toWrite)
        
    def writeMaterials():
            toWrite = \
'''
*MAT_RIGID
         1    1900.0100000000.       0.3       0.0       0.0       0.0          
       1.0       7.0       7.0
         0       0.0       0.0       0.0       0.0       0.0
*MAT_RIGID_TITLE
Gate
         2    2500.0100000000.       0.3       0.0       0.0       0.0          
       1.0       4.0       7.0
         0       0.0       0.0       0.0       0.0       0.0
*MAT_SOIL_AND_FOAM
         3    1900.0 6000000.012000000.0       0.5       0.0   0.03015    -1.0E8
       1.0       0.0         0
       0.0       0.0       0.0       0.0       0.0       0.0       0.0       0.0
       0.0       0.0
       0.012000000.0       0.0       0.0       0.0       0.0       0.0       0.0
       0.0       0.0
*MAT_VACUUM_TITLE
Air
         4    0.0013'''
            k_file.write(toWrite)
    
    def writeSections():
            toWrite = \
'''
*SECTION_SHELL_TITLE
shell
         1         2       0.0         0       0.0       0.0         0         0
       0.1       0.1       0.1       0.1       0.0       0.0       0.0         0
*SECTION_SOLID
         2        11         0                                     0.0       0.0'''
            k_file.write(toWrite)
    
    def writeHourglass():
            toWrite = \
'''
*HOURGLASS
         1         0    1.0E-8         0       0.0       0.0       0.0       0.0'''
            k_file.write(toWrite)
            
    def writeParts():
            toWrite = \
'''
*PART
Topography
         1         1         1         0         1         0         0         0
*PART
Gate
         2         1         2         0         1         0         0         0
*PART
Lid
         3         1         2         0         1         0         0         0
*PART
Debris
         4         2         3         0         1         0         0         0
*PART
Air
         5         2         4         0         1         0         0         0'''
            k_file.write(toWrite)
    
    def writeDefines():
        toWrite = \
'''*DEFINE_CURVE_TITLE
Gate_lid_opening
         1         0       0.0       0.0       0.0       0.0         0         0
                 0.0                 0.0
                 3.0                 0.0
                3.01               100.0
               100.0               100.0
*DEFINE_CURVE_TITLE
gravity_load
         2         0       0.0       0.0       0.0       0.0         0         0
                 0.0                 0.0
                 2.0                 1.0
               100.0                 1.0
               300.0                 1.0
*DAMPING_RELATIVE
       0.0       1.0         1         2      0.01         0
*BOUNDARY_PRESCRIBED_MOTION_RIGID
         2         3         2         1       0.0         0       0.0       0.0
         3         3         2         1       0.0         0       0.0       0.0
*BOUNDARY_SPC_SET
         1         0         1         1         0         0         0         0'''
        k_file.write(toWrite)
        
    def writeEnd():
        toWrite = \
'''
*CONSTRAINED_LAGRANGE_IN_SOLID_TITLE
         1Debris on Topo                                                        
         1         4         1         1         0         4         2         1
       0.0       0.0       0.0    0.1405      0.01         0         1       0.0
       0.0       0.0       0.0         1       0.0         0         0         0
         0         0         0         0       0.0         0       0.0
       0.0       0.0       0.0       0.0       0.0       0.0                 0.0
*CONSTRAINED_LAGRANGE_IN_SOLID_TITLE
         2Debris on Lid                                                         
         2         4         1         1         0         4         2         1
       0.0       0.0       0.0      0.01      0.01         0         1       0.0
       0.0       0.0       0.0         1       0.0         0         0         0
         0         0         0         0       0.0         0       0.0
       0.0       0.0       0.0       0.0       0.0       0.0                 0.0
*CONSTRAINED_LAGRANGE_IN_SOLID_TITLE
         3Debris on Gate                                                        
         3         4         1         1         0         4         2         1
       0.0       0.0       0.0      0.01      0.01         0         1       0.0
       0.0       0.0       0.0         1       0.0         0         0         0
         0         0         0         0       0.0         0       0.0
       0.0       0.0       0.0       0.0       0.0       0.0                 0.0
*INITIAL_VOLUME_FRACTION_GEOMETRY
         4         1         1         0
         1         0         2       0.0       0.0       0.0
         1         1         0       0.0
         1         1         1       0.0       0.0       0.0
         2         1         0       0.0
         1         1         1       0.0       0.0       0.0
         3         1         0       0.0
*LOAD_BODY_Z
         2       9.8         0
*ALE_MULTI-MATERIAL_GROUP
         5         1
         4         1
*SET_PART_LIST_TITLE
Air and Debris
         2       0.0       0.0       0.0       0.0
         4         5'''
        k_file.write(toWrite)
    
    def ProcessRawDf():
    # return dataframe in XYZ partID: topo with partID=1 and lids with their own ID 
        topo_df=TOPO[['X','Y','Z']]
        topo_df['PartID']=1
        lid_df=TOPO[['X','Y','SurfaceZ',"Lid"]]
        lid_df.rename(columns={'SurfaceZ': 'Z', 'Lid': 'PartID'}, inplace=True)
        
        df=pd.concat([topo_df,lid_df])
        df=df.reset_index(drop=True)
        df['index'] = range(1, len(df) + 1)
        groups=df.groupby("PartID"); print('There is these many groups---',groups.ngroups)
        
        return df
     
    def getNode(df):
        pd.set_option('max_colwidth', None)
        
        df=df.dropna(subset='PartID')
        
        df["OutputContent"] = \
            df["index"].apply(lambda x: '{:8.0f}'.format(x)) + \
            df["X"].apply(lambda x: '{:16.3f}'.format(x)) + \
            df["Y"].apply(lambda x: '{:16.8f}'.format(x)) + \
            df["Z"].apply(lambda x: '{:16.8f}'.format(x))
        return df


    def getShell(dfFull,dfNode):
             
        groups=dfFull.groupby("PartID"); print('There is these many lids',groups.ngroups)
        topo_df=groups.get_group(1)
        nextStartNode=topo_df.shape[0]
        df_lid=dfFull[dfFull['index']>nextStartNode];df_lid.dropna(subset='PartID');df_lid.set_index('index', inplace=True)
        
        n_rows = len(set(topo_df["Y"]));n_cols = len(set(topo_df["X"]))
        ShelltoFormat       = '{:8.0f}{:8.0f}{:8.0f}{:8.0f}{:8.0f}{:8.0f}'
        NodetoFormat	 	= '{:8.0f}{:16.3f}{:16.8f}{:16.8f}'
        TopoShellElement=[];LidShellElement=[];GateShellElement=[];GateNodeElement=[]
        ShellCount = 1; NodeCount=nextStartNode*2
        
        # get in Topo Shell
        print('Topo:     ',n_cols,n_rows,'-----',topo_df.shape)
        for j in np.arange(1, n_rows):
            for i in np.arange(1, n_cols):
                lower_left_ID  = i + (j-1) * n_cols
                lower_right_ID = lower_left_ID + 1
                upper_right_ID = lower_right_ID + n_cols 
                upper_left_ID  = upper_right_ID - 1
                content=ShelltoFormat.format(ShellCount, 1, lower_left_ID, lower_right_ID,upper_right_ID,upper_left_ID)
                TopoShellElement.append(content);ShellCount+=1
        
        print("ShellCount of topo", TopoShellElement)
        
        # get in lids Shell
        startNode=nextStartNode
        
        # Check whether there is part ID for the shell, take in when one node of the 4 cover landslides
        # Remove overlap element between parts
        def mode_partID(elementList):
            partIDList=[df_lid.loc[x,'PartID'] for x in elementList]
            partIDList = np.array(partIDList)
            nonNaID=partIDList[~np.isnan(partIDList)].tolist()
            if len(nonNaID)==4:
            # if len(nonNaID)>2:
                PartID=nonNaID[0]
                if all(ID == PartID for ID in nonNaID): return PartID 
                else: return 0
            else: return 0
        
        for j in np.arange(1, n_rows):
            for i in np.arange(1, n_cols):
                lower_left_ID  = i + (j-1) * n_cols+startNode
                lower_right_ID = lower_left_ID + 1
                upper_right_ID = lower_right_ID + n_cols 
                upper_left_ID  = upper_right_ID - 1
                shellELementList=[lower_left_ID,lower_right_ID,upper_right_ID,upper_left_ID]
                partID=mode_partID(elementList=shellELementList)
                # partID= df_lid.loc[upper_left_ID,'PartID']
                
                if partID>1:
                    content=ShelltoFormat.format(ShellCount, partID, lower_left_ID, lower_right_ID,upper_right_ID,upper_left_ID)
                    LidShellElement.append(content);ShellCount+=1
                else: continue
                
        # Ready to get in gate : find all gate node-> find all edge-> extrude down
                
        df_lidShell=pd.DataFrame(LidShellElement,columns=["OutputContent"])
        df_lidShell[['shellCount','partID','LL', 'LR', 'UR','UL']] = df_lidShell['OutputContent'].str.split(' ', expand=True)
        LidShellGroup=df_lidShell.groupby('partID');print('Num Lid group: ',LidShellGroup.ngroups)
        LengthOfExtrude=10; ExtrudeVector=np.array([0,0,-0.5])
        
        
        '''
        1. loop for all boundaryshell create shell and node for each edges, locate by index 
        
        
        '''
        def ExtrudeGate(node1,node2,startingNode):
            global ShellCount
            # node contain x,y,z in np.array() TODO: locate node 1 2 details from lid by df_LidBoundaryNodeDetail.loc[node1] given that node 1 is index 
            '''
            1--2
            |  |
            4--3
            '''
            NodeIndex1=node1.name;NodeIndex2=node2.name; partID=node1['partID']
            for i in range(1,LengthOfExtrude):
                x1,y1,z1=np.array(node1[-3:])+ExtrudeVector*i;NodeIndex4=startingNode+2*i-1
                x2,y2,z2=np.array(node2[-3:])+ExtrudeVector*i;NodeIndex3=NodeIndex4+1
                GateNodeElement.append(NodetoFormat.format(NodeIndex4,x1,y1,z1)) 
                GateNodeElement.append(NodetoFormat.format(NodeIndex3,x2,y2,z2)) 
                GateShellElement.append(ShelltoFormat.format(ShellCount,partID,NodeIndex1,NodeIndex2,NodeIndex3,NodeIndex4))
                NodeIndex1=NodeIndex4;NodeIndex2=NodeIndex3
                ShellCount=ShellCount+1
                
                
             
        def getBoundarySequence(row):
            BoundaryNodesInBoundaryShell
            return 
        
        for partID, df_partLidNode in LidShellGroup:
            print('Ready to find gate of lid with partID-------',partID)
            startNode+=nextStartNode
            # find the boundaryNodes
            LidNodesValueCount= df_partLidNode[['LL', 'LR', 'UR','UL']].stack().value_counts()
            boundaryNodesList=LidNodesValueCount[LidNodesValueCount < 4].index.tolist(); print('for Lid', partID, 'there is ', len(boundaryNodesList),'boundaryNodesList')
            nextStartNode=len(boundaryNodesList)*10
            # Find all shell containing boundary shell
            df_LidBoundaryShell=df_partLidNode[df_partLidNode.apply(lambda row: any(NodeCount in boundaryNodesList for NodeCount in row), axis=1)]
            df_LidBoundaryNodeDetail=df_lid.loc[boundaryNodesList] # index, x,y,z, partID
            df_LidBoundaryNodeDetail['partIndex']=range(1,len(df_LidBoundaryNodeDetail))
            # Find Sequence of shell edge


        ShellElement = TopoShellElement+LidShellElement+GateShellElement 
        print(ShellCount,'here is the ShellCount after writng all shit')
        dfShell=pd.DataFrame(ShellElement,columns=["OutputContent"])
        return dfShell,dfNode

    def writeInContent(df_shell,df_node):
        NodeContent = df_node["OutputContent"].to_string(header=False, index=False)
        ShellContent = df_shell["OutputContent"].to_string(header=False, index=False)
            
        k_file.write("*NODE\n")
        k_file.write(NodeContent)
        k_file.write("\n")
        k_file.write("*ELEMENT_SHELL\n")        
        k_file.write(ShellContent)
        k_file.write("\n")
        
    def writeFile():
        writeStart()
        print("Write In details-------------------")
        dfFull=ProcessRawDf()   
        df_node=getNode(df=dfFull)   
        df_shell,df_node=getShell(df=dfFull,dfNode=df_node)
        writeInContent(df_shell,df_node)
   
    writeFile()
   
    # writeControlDataBase()
    # writeMaterials()
    # writeSections()
    # writeHourglass()
    # writeParts()
    # k_file.write('\n')

    # writeDefines()
    # writeEnd()
    
    k_file.write("*END")  
    
    print("  LS-Dyna key file written as:\n    " + outputFileName)
    print("")
    pm.reportTime(startTime, '  Time to write file: ')