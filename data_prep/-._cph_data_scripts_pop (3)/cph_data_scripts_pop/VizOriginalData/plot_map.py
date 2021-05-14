import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import rasterio 
import rasterio.plot
import numpy as np

def plot_map(cph,regions,waterPath, src,exportPath, year, valMin, val, valmid1, valmid2, valmid3, valmid4,valmid5, valMax, fileName):
    # Read file using gpd.read_file()
    cph_area = gpd.read_file(cph)
    regioner = gpd.read_file(regions)
    waterTif = rasterio.open(waterPath)

    fig, ax = plt.subplots(figsize=(20, 20),facecolor='black') #50, 50
    # Define a normalization from values -> colors
    norm = colors.BoundaryNorm([valMin, val, valmid1, valmid2, valmid3, valmid4, valMax], 6) 
                   
    # Define the colors you want for the layer and the water 
    cmap = ListedColormap(["#00233800","#002338","#004D57","#009994","#80F7FF","#B8FFEA" ]) # transparent 1st 
    cmapWater = ListedColormap(["#00000000","#000000" ])
    
    # Plot the data                       
    regioner.plot(ax=ax, facecolor='#161a1d', edgecolor='None') 
    rasterio.plot.show(waterTif, ax=ax, cmap=cmapWater, zorder=15)
    rasterio.plot.show(src, ax=ax, cmap=cmap, norm=norm, extent= [src.bounds[0],src.bounds[1], src.bounds[2], src.bounds[3]], zorder=10)
    cph_area.plot(ax=ax, facecolor='None', edgecolor='#ffffff', linewidth=.6, alpha=0.8, zorder=11 )

    # Set the plot extent                
    xlim = ([cph_area.total_bounds[0],  cph_area.total_bounds[2]])
    ylim = ([cph_area.total_bounds[1],  cph_area.total_bounds[3]])
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # Add a title
    ax.set_title("{}, {}".format(fileName, year),color="white", fontsize=40)
    # Add a legend for labels
    legend_labels = { "#002338": "{0}-{1}".format(val,valmid1), "#004D57": "{0}-{1}".format(valmid1,valmid2), "#009994": "{0}-{1}".format(valmid2,valmid3), 
    "#80F7FF": "{0}-{1}".format(valmid3,valmid4), "#B8FFEA": "{0}-{1}".format(valmid4,valmid5)} #"#096e6b00": "{0}-{1}".format(valMin,valmid1),

    # Connect labels and colors, create legend and save the image
    patches = [mpatches.Patch(color=color, label=label)
                for color, label in legend_labels.items()]             
    ax.legend(handles=patches, bbox_to_anchor=(0.01, 0.08), loc='center left',facecolor="white",fontsize=20)
    plt.savefig(exportPath +'/{0}_{1}.png'.format( year,fileName), dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(),transparent=True) #
    ax.set_axis_off()
    #plt.show()
    plt.cla()
    plt.close()