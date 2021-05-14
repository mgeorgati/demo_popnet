import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import rasterio 
from rasterio.plot import show

year_list=[2012,2014,2016,2018]
paths=[]

def read_txt(txt_path):
    text = open(txt_path).read()
    
    new_text = text.replace(".tif", ".tif\n")
    lines_of_text= new_text.splitlines()
    
    names=[]
    for i in range(len(lines_of_text)):
        name= lines_of_text[i].split("\\")[-1].split('.tif')[0]
        names.append(name)
    return names

def vizInput(tif_path, txt_path, trialNo, base_dir, cph_area,regioner, waterPath):
    cols = 7
    rows = 5

    fig, axs = plt.subplots(rows,cols, figsize=(20,10))
    fig.subplots_adjust(hspace = .02, wspace=.5)
    axs = axs.ravel()
    
    src = rasterio.open(tif_path)
    array = src.read()
    channels= array.shape[0]
    #print(channels)
    titles = read_txt(txt_path)
    
    for j in range(0,channels):
        
        #Get and Plot all channels
    
        cmap = ListedColormap(["#00233800","#002338","#004D57", "#009994", "#80F7FF", "#B8FFEA"]) # yellow:everthing lower than 10 #002338: 10-30 red: everthing higher than 30
        norm = colors.BoundaryNorm([ -100,1, 10, 20, 30,50,100], 6) 
        
        # Add a legend for labels
        legend_labels_Pred = { "#002338": "{0}-{1}".format(1,10), "#004D57": "{0}-{1}".format(10,20), "#009994": "{0}-{1}".format(20,30),
        "#80F7FF": "{0}-{1}".format(30,50), "#B8FFEA": ">50"} #"Red":"Min:{0}, Max:{1}".format(valMinP,valMaxP)
            
        # Connect labels and colors, create legend and save the image
        patches_Pred = [mpatches.Patch(color=color, label=label)
                        for color, label in legend_labels_Pred.items()]
        #print(pred_paths[j])
        show((src,j+1), ax=axs[j], cmap=cmap, norm=norm, zorder=2)
        cph_area.plot(ax=axs[j], facecolor='None', edgecolor='#FFFFFF', linewidth=.2, alpha=0.3, zorder=1 )
        regioner.plot(ax=axs[j], facecolor='#161a1d', edgecolor='None',zorder=0, alpha=0.8 )
        axs[j].legend(handles=patches_Pred, bbox_to_anchor=(0.01, 0.08), loc='center left',facecolor="white",fontsize=2)
        axs[j].set_title('{}'.format(titles[j]), color="black", fontsize=4)
        axs[j].set_axis_off()      

        xlim = ([cph_area.total_bounds[0],  cph_area.total_bounds[2]])
        ylim = ([cph_area.total_bounds[1],  cph_area.total_bounds[3]])
        axs[j].set_xlim(xlim)
        axs[j].set_ylim(ylim)
            
            
    plt.savefig(base_dir + '/summarizeResults/InputMatrixes/{}.png'.format(trialNo), dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(),transparent=True)
    #plt.show()
    
    
