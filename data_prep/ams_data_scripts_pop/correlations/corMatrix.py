import os 
import pandas as pd
import geopandas as gpd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print(base_dir)
city='ams'
# Paths for the Population Data --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path = base_dir + "/data_prep/{}_Projectdata/AncillaryData".format(city)
ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_Projectdata/PopData".format(city)
cor_path= base_dir + "data_prep/{}_data_scripts_pop/correlations/corImages"

years = [1990,1992, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018] 


#Calculate correlations among regions of origin
def calc_cor(ancillary_POPdata_folder_path, year, selectList):
    # Load point data
    js = gpd.read_file(ancillary_POPdata_folder_path + '/{0}/temp_shp/{0}_dataVectorGrid.geojson'.format(year))     
    frame = pd.DataFrame(js, columns=selectList)
    
    cor = frame.corr(method='pearson')
    cor = cor.replace(np.nan, 0)
    
    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(cor, dtype=bool))
    
    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(cor, mask=mask, cmap=cmap, vmax=.3, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})  

    plt.title("Correlation matrix of Migrants by Country of origin, {}".format(year),fontsize=10)
    plt.xlabel("Layers", fontsize=8)
    plt.ylabel("Layers", fontsize=8)
    plt.xticks(fontsize=7, rotation=45, ha='right')
    plt.yticks(fontsize=7, rotation=0)
    #plt.savefig(cor_path + "/{}_cor_Matrix.png".format(year), dpi=300)
    plt.show()

#Calculate correlations among regions of origin
"""def calc_cor(ancillary_POPdata_folder_path, year):
    # Load point data
    js = gpd.read_file(ancillary_POPdata_folder_path + '/{0}/temp_shp/{0}_dataVectorGrid.geojson'.format(year))
    col= js.columns.to_list()
    #Select columns to correlate
    selectList = [ 'l2_children', 'l3_students', 'l4_mobile_adults', 'l5_not_mobile_adults', 'l6_elderly', 'l7_immigrants', 'l8_eu_immigrants', 'l9_noneu_immigrants', 
'l11_births', 'l12_deaths', 'l14a_people_who_moved_out_of_grid', 'l14b_immigrants_into_netherlands', 'l15a_ people_who_moved_into_grid', 'l15b_immigrants_outof_netherlands', 
'l16_verhuis_in_ams_outof', 'l17_verhuis_in_ams_into', 'l21_not_used_dwellings', 'l22_let_out_dwellings', 'l23_privately_owned_dwellings', 'l25_total_area_of_residence', 
'l26_number_of_dwellings', 'l27_number_of_rooms', 'nld', 'Oceania', 'Australia', 'Malanesia', 'Micronesia', 'Polynesia', 'Europe', 'EuropenoLocal', 'Eastern_Europe', 'Southern_Europe', 
'Western_Europe', 'Western_EuropenoLocal', 'Northern_Europe', 'EuropeEU', 'EuropeNotEU', 'EuropeEUnoLocal', 'Asia', 'Central_Asia', 'Eastern_Asia', 'Southern-Eastern_Asia', 'Southern_Asia', 
'Western_Asia', 'Antarctica', 'Americas', 'Northern_America', 'Latin_America_and_the_Caribbean', 'Africa', 'Northern_Africa', 'Sub-Saharan_Africa', 'OutsideEurope', 'Others', 'Colonies'] 
    frame = pd.DataFrame(js,columns=selectList)
    
    cor = frame.corr(method='pearson')
    cor = cor.replace(np.nan, 0)
    
    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(cor, dtype=bool))
    
    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(cor, mask=mask, cmap=cmap, vmax=.3, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})  

    plt.title("Correlation matrix of Migrants by Country of origin, {}".format(year),fontsize=10)
    plt.xlabel("Layers", fontsize=8)
    plt.ylabel("Layers", fontsize=8)
    plt.xticks(fontsize=7, rotation=45, ha='right')
    plt.yticks(fontsize=7, rotation=0)
    #plt.savefig(cor_path + "/{}_cor_Matrix.png".format(year), dpi=300)
    plt.show()"""

calc_cor(ancillary_POPdata_folder_path, 1992)