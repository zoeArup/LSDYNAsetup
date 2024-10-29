# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 09:51:04 2024

@author: Thomas.Bush / Saoirse.Goodwin
"""

import matplotlib.pyplot as plt

#%%
def threeDimPlot(df):
    # Create a new figure for plotting
    fig = plt.figure()

    # Add a 3D subplot
    ax = fig.add_subplot(111, projection='3d')

    # Scatter plot using XYZ coordinates from the DataFrame
    ax.scatter(df['X'], df['Y'], df['Z'])

    # Set labels for axes
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    # Show the plot
    plt.show()

#%%
def twoDimColorMap(df):
    # Create a 2D scatter plot
    plt.scatter(df['X'], df['Y'], c=df['Z'], cmap='viridis')

    # Add a color bar to the right of the plot
    plt.colorbar(label='Elevation')

    # Set labels for axes
    plt.xlabel('X')
    plt.ylabel('Y')

    # Set a title for the plot
    plt.title('2D Scatter Plot Coloured by Elevation')

    # Show the plot
    plt.show()
 