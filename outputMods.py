# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 09:50:13 2024

@author: Thomas.Bush / Saoirse.Goodwin
"""

import os
import numpy as np
import pandas as pd
import processingMods as pm

#%%
def writeLSDynaKeyFile(df, settingsObj, partID=1):
    startTime = pm.reportProgress('Writing LS-Dyna key file...')
    
    outputFileName = "{:02d}".format((settingsObj.fileCounter + 1)) + \
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
    
    def writeNodes():
        pd.set_option('max_colwidth', None)
        
        df['index'] = range(1, len(df) + 1)
        
        df["OutputContent"] = \
            df["index"].apply(lambda x: '{:8.0f}'.format(x)) + \
            df["X"].apply(lambda x: '{:16.3f}'.format(x)) + \
            df["Y"].apply(lambda x: '{:16.8f}'.format(x)) + \
            df["Z"].apply(lambda x: '{:16.8f}'.format(x))

        outputContentAsString = df["OutputContent"].to_string(header=False, index=False)
            
        k_file.write("*NODE\n")
        k_file.write(outputContentAsString)
        k_file.write("\n")
        
    def writeShells():
        k_file.write("*ELEMENT_SHELL\n")
        
        n_rows = len(set(df["Y"]))
        n_cols = len(set(df["X"]))
        
        count = 1
        
        # Consider refactoring later.
        for j in np.arange(1, n_rows):
            for i in np.arange(1, n_cols):
                lower_left_ID  = i + (j-1) * n_cols
                lower_right_ID = lower_left_ID + 1
                upper_right_ID = lower_right_ID + n_cols
                upper_left_ID  = upper_right_ID - 1
                toFormat       = '{:8.0f}{:8.0f}{:8.0f}{:8.0f}{:8.0f}{:8.0f}\n'
                k_file.write(toFormat.format(count, partID, lower_left_ID, lower_right_ID,upper_right_ID,upper_left_ID))
                count += 1
                
      
    writeStart()
    # writeControlDataBase()
    # writeMaterials()
    # writeSections()
    # writeHourglass()
    # writeParts()
    # k_file.write('\n')
    writeNodes() 
    writeShells()
    # writeDefines()
    # writeEnd()
    
    k_file.write("*END")  
    
    print("  LS-Dyna key file written as:\n    " + outputFileName)
    print("")
    pm.reportTime(startTime, '  Time to write file: ')