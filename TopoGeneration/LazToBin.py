# pip install laspy
import laspy
import numpy as np
import os

# Open the LAS file

# INPUT=r'\Users\zoe.chan\Desktop\Zoe\SandyRidge\Model\Data\PC_5pix_Trim.las'
DIR=os.getcwd().split('Python')[0]+'Data'
INPUT=os.path.join(DIR,"PC_5pix_Trim.las");print(INPUT)
OUTPUT=os.path.join(DIR,"PC_5pix_Trim.bin")

las = laspy.read(INPUT)
# Extract the point data
points = las.points
# Convert the points to a numpy array
points_array = np.array(points)
# Save the numpy array to a binary file
points_array.tofile(OUTPUT)