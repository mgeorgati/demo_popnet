#import libraries 
import os
import json
import subprocess
import geopandas as gpd
from rasterstats import zonal_stats
import gdal

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.colors as colors
import matplotlib.patches as mpatches  
import imageio

import numpy as np
import seaborn as sns

def calc_shares(group, select, share, src_file, dest_file, year):
    df = gpd.read_file(src_file, crs="EPSG:3035")
    selectedColumns = df.loc[:, select]
    frame = selectedColumns.copy()
    if share == 'Z0':
        for i in group:
            frame['{0}_{1}'.format(share, i)] = (df['{}'.format(i)]/df['l1_sum_population'])*100
        frame.to_file(dest_file + "/{0}_{1}.geojson".format(year, share),driver='GeoJSON',crs="EPSG:3035")
    elif share == 'Z1' :
        for i in group:
            frame['{0}_{1}'.format(share, i)] = (df['{}'.format(i)]/df['totalMig'])*100
        frame.to_file(dest_file + "/{0}_{1}.geojson".format(year, share),driver='GeoJSON',crs="EPSG:3035")
    elif share == 'Z2':
        for i in group:
            frame['{0}_{1}'.format(share, i)] = (df['{}'.format(i)]/ (df['l1_sum_population'] - df['EuropeEU']))*100
        frame.to_file(dest_file + "/{0}_{1}.geojson".format(year, share),driver='GeoJSON',crs="EPSG:3035")
    elif share =='Z3' :
        for i in group:
            frame['{0}_{1}'.format(share, i)] = ((df['l1_sum_population'] - df['EuropeEU'])/ df['l1_sum_population'] )*100
            #frame['{0}_{1}'.format(share, i)] = ((df['l1_sum_population'] - df['EuropeEU'])/ df['totalMig'] )*100
        frame.to_file(dest_file + "/{0}_{1}.geojson".format(year, share),driver='GeoJSON',crs="EPSG:3035")


def shptoraster(ancillary_data_folder_path, cur_path, src_file, dst_path, share, gdal_rasterize_path, city, year):
    ## ## ## ## ## ----- Getting extent of corine raster ----- ## ## ## ## ##  
    data = gdal.Open(ancillary_data_folder_path + "/temp_tif/corine/{0}_CLC_2012_2018.tif".format(city))
    wkt = data.GetProjection()
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None
    xres=100
    yres=100

    ## ## ## ## ## ----- Rasterize files ----- ## ## ## ## ##
    df = gpd.read_file(src_file, crs="EPSG:3035")
    for column_name in df.columns:
        if column_name.startswith("{}_".format(share)):
            print("Rasterizing in GeogrGroups: {} layer".format(column_name))
            dst_file = dst_path + "/{0}_{1}.tif".format(year, column_name)
            cmd = '{0}/gdal_rasterize.exe -a {9} -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
            subprocess.call(cmd, shell=True)

# Calculate Zonal Statistic of TIF
def createSognMean(inputTif, dest_file, name, polys):
    zs = zonal_stats(polys, inputTif, stats="mean", geojson_out=True)
    for row in zs:
        newDict = row['properties']
        #print(newDict)
        for i in newDict.keys():
            #print(i)
            if i == 'mean':
                newDict['mean_{}'.format(name)] = newDict.pop(i)
    result = {"type": "FeatureCollection", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::3035" } }, "features": zs}
     
    with open(dest_file , 'w') as outfile:
        json.dump(result, outfile)

def plotSognMean(year, src_path, title, image_path, area, cph_area, regioner, share):
    gdf = gpd.read_file(src_path)
    gdf = gdf.to_crs(3035)
    # bins = UserDefined(gdf['mean_{}'.format(area)], bins=[2.5, 5,10,20,30,40,50,100]).bins
    maxNo = gdf['mean_{}'.format(area)].max() 
    if share == 'Z0':
        bins = 6
        a=[ 0, 0.5, 1, 2, 4, 6, maxNo]
    elif share == 'Z1':
        bins = 6
        a=[ 0, 1, 2, 4, 6, 8, maxNo]
    elif share == 'Z2':
        bins = 6
        a=[ 0, 0.2, 2, 4, 6, 8, maxNo]
    
    #bins = 6
    #a=[2, 5, 7.5, 10, 20, 30, 40, 100] #[1, 2.5, 5, 7.5, 10, 12.5,100]
    print(a)
    cmap = ListedColormap(["#fef0d900","#fef0d9","#fdcc8a", "#fc8d59", "#e34a33", "#b30000"])
    norm = colors.BoundaryNorm(a, bins) 
    # Add a legend for labels
    legend_labels_Pred = { "#fef0d9": "{0}-{1}".format(a[1],a[2]), "#fdcc8a": "{0}-{1}".format(a[2],a[3]), "#fc8d59": "{0}-{1}".format(a[3],a[4]),
    "#e34a33": "{0}-{1}".format(a[4],a[5]), "#b30000": "{0}-{1}".format(a[5], a[6])}
     # Connect labels and colors, create legend and save the image
    patches_Pred = [mpatches.Patch(color=color, label=label)
                    for color, label in legend_labels_Pred.items()]
    fig, ax = plt.subplots(1, figsize=(12, 8))
    #gdf.plot(column='mean_{}'.format(area), scheme='userdefined', ax=ax, classification_kwds={'bins':bins}, legend=True, cmap='PuRd') #PuRd'
    gdf.plot(column='mean_{}'.format(area), cmap=cmap, norm=norm, ax=ax) #PuRd'

    cph_area.plot(ax=ax, facecolor='None', edgecolor='black', linewidth=.2,  zorder=5)
        
    regioner.plot(ax=ax, facecolor='#A9A9AA', edgecolor='None',zorder=0, alpha=0.6 )
    ax.legend(handles=patches_Pred, bbox_to_anchor=(0.01, 0.08), loc='center left',facecolor="white",fontsize=7)

    ax.set_title(title, color="black", fontsize=10)
    xlim = ([cph_area.total_bounds[0],  cph_area.total_bounds[2]])
    ylim = ([cph_area.total_bounds[1],  cph_area.total_bounds[3]])
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_axis_off()
    plt.savefig(image_path , dpi=300, bbox_inches='tight',  facecolor=fig.get_facecolor(),transparent=True)
    #plt.show()
    plt.clf()        

def createGif(src_path, dest_path, area):
    fileNames=[]
    
    for file in os.listdir(src_path):
        if file.endswith('.png'):
            fileName = src_path + file
            fileNames.append(imageio.imread(fileName))
    #print(fileNames)
    imageio.mimsave(dest_path + '/sognMean_{}.gif'.format(area), fileNames, fps=24, duration=1)
    fileNames.clear()
    
def calc_cor(src_file, select, year, dest_path):
    # Load point data
    df = gpd.read_file(src_file, crs="EPSG:3035")
    selectedColumns = df.loc[:, select]
    frame = selectedColumns.copy()
                
    corr = frame.corr(method='pearson')
    corr.to_csv(dest_path + "/{}_corMatrix.csv".format(year))
    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=mask, cmap=cmap,  center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5}) #
    #plt.title("Correlation among Migrant Groups and Housing Elements, {}".format(year),fontsize=10)
    plt.title("Correlation among Selected Layers, {}".format(year),fontsize=10)
    plt.xlabel("Layers", fontsize=8)
    plt.ylabel("Layers", fontsize=8)
    plt.xticks(fontsize=7, rotation=45, ha='right')
    plt.yticks(fontsize=7, rotation=0)
    #plt.savefig(dest_path + "/{}_corMatrix.png".format(year), dpi=300)
    #plt.show() 