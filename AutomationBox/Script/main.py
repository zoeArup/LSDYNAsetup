# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 09:51:04 2024

@author: Thomas.Bush / Saoirse.Goodwin
"""

#%%
# The settings are contained within 'config.ini'. You need to select the
# case that you want to run there.
#
# Note: 'gridResolution' will pick every nth value if it's an integer,
# or will run interpolation if < 1. 
#
# Modules required: os, numpy, pyarrow, matplotlib, re, pandas, configparser,
# scipy

#%%
import processingMods as pm
import outputMods as om
import visualisationMods as vm
import os
import pandas as pd
#%% Collect program settings.

settingsObj = pm.processConfig()

# Manipulate dataframe.
if settingsObj.customTopo:
    print(settingsObj.customTopo)
    df = pd.read_csv(settingsObj.customTopo, sep = '\t', header=None, names=['X','Y','Z'] )
    for m in ['X','Y','Z']: print(m,max(df[m]),min(df[m]))
else:
    df = pm.getsortedDataframe(settingsObj) 

# Write output file(s).
path=os.path.join(settingsObj.DataPath,'Topography.xyz')
print(df.columns)
df.to_csv(path, sep='\t', index=False, header=False)
om.writeLSDynaKeyFile(df, settingsObj)

# Plot out data (primarily for debugging)
# vm.threeDimPlot(df)
# vm.twoDimColorMap(df)
# %%
