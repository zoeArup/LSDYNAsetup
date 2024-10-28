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
import configparser

import processingMods as pm
import outputMods as om
import visualisationMods as vm

#%% Collect program settings.
config = configparser.ConfigParser()
config.read('config.ini')
settingsObj = pm.processConfig(config)

# Manipulate dataframe.
df = pm.getsortedDataframe(settingsObj)

# Write output file(s).
om.writeLSDynaKeyFile(df, settingsObj)


# Plot out data (primarily for debugging)
# vm.threeDimPlot(df)
# vm.twoDimColorMap(df)