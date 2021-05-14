import os
import sys
import numpy as np
from numpy import inf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import rasterio 
from rasterio.plot import show
import geopandas as gpd
import numpy as np

def calc_dif(directory,trialNo,country,year,extTrial,city,base_dir):
    pred_path = directory + '/{0}_{1}/{0}_{1}_{3}/outputs/predictions/pred_{2}.tif'.format(trialNo, country, year, extTrial)
    real_path = base_dir + '/data/{0}/{1}/{2}_proj/{3}.tif'.format(city,trialNo,country,year)
    src_real = rasterio.open(real_path)
    src_pred = rasterio.open(pred_path)

    array_real= src_real.read(1)
    array_pred = src_pred.read(1)
    dif =  array_real - array_pred
    with rasterio.open(pred_path) as src:
        new_dataset = rasterio.open(
            directory + '/{0}_{1}/{0}_{1}_{3}/output/dif_{0}_{1}_{2}.tif'.format(trialNo,country,year, extTrial),
            'w',
            driver='GTiff',
            height=dif.shape[0],
            width=dif.shape[1],
            count=1,
            dtype=dif.dtype,
            crs=src.crs,
            transform= src.transform
            )
    new_dataset.write(dif, 1)
    new_dataset.close()

def calc_AcPerc(directory,trialNo,country,year, extTrial,city, base_dir):
    pred_path = directory + '/{0}_{1}/{0}_{1}_{3}/output/dif_{0}_{1}_{2}.tif'.format(trialNo,country,year, extTrial)
    real_path = base_dir + '/data/{0}/{1}/{2}_proj/{3}.tif'.format(city,trialNo,country,year)
    
    src_real = rasterio.open(real_path)
    src_pred = rasterio.open(pred_path)

    array_real= src_real.read(1)
    array_pred = src_pred.read(1)
    SD = np.sum(array_real)

    #print(array_real)
    #divide calculation--> anywhere 'where' b does not equal zero. When b does equal zero, then it remains unchanged from whatever value you originally gave it in the 'out' argument
    AcPerc = np.divide((array_pred * array_real), SD ) #np.zeros(array_pred.shape, dtype=float) #out=array_pred, where=array_real!=0
    AcPerc = AcPerc * 100
    #♫print(AcPerc)
    with rasterio.open(pred_path) as src:
        new_dataset = rasterio.open(
            directory + '/{0}_{1}/{0}_{1}_{3}/output/AcPerc_{0}_{1}_{2}.tif'.format(trialNo,country,year, extTrial),
            'w',
            driver='GTiff',
            height=AcPerc.shape[0],
            width=AcPerc.shape[1],
            count=1,
            dtype=AcPerc.dtype,
            crs=src.crs,
            transform= src.transform
            )
    new_dataset.write(AcPerc, 1)
    new_dataset.close()

def viz_AcPerc(trialNo, base_dir, cph_area, regioner, waterTif, country, Ac_Perc_paths, extTrial,city): 
    cols = 2
    rows = 2

    fig, axs = plt.subplots(rows,cols, figsize=(10,10),  subplot_kw = dict( facecolor = "black"))
    fig.subplots_adjust(hspace = .01, wspace=.01)
    axs = axs.ravel()
            
    year=2010
    for j in range(len(Ac_Perc_paths)):
        year +=2
        #Get and Plot Acccuracy Percentage
        src_AcPerc= rasterio.open(Ac_Perc_paths[j])

        cmapWater = ListedColormap(["black","#36454f" ])
        rasterio.plot.show(waterTif, ax=axs[j], cmap=cmapWater, zorder=1)
        #cph_area.plot(ax=axs[j], facecolor='None', edgecolor='#ffffff', linewidth=.6, alpha=0.8, zorder=11 )
        
        cmap_AcPerc = ListedColormap(["#00383D","#006D77","#83C5BE","#bcf5ef","#EDF6F900","#fae3dc","#E29578","#974220", "#5e1617"])#
        norm_AcPerc = colors.BoundaryNorm([-500, -10, -5, -1,-0.01, 0.01, 1, 5, 10,  500], 9)
        legend_labels_AcPerc = {"#00383D": "<{0}".format(-10), "#006D77": "{0}-{1}".format(-10, -5), "#83C5BE": "{0}-{1}".format(-5, -1), "#bcf5ef": "{0}-{1}".format(-1, -0.01),
                            "#EDF6F900": "{0}-{1}".format(-0.01,0.01), "#fae3dc": "{0}-{1}".format(0.01, 1), 
                        "#E29578": "{0}-{1}".format(1, 5),"#974220": "{0}-{1}".format(5,10), "#5e1617": ">{0}".format(10)} 

        patches_AcPerc = [mpatches.Patch(color=color, label=label)
                            for color, label in legend_labels_AcPerc.items()]
        show((src_AcPerc,1), ax=axs[j], cmap=cmap_AcPerc, norm=norm_AcPerc, zorder=2)   
        cph_area.plot(ax=axs[j], facecolor='None', edgecolor='white', linewidth=.2 , alpha=0.6, zorder=2 )
        #regioner.plot(ax=axs[j], facecolor='None', edgecolor='None', zorder=0, alpha=0.9 )
        axs[j].legend(handles=patches_AcPerc, bbox_to_anchor=(0.01, 0.08), loc='center left',facecolor="white",fontsize=3)
        axs[j].set_title('Significance of Error (%): {0},{1}'.format(country,year), color="black", fontsize=9)
        axs[j].set_axis_off()

        xlim = ([cph_area.total_bounds[0],  cph_area.total_bounds[2]])
        ylim = ([cph_area.total_bounds[1],  cph_area.total_bounds[3]])
        axs[j].set_xlim(xlim)
        axs[j].set_ylim(ylim)
                       
    plt.savefig(base_dir + '/experiments/{3}/{0}/{0}_{1}/{0}_{1}_{2}/output/ErrorPerc_{0}_{1}.png'.format(trialNo,country, extTrial,city),  dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(),transparent=True) #{0}_{1}/{0}_{1}_{2}/output
    #plt.show()
    plt.cla()
    plt.close()


def makeLineDiagrams(trialNo, base_dir, country, extTrial,city):
    df = pd.DataFrame()
    hist_path = base_dir + '/data/{0}/{1}/{2}'.format(city,trialNo,country)
    for file in os.listdir(hist_path):
        if file.endswith('.tif'):
            
            hist_year = file.split(".tif")[0]
            hist_data = base_dir + '/data/{0}/{1}/{2}/{3}'.format(city,trialNo,country,file)
            src_hist_data = rasterio.open(hist_data)
            array_hist_data = src_hist_data.read(1)
            pop_hist_data = np.sum(array_hist_data)
            df.at[hist_year, '{}_hist'.format(country)] = pop_hist_data
    
    gtruth_path = base_dir + '/data/{0}/{1}/{2}_proj'.format(city,trialNo,country)
    for i in os.listdir(gtruth_path):
        if i.endswith('.tif'):
            year = i.split(".tif")[0]
            gtruth_data = gtruth_path + '/{0}'.format(i)
            src_ground_truth_path = rasterio.open(gtruth_data)
            array_ground_truth_path = src_ground_truth_path.read(1)
            pop_ground_truth_path = np.sum(array_ground_truth_path)
            df.at[year, '{}_hist'.format(country)] = pop_ground_truth_path
    
    proj_path = base_dir + '/experiments/{3}/{0}/{0}_{1}/{0}_{1}_{2}/outputs/predictions'.format(trialNo,country, extTrial,city)
    for k in os.listdir(proj_path):
        if k.endswith('.tif'):
            
            year = k.split(".tif")[0].split("pred_")[1]
            proj_data = proj_path + '/{0}'.format(k)
            src_proj_path  = rasterio.open(proj_data)
            array_proj_path  = src_proj_path.read(1)
            pos_array_proj_path = array_proj_path[array_proj_path > 0]
            pop_proj_path  = np.sum(pos_array_proj_path)
            df.at[year, '{}_proj'.format(country)] = pop_proj_path
    #print(df)
    df.index.name = "year"
    df.plot(kind="line", title= "Comparison of Sum Population (only positive)")
    plt.xlabel("Year")
    plt.ylabel("Population")
    save_path = base_dir + '/experiments/{3}/{0}/{0}_{1}/{0}_{1}_{2}/output'.format(trialNo,country, extTrial,city)
    plt.savefig(save_path + '/pred_gtruth_comparison.png', dpi=300, bbox_inches='tight', transparent=True) #{0}_{1}/{0}_{1}_{2}/output
    #plt.show()
    plt.cla()
    plt.close()




        

