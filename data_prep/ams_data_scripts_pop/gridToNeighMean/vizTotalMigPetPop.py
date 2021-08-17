import os
import mapclassify
import geopandas as gpd
import matplotlib.pyplot as plt
from mapclassify import  UserDefined
from matplotlib.colors import Normalize
import contextily as cx

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print(base_dir)
city="cph"

#Set filepath
#cph = "K:/FUME/Ghetto_coordinates/tingbjerg.geojson"
cph = base_dir + "/data_prep/cph_ProjectData/AncillaryData/CaseStudy/sogns.geojson"
regions = base_dir + "/data_prep/cph_ProjectData/AncillaryData/CaseStudy/regioner.gpkg"

cph_area = gpd.read_file(cph)
regioner = gpd.read_file(regions)
ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_ProjectData/PopData".format(city)

def plotSognMean(year):
    shp_link =  base_dir + "/data_prep/cph_data_scripts_pop/sognStatistics/sognMean/pred_{}.geojson".format(year)
    gdf = gpd.read_file(shp_link)
    gdf = gdf.to_crs(3035)
    valMin = gdf['mean'].min()
    if valMin>0:
        bins= UserDefined(gdf['mean'], bins=[ 0.01,1,5]).bins
    else:
        bins= UserDefined(gdf['mean'], bins=[-1, -0.01, 0, 0.01,1,5]).bins
    """valMax = gdf['mean'].max()
    print(valMax)
    if valMax >= 60:
        x = round(valMax, 2)
        bins= UserDefined(gdf['mean'], bins=[5,10,20,40,60]).bins
        print(bins)
    elif valMax<60 and valMax>=40:
        x = round(valMax, 2)
        bins= UserDefined(gdf['mean'], bins=[5,10,20,40]).bins
        print(bins)
    else:
        x = round(valMax, 2)
        bins= UserDefined(gdf['mean'], bins=[5,10,20]).bins
        print(bins)"""
    fig, ax = plt.subplots(1, figsize=(12, 8))
    gdf.plot(column='mean', scheme='userdefined', ax=ax, classification_kwds={'bins':bins}, legend=True, cmap='bwr') #PuRd'
    cph_area.plot(ax=ax, facecolor='None', edgecolor='black', linewidth=.2,  zorder=5)
        
    regioner.plot(ax=ax, facecolor='#A9A9AA', edgecolor='None',zorder=0, alpha=0.6 )

    ax.set_title('Average Error, {}'.format(year), color="black", fontsize=10)
    xlim = ([cph_area.total_bounds[0],  cph_area.total_bounds[2]])
    ylim = ([cph_area.total_bounds[1],  cph_area.total_bounds[3]])
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_axis_off()
    plt.savefig(base_dir + '/data_prep/cph_data_scripts_pop/sognStatistics/sognMeanPNG/pred_{}.png'.format(year), dpi=300, bbox_inches='tight',  facecolor=fig.get_facecolor(),transparent=True)
    #plt.show()
years_list= [ 2012,2014,2016,2018 ]
#years_list= [ 1990, 1992, 1994, 1996, 1998,2000, 2002,2004,2006, 2008,2010,2012, 2014,2016,2018 ] 
for year in years_list:
    plotSognMean(year)