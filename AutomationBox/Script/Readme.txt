Config.json and Scripts should always stay in the same folder

Instruction of Full Workflow :
1. Setup File Structure within project folder
	a. Script; Data folder-> copyin all script into Script Folder
2. Setup Python env
	a. conda activate "env" (e.g. command: conda activate spyder-env-new)
	b. cd to script folder (e.g. cd C:\Users\zoe.chan\Desktop\Zoe\LS-DYNA\AutomationBox\Script)
3. Setup config.json inside script folder [see later section for details]
4. SETUP PRIMER .key file to generate topography
	a. command: python main.py
	b. find generated key file in output folder 
5. SETUP PARTS and other model settings
	open key file, run javascripts:
	i. run setUpParts.js
	ii. run LS-Dyna_Terrain_Setup.js
	iii. [if parts are not visible in interface, just randomly click update in part]
	iv. save file
6. Run LSDYNA for result
7. RETRIEVE RESULTS
	a. open result d3plot file
	b. run javascripts: ExtractAlld3PlotData.js -> DATA folder will pop up in the model folder
	c. in python env, run script plotContours.py (command: python main.py) -> results will pop up in FIGS folder in the model folder


Instruction for Separated Workflow for SETUP PART OR RETRIEVE RESULTS:
1. Update config.json accordingly and put with scripts
2. SETUP PART
	a. run setUpParts.js, LS-Dyna_Terrain_Setup.js
3. RETRIEVE RESULTS
	a. put scripts [ExtractAlld3PlotData.js; plotContours.py; config.json] within the model folder
	b. run ExtractAlld3PlotData.js, plotContours.py accordingly

Setup config.json
1. General Instruction"
	a. for Custom Path: Put in "" if custom path is not used, default folder structure will be applied
	b. start a new block of input with same structures under project name-> update "caseToRun" with the project name 
2. Explanation for setup parameter (# explanation):
-----------------------------------------------------------------------------------------------------------------------
{
"caseToRun":"SandyRidge", 		# Project Name of case to be modelled

					# Below structure should be kept for new cases
"SandyRidge":{				# Start with Project Name - same as "caseToRun"

    "Topo":{				# Used for topo generation 
        "xCoordMin": 829940,
        "xCoordMax": 830080,
        "yCoordMin": 842800,
        "yCoordMax": 843080,
        "gridResolution": 0.5,
        				# Source of topo: 
        "parquetFilePath":"",		# Full path should be input, -*if not used, please keep as ""
        "customTopoPath":""		# Full path in format .csv or xyz can be set- *if not used, please keep as ""
        },

    "LidNGate":{							# Used for topo generation Setup parts
        "numberOfSources":2,
        "VolumeSource" : [230,300],					# Specify volume for each source 
        "boxSize": [[12,8],[15,10]],					# Specify dimension for each source [[source1 length, width]]
        "SourceCentreCoords" : [[830000,842900],[829980,842900]],	# Specify CentreCoords for each source [[source1 x, y]]
        "ALESoildHeight":0.5						# Specify ALE mesh height used for source
        },

    "SoilParameters":{			# Used for topo generation Setup parts
        "BasalFrictionAngle":34,
        "InternalFrictionAngle" :34,
        "cohesion":1,
        "DV2":0.02 
    },

    "OutputConfig":{			# Used for extracting d3plot data and plot graph
        "TOPO": 1,			# if Topo is used for the base of plot: 1, else put 0
        "customTopoPath":"",		# Full path in format .csv or xyz can be set- *if not used, please keep as ""
        "caseTitle":"SandyRidge",	# Project Name of case to be modelled
        "D3Plotsubfolder":"v3",		# subfolder inside output folder containing results of d3plot- *if not used, please keep as ""
					
        "TimeStepOfOutput":2,		# logout data every no# frame
        "SoilExtra":3,			# Specify debris material
        "ALEmeshRotatedAroundXaxis":0,	# Specify the angle of ALE mesh plane tilting around x axis 

					# Specify configuration of plots output
        "topoContourStepSize" : 10,
        "flowContourStepSize" : 1 ,
        "plotResolution":1,
        "Translate":[0,0],		# This only modify plot ticker label without translating real data

        "ZoomInWindow":[[829960,830020],[842880,842920]], # Specify focused arrange of result
        "OverallPlotTickerStepSize":[20,50],
        "ZoomInPlotTickerStepSize":[5,20]

    }
    }
}

General Remark for debugging:
1. Check existence of files: 
	a. correct folder structure?
	b. correct file content format? e.g. in topography.xyz only should contain 3 columns
2. No content in plots output -> check inputs under OutputConfig section in config.json 
	a. check correct input for plot range e.g  ZoomInWindow
	b. modify parameters related to plot configuration, if step size is too large or small, or resolution is not high enough







 






	