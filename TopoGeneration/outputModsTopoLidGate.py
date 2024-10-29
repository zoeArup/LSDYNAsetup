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

class ShellCountClass:
    def __init__(self):
        self.ShellCount=1
    def add(self):
        self.ShellCount+=1   
    def getCount(self):
        return self.ShellCount 
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
     
    def getNodeString(df):
        pd.set_option('max_colwidth', None)
        NodetoFormat	 	= '{:8.0f}{:16.3f}{:16.8f}{:16.8f}'
        
        # df["OutputContent"] = \
        #     df.index.map(lambda x: '{:8.0f}'.format(x)) + \
        #     df["X"].apply(lambda x: '{:16.3f}'.format(x)) + \
        #     df["Y"].apply(lambda x: '{:16.8f}'.format(x)) + \
        #     df["Z"].apply(lambda x: '{:16.8f}'.format(x))
        df["OutputContent"] = df.apply(lambda row: NodetoFormat.format(row.name,row['X'],row['Y'],row['Z']),axis=1)
        return df[["OutputContent"]]

    def getShell(dfFull):
             
        groups=dfFull.groupby("PartID"); print('There is these many lids',groups.ngroups-1)
        topo_df=groups.get_group(1); 
        topo_df.set_index('index', inplace=True)
        nextStartNode=topo_df.shape[0]
        df_lid=dfFull[dfFull['index']>nextStartNode];df_lid.dropna(subset='PartID');df_lid.set_index('index', inplace=True)
        
        n_rows = len(set(topo_df["Y"]));n_cols = len(set(topo_df["X"]))
        ShelltoFormat       = '{:8.0f}{:8.0f}{:8.0f}{:8.0f}{:8.0f}{:8.0f}'
        NodetoFormat	 	= '{:8.0f}{:16.3f}{:16.8f}{:16.8f}'
        TopoShellElement=[];LidShellElement=[];GateShellElement=[]
        GateNodeElement=[];LidNodeElement=set()
        # ShellCount = 1; NodeCount=nextStartNode*2
        ShellCountObj=ShellCountClass()
        
        # get in Topo Shell
        print('Topo:     ',n_cols,n_rows,'-----',topo_df.shape)
        for j in np.arange(1, n_rows):
            for i in np.arange(1, n_cols):
                lower_left_ID  = i + (j-1) * n_cols
                lower_right_ID = lower_left_ID + 1
                upper_right_ID = lower_right_ID + n_cols 
                upper_left_ID  = upper_right_ID - 1
                content=ShelltoFormat.format(ShellCountObj.getCount(), 1, lower_left_ID, lower_right_ID,upper_right_ID,upper_left_ID)
                TopoShellElement.append(content);ShellCountObj.add()
        
        print("ShellCount of topo", ShellCountObj.getCount())
        
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
                    content=ShelltoFormat.format(ShellCountObj.getCount(), partID, lower_left_ID, lower_right_ID,upper_right_ID,upper_left_ID)
                    LidShellElement.append(content);ShellCountObj.add()
                    LidNodeElement.update(shellELementList)
                else: continue
                
        df_lid=df_lid.loc[list(LidNodeElement)]
        # Ready to get in gate : find all gate node-> find all edge-> extrude down
        
        '''
        TODO: Remove single elements ones, fk lah
        '''
        
        df_lidShell=pd.DataFrame(LidShellElement,columns=["OutputContent"])
        def decompose_string(s):
            return [int(s[i:i+8].strip()) for i in range(0, len(s), 8)]
        df_lidShell[['shellCount','partID','LL', 'LR', 'UR','UL']]= df_lidShell['OutputContent'].apply(decompose_string).apply(pd.Series)
        # df_lidShell[['shellCount','partID','LL', 'LR', 'UR','UL']] = df_lidShell['OutputContent'].str.split(' ', expand=True)
        LidShellGroup=df_lidShell.groupby('partID');print('Num Lid group: ',LidShellGroup.ngroups)
        LengthOfExtrude=10; ExtrudeVector=np.array([0,0,-0.5])
        uglyLidShell=[]

        def ExtrudeNodes(nodeRow,startingNode):
            partNodeIndex=nodeRow['partIndex'] 
            for i in range(1,LengthOfExtrude):
                nodeCount=startingNode+partNodeIndex*(LengthOfExtrude-1)+i+1 # starting Node of the part + before there are already num of node created + the nth node in extruded form the specific node
                x,y,z=np.array([nodeRow['X'],nodeRow['Y'],nodeRow['Z']])+ExtrudeVector*i
                GateNodeElement.append(NodetoFormat.format(nodeCount,x,y,z)) 
        
        def CreateGateShellFromEdgeNodes(node1,node2,partID,startingNode):
            # node contain x,y,z in np.array() TODO: locate node 1 2 details from lid by df_LidBoundaryNodeDetail.loc[node1] given that node 1 is index 
            '''
            1--2
            |  |
            4--3
            '''
            partNodeIndex1=df_LidBoundaryNodeDetail.loc[node1,'partIndex']
            partNodeIndex2=df_LidBoundaryNodeDetail.loc[node2,'partIndex']
            NodeIndex1,NodeIndex2=node1,node2
            for i in range(1,LengthOfExtrude):
                NodeIndex4=startingNode+partNodeIndex1*(LengthOfExtrude-1)+i+1
                NodeIndex3=startingNode+partNodeIndex2*(LengthOfExtrude-1)+i+1
                GateShellElement.append(ShelltoFormat.format(ShellCountObj.getCount(),partID,NodeIndex1,NodeIndex2,NodeIndex3,NodeIndex4))
                NodeIndex1=NodeIndex4;NodeIndex2=NodeIndex3
                ShellCountObj.add()
                
        def ExtrudeGate(row,partID,startingNode):
            # row with node at 'LL', 'LR', 'UR','UL'
            checkBoundaryNode=[NodeCount in boundaryNodesList for NodeCount in row]
            BoundaryNodeCount=checkBoundaryNode.count(True)
            if BoundaryNodeCount==4: uglyLidShell.append(row.name)
            if BoundaryNodeCount>1 and BoundaryNodeCount<4:
                checkBoundaryNode.append(checkBoundaryNode[0]) # making sure it form a loop
                # slice through the list, if two true found, it is edge and return the node
                edgeList=[[row[i],row[(i+1)%4]] for i in range(len(checkBoundaryNode)-1) if [checkBoundaryNode[i],checkBoundaryNode[i+1]].count(True)==2]
                for i in edgeList:
                    node1,node2=i
                    CreateGateShellFromEdgeNodes(node1,node2,partID,startingNode)
                
        for partID, df_partLidShell in LidShellGroup:
            print('Ready to find gate of lid with partID-------',partID)
            startNode+=nextStartNode
            # find the boundaryNodes: appearing less than 4 times in the shells-> boundary nodes
            LidNodesValueCount= df_partLidShell[['LL', 'LR', 'UR','UL']].stack().value_counts()
            print('this is the number of node in ', partID, len(LidNodesValueCount))
            boundaryNodesList=LidNodesValueCount[LidNodesValueCount < 4].index.tolist(); print('for Lid', partID, 'there is ', len(boundaryNodesList),'boundaryNodesList')
            nextStartNode=len(boundaryNodesList)*(LengthOfExtrude-1) # give the end node for starting node of next part
            # Ready to write in node for extruded boundary nodes
            df_LidBoundaryNodeDetail=df_lid.loc[boundaryNodesList] # index, x,y,z, partID
            df_LidBoundaryNodeDetail['partIndex']=range(0,len(df_LidBoundaryNodeDetail)) # this is the index for locating the nodes within the part
            df_LidBoundaryNodeDetail.apply(lambda row: ExtrudeNodes(row,startNode),axis=1) # write nodes
            # Find the nodes along the boundary shell: find the edge, extrude by appending shell element 
            df_partLidShell[['LL', 'LR', 'UR','UL']].apply(lambda row: ExtrudeGate(row,partID,startNode) , axis=1)
            
        print(len(uglyLidShell)) ;  LidShellElement=df_lidShell.drop(index=uglyLidShell)['OutputContent'].tolist()
            # Find Sequence of shell edge

        print(ShellCountObj.getCount(),'here is the ShellCount after writng all shit')
        ShellElement = TopoShellElement+LidShellElement+GateShellElement 
        dfShell=pd.DataFrame(ShellElement,columns=["OutputContent"])
        
        dfTopoStr=getNodeString(df=topo_df)
        dfLidStr=getNodeString(df_lid)
        dfGateStr=pd.DataFrame(GateNodeElement,columns=["OutputContent"])
        dfNode=pd.concat([dfTopoStr,dfLidStr,dfGateStr])
        
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
        # df_node=getNode(df=dfFull)   
        df_shell,df_node=getShell(dfFull)
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