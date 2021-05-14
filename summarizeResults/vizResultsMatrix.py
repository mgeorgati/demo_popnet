import os
import sys
import numpy as np
from numpy import inf
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import rasterio 
from rasterio.plot import show
import geopandas as gpd

def viz4x3Matrix(directory,year_list, trialNo, extTrial, base_dir, cph_area,regioner, waterPath,country,city):
    real_paths=[]
    pred_paths=[]
    dif_paths=[]
    for year in year_list: 
        pred_path = directory + '/{0}_{1}/{0}_{1}_{3}/outputs/predictions/pred_{2}.tif'.format(trialNo, country, year, extTrial)
        real_path = base_dir + '/data/{0}/{1}/{2}_proj/{3}.tif'.format(city,trialNo,country,year)
        #calc_dif(pred_path,real_path,directory,trialNo,country,year, extTrial)
        pred_paths.append(pred_path)
        real_paths.append(real_path)
        
        dif_path= directory + '/{0}_{1}/{0}_{1}_{3}/output/dif_{0}_{1}_{2}.tif'.format(trialNo,country,year, extTrial)
        dif_paths.append(dif_path)
    print(real_paths,pred_paths)
    
    cols = 4
    rows = 3

    fig, axs = plt.subplots(rows,cols, figsize=(20,10))
    fig.subplots_adjust(hspace = .02, wspace=.5)
    axs = axs.ravel()
    
    year=2010
    for j in range(len(pred_paths)):
        year +=2
        m=j+4
        h=j+8

        #Get and Plot Predictions
        src = rasterio.open(pred_paths[j])
        array_pred = src.read(1)
        cmap_Pred = ListedColormap(["#00233800","#002338","#004D57", "#009994", "#80F7FF", "#B8FFEA"]) # yellow:everthing lower than 10 #002338: 10-30 red: everthing higher than 30
        norm_Pred = colors.BoundaryNorm([ -100,1, 10, 20, 30,50,100], 6) 
    
        # Add a legend for labels
        legend_labels_Pred = { "#002338": "{0}-{1}".format(1,10), "#004D57": "{0}-{1}".format(10,20), "#009994": "{0}-{1}".format(20,30),
        "#80F7FF": "{0}-{1}".format(30,50), "#B8FFEA": ">50"} #"Red":"Min:{0}, Max:{1}".format(valMinP,valMaxP)
        
        # Connect labels and colors, create legend and save the image
        patches_Pred = [mpatches.Patch(color=color, label=label)
                    for color, label in legend_labels_Pred.items()]
        print(pred_paths[j])
        show(src, ax=axs[j], cmap=cmap_Pred, norm=norm_Pred, zorder=2)
        cph_area.plot(ax=axs[j], facecolor='None', edgecolor='#FFFFFF', linewidth=.2, alpha=0.3, zorder=1 )
        regioner.plot(ax=axs[j], facecolor='#161a1d', edgecolor='None',zorder=0, alpha=0.8 )
        axs[j].legend(handles=patches_Pred, bbox_to_anchor=(0.01, 0.08), loc='center left',facecolor="white",fontsize=3)
        axs[j].set_title('Prediction {0},{1},{2}'.format(trialNo,country,year), color="black", fontsize=6)
        axs[j].set_axis_off()

        #Plot Real Data
        # Define the colors you want
        src_real = rasterio.open(real_paths[j])
        array_real = src_real.read(1)
        cmap_Real = ListedColormap(["#00233800","#002338","#004D57","#009994","#80F7FF","#B8FFEA" ])
        norm_Real = colors.BoundaryNorm([0, 1, 10, 20, 50, 100, 10000], 6) 
        # Add a legend for labels
        legend_labels_Real = { "#002338": "{0}-{1}".format(1, 10),"#004D57": "{0}-{1}".format(10,20), "#009994": "{0}-{1}".format(20,50), 
        "#80F7FF": "{0}-{1}".format(50,100), "#B8FFEA": ">100"} #"#096e6b00": "{0}-{1}".format(valMin,valmid1),

        patches_Real = [mpatches.Patch(color=color, label=label)
                    for color, label in legend_labels_Real.items()]
        print(np.sum(array_real), np.max(array_real), np.min(array_real))
        show((src_real,1), ax=axs[m], cmap=cmap_Real, norm=norm_Real, zorder=2)
        cph_area.plot(ax=axs[m], facecolor='None', edgecolor='#FFFFFF', linewidth=.2, alpha=0.3, zorder=1 )
        regioner.plot(ax=axs[m], facecolor='#161a1d', edgecolor='None',zorder=0, alpha=0.8 )
        axs[m].legend(handles=patches_Real, bbox_to_anchor=(0.01, 0.08), loc='center left',facecolor="white",fontsize=3)
        axs[m].set_title('Real Data: {0},{1}'.format(country,year), color="black", fontsize=6)
        axs[m].set_axis_off()

        #Get and Plot difference
        src_dif= rasterio.open(dif_paths[j])
        array_dif= src_dif.read(1)
        print(np.sum(array_dif), np.max(array_dif), np.min(array_dif))
        cmap_Dif = ListedColormap(["#00383D","#006D77","#83C5BE","#EDF6F900","#FFDDD2","#E29578","#974220"])#
        norm_Dif = colors.BoundaryNorm([-50, -30, -10, -1, 1, 10, 30, 50], 7)
        legend_labels_Dif = { "#00383D": "{0}-{1}".format(-inf, -30,), "#006D77": "{0}-{1}".format(-30, -10), "#83C5BE": "{0}-{1}".format(-10, -1), 
                    "#EDF6F900": "{0}-{1}".format(-1,1), "#FFDDD2": "{0}-{1}".format(1, 10),
                "#E29578": "{0}-{1}".format(10, 30),"#974220": "{0}-{1}".format(30,inf)} 

        patches_Dif = [mpatches.Patch(color=color, label=label)
                    for color, label in legend_labels_Dif.items()]
        show(src_dif, ax=axs[h], cmap=cmap_Dif, norm=norm_Dif, zorder=2)   
        cph_area.plot(ax=axs[h], facecolor='None', edgecolor='#FFFFFF', linewidth=.2,alpha=0.3, zorder=1 )
        regioner.plot(ax=axs[h], facecolor='#161a1d', edgecolor='None', zorder=0, alpha=0.8 )
        axs[h].legend(handles=patches_Dif, bbox_to_anchor=(0.01, 0.08), loc='center left',facecolor="white",fontsize=3)
        axs[h].set_title('Difference: {0},{1}'.format(country,year), color="black", fontsize=6)
        axs[h].set_axis_off()

        xlim = ([cph_area.total_bounds[0],  cph_area.total_bounds[2]])
        ylim = ([cph_area.total_bounds[1],  cph_area.total_bounds[3]])
        axs[j].set_xlim(xlim)
        axs[j].set_ylim(ylim)
        axs[m].set_xlim(xlim)
        axs[m].set_ylim(ylim)
        axs[h].set_xlim(xlim)
        axs[h].set_ylim(ylim)
        
    plt.savefig(directory + '/{0}_{1}/{0}_{1}_{2}/output/comp_{0}_{1}_{2}.png'.format(trialNo, country, extTrial,city), dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(),transparent=True) #{0}_{1}/{0}_{1}_{2}/output
    #pyplot.show()

"""def vizOutput_Proj(directory, trialNo, base_dir, cph_area,regioner, waterPath,countries):
    for country in countries:
    #country=countries[i]
        path = directory + "/{0}_{1}".format(trialNo,country)
        extTrials=[]
        for k in os.listdir(path):
            extTrial= k.split("{0}_{1}_".format(trialNo,country))[1]
            print(extTrial)
            extTrials.append(extTrial)
        
        for extTrial in extTrials:
            print(country, extTrial)

            real_paths=[]
            pred_paths=[]
            dif_paths=[]
            for year in year_list: 
                pred_path = directory + '/{0}_{1}/{0}_{1}_{3}/outputs/predictions/pred_{2}.tif'.format(trialNo, country, year, extTrial)
                real_path = os.path.dirname(directory) + '/data/{0}/{1}_proj/{2}.tif'.format(trialNo,country,year)
                calc_dif(pred_path,real_path,directory,trialNo,country,year, extTrial)
                pred_paths.append(pred_path)
                real_paths.append(real_path)
                
                hist_year= year - 8
                dif_path= os.path.dirname(directory) + '/data/{0}/{1}/{2}.tif'.format(trialNo,country,hist_year)
                dif_paths.append(dif_path)
            print(real_paths,pred_paths, dif_paths)
            
            cols = 4
            rows = 3

            fig, axs = plt.subplots(rows,cols, figsize=(20,10))
            fig.subplots_adjust(hspace = .02, wspace=.5)
            axs = axs.ravel()
            
            year=2010
            for j in range(len(pred_paths)):
                year +=2
                m=j+4
                h=j+8

                #Get and Plot Predictions
                src = rasterio.open(pred_paths[j])
                array_pred = src.read(1)
                cmap_Pred = ListedColormap(["#00233800","#002338","#004D57", "#009994", "#80F7FF", "#B8FFEA"]) # yellow:everthing lower than 10 #002338: 10-30 red: everthing higher than 30
                norm_Pred = colors.BoundaryNorm([ -100,1, 10, 20, 30,50,100], 6) 
            
                # Add a legend for labels
                legend_labels_Pred = { "#002338": "{0}-{1}".format(1,10), "#004D57": "{0}-{1}".format(10,20), "#009994": "{0}-{1}".format(20,30),
                "#80F7FF": "{0}-{1}".format(30,50), "#B8FFEA": ">50"} #"Red":"Min:{0}, Max:{1}".format(valMinP,valMaxP)
                
                # Connect labels and colors, create legend and save the image
                patches_Pred = [mpatches.Patch(color=color, label=label)
                            for color, label in legend_labels_Pred.items()]
                print(pred_paths[j])
                show(src, ax=axs[j], cmap=cmap_Pred, norm=norm_Pred, zorder=2)
                cph_area.plot(ax=axs[j], facecolor='None', edgecolor='#FFFFFF', linewidth=.2, alpha=0.3, zorder=1 )
                regioner.plot(ax=axs[j], facecolor='#161a1d', edgecolor='None',zorder=0, alpha=0.8 )
                axs[j].legend(handles=patches_Pred, bbox_to_anchor=(0.01, 0.08), loc='center left',facecolor="white",fontsize=3)
                axs[j].set_title('Projection: {0},{1},{2}'.format(trialNo,country,year), color="black", fontsize=6)
                axs[j].set_axis_off()

                #Plot Real Data
                # Define the colors you want
                src_real = rasterio.open(real_paths[j])
                array_real = src_real.read(1)
                cmap_Real = ListedColormap(["#00233800","#002338","#004D57","#009994","#80F7FF","#B8FFEA" ])
                norm_Real = colors.BoundaryNorm([0, 1, 10, 20, 50, 100, 10000], 6) 
                # Add a legend for labels
                legend_labels_Real = { "#002338": "{0}-{1}".format(1, 10),"#004D57": "{0}-{1}".format(10,20), "#009994": "{0}-{1}".format(20,50), 
                "#80F7FF": "{0}-{1}".format(50,100), "#B8FFEA": ">100"} #"#096e6b00": "{0}-{1}".format(valMin,valmid1),

                patches_Real = [mpatches.Patch(color=color, label=label)
                            for color, label in legend_labels_Real.items()]
                print(np.sum(array_real), np.max(array_real), np.min(array_real))
                show((src_real,1), ax=axs[m], cmap=cmap_Real, norm=norm_Real, zorder=2)
                cph_area.plot(ax=axs[m], facecolor='None', edgecolor='#FFFFFF', linewidth=.2, alpha=0.3, zorder=1 )
                regioner.plot(ax=axs[m], facecolor='#161a1d', edgecolor='None',zorder=0, alpha=0.8 )
                axs[m].legend(handles=patches_Real, bbox_to_anchor=(0.01, 0.08), loc='center left',facecolor="white",fontsize=3)
                axs[m].set_title('Ground truth: {0},{1}'.format(country,year), color="black", fontsize=6)
                axs[m].set_axis_off()

                #Get and Plot difference
                src_dif= rasterio.open(dif_paths[j])
                show((src_dif,1), ax=axs[h], cmap= cmap_Real, norm=norm_Real, zorder=2)   
                cph_area.plot(ax=axs[h], facecolor='None', edgecolor='#FFFFFF', linewidth=.2,alpha=0.3, zorder=1 )
                regioner.plot(ax=axs[h], facecolor='#161a1d', edgecolor='None', zorder=0, alpha=0.8 )
                axs[h].legend(handles=patches_Real, bbox_to_anchor=(0.01, 0.08), loc='center left',facecolor="white",fontsize=3)
                axs[h].set_title('Historical Data: {0},{1}'.format(country,year-8), color="black", fontsize=6)
                axs[h].set_axis_off()

                xlim = ([cph_area.total_bounds[0],  cph_area.total_bounds[2]])
                ylim = ([cph_area.total_bounds[1],  cph_area.total_bounds[3]])
                axs[j].set_xlim(xlim)
                axs[j].set_ylim(ylim)
                axs[m].set_xlim(xlim)
                axs[m].set_ylim(ylim)
                axs[h].set_xlim(xlim)
                axs[h].set_ylim(ylim)
                
            plt.savefig(base_dir + '/summarizeResults/OutputImages/proj_{0}_{1}_{2}.png'.format(trialNo, country, extTrial), dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(),transparent=True) #{0}_{1}/{0}_{1}_{2}/output
            #pyplot.show()
"""

