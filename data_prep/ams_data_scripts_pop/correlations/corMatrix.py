import os 
import pandas as pd
import geopandas as gpd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from variables import base_dir, ancillary_POPdata_folder_path, ancillary_data_folder_path, city, country_Orig
from mainFunctions import createFolder, dfTOxls

years = [1992, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018] 
## Correlations
#This script creates correlation matrixes from the geojson files for the countries in categories/regions of dictionary
## ## ## ## ## ----- Calculate correlations ----- ## ## ## ## ## 
def calc_cor(js, cor_path, year, selectList, selection, title, dest_path, fileName):
    # Load data
    frame = pd.DataFrame(js, columns=selectList)
    cor = frame.corr(method='pearson')
    cor = cor.replace(np.nan, 0)

    dfTOxls(dest_path, fileName, cor)
    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(cor, dtype=bool))
    
    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(cor, mask=mask, cmap=cmap, vmax=.3, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})  

    plt.title("{1}, {0}".format(year, title),fontsize=10)
    plt.xlabel("Layers", fontsize=8)
    plt.ylabel("Layers", fontsize=8)
    plt.xticks(fontsize=5, rotation=90)
    plt.yticks(fontsize=5, rotation=0)
    plt.savefig(cor_path + "/{0}_corMatrix_{1}.png".format(year,selection), dpi=300)
    plt.cla()
    plt.close()

year= 2018
#Case 1st: Get the following layers and check correlations
js = gpd.read_file(ancillary_POPdata_folder_path + '/{0}/temp_shp/{0}_dataVectorGrid.geojson'.format(year)) 
selectListA = [ 'l2_children', 'l3_students', 'l4_mobile_adults', 'l5_not_mobile_adults', 'l6_elderly', 'l7_immigrants', 'l8_eu_immigrants', 'l9_noneu_immigrants', 
'l11_births', 'l12_deaths', 'l14a_people_who_moved_out_of_grid', 'l14b_immigrants_into_netherlands', 'l15a_ people_who_moved_into_grid', 'l15b_immigrants_outof_netherlands', 
'l16_verhuis_in_ams_outof', 'l17_verhuis_in_ams_into', 'l21_not_used_dwellings', 'l22_let_out_dwellings', 'l23_privately_owned_dwellings', 'l25_total_area_of_residence', 
'l26_number_of_dwellings', 'l27_number_of_rooms', 'nld', 'Oceania', 'Australia', 'Malanesia', 'Micronesia', 'Polynesia', 'Europe', 'EuropenoLocal', 'Eastern_Europe', 'Southern_Europe', 
'Western_Europe', 'Western_EuropenoLocal', 'Northern_Europe', 'EuropeEU', 'EuropeNotEU', 'EuropeEUnoLocal', 'Asia', 'Central_Asia', 'Eastern_Asia', 'Southern-Eastern_Asia', 'Southern_Asia', 
'Western_Asia', 'Antarctica', 'Americas', 'Northern_America', 'Latin_America_and_the_Caribbean', 'Africa', 'Northern_Africa', 'Sub-Saharan_Africa', 'OutsideEurope', 'Others', 'Colonies'] 
titleA = "Correlation matrix of Migrants by Region of origin and other"
cor_path = base_dir + "/data_prep/{0}_data_scripts_pop/correlations/corImages/{1}_corImages/".format(city,year)
createFolder(cor_path)
dest_path = base_dir + "/data_prep/{0}_data_scripts_pop/correlations/corEXCEL/{1}_corEXCEL/".format(city,year)
fileNameA = "{0}_corEXCEL_{1}".format(year,'A')
createFolder(dest_path)
calc_cor(js, cor_path, year, selectListA, 'A', titleA, dest_path, fileNameA)

#Case 2nd: Get countries by regions of origin and check correlations
for key in country_Orig:
    df = gpd.read_file(ancillary_POPdata_folder_path + '/{0}/temp_shp/{0}_dataVectorGrid.geojson'.format(year)) 
    selectListB =country_Orig['{}'.format(key)]   
    select = [x for x in df.columns if x in selectListB]
    titleB = "Correlation matrix of Migrants by Country of origin"
    cor_path= base_dir + "/data_prep/{0}_data_scripts_pop/correlations/corImages/{1}_corImages/".format(city,year)
    createFolder(cor_path)
    dest_path = base_dir + "/data_prep/{0}_data_scripts_pop/correlations/corEXCEL/{1}_corEXCEL/".format(city,year)
    fileNameB = "{0}_corEXCEL_{1}".format(year,key)
    createFolder(dest_path)
    calc_cor(df,cor_path, year, selectListB, key, titleB, dest_path, fileNameB)