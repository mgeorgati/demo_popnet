import os
import sys 
import numpy as np
import pandas as pd
import geopandas as gpd
import openpyxl
import matplotlib.pyplot as plt

current_path = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from variables import base_dir, ancillary_POPdata_folder_path, ancillary_data_folder_path, city, country_Orig
from mainFunctions import createFolder, dfTOxls, generate_colors, unique, lineDiagram

years_list=[1992,1994,1996,1998,2000,2002,2004,2006,2008,2010,2012,2014,2016,2018] 

## ## ## ## ## ----- CREATE FRAME FOR ALL YEARS BY COUNTRY IN REGION, EXPORT TO EXCEL ----- ## ## ## ## ## 
def createFrame(region, years_list, outputName):
    frame = pd.DataFrame(columns=region)
    year = ['1992','1994','1996','1998','2000','2002','2004','2006','2008','2010','2012','2014','2016','2018'] 
    frame['Year'] = year
    nframe= frame.set_index('Year')
    print("##### - - - - - Creating Dataframe  - - - - - #####")
    for year in years_list:
        pathI = ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.geojson".format(year)
        dfI = gpd.read_file(pathI, header=0)
        for y in region: 
            if y in dfI.columns:
                nframe.at['{}'.format(year), y ] = dfI['{}'.format(y)].sum()
    print(nframe.head(3))    
    destEXCEL_path = current_path + '/EXCEL/'
    createFolder(destEXCEL_path)
    dfTOxls(destEXCEL_path, outputName, nframe)  
"""
## ## ## ## ## ----- CREATE LINE DIAGRAM FROM DATAFRAME ----- ## ## ## ## ##
def lineDiagram(frame, outputName, n, title, dest_path):
    ax = plt.gca()
    # Shink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # generate values and print them 
    hex_values = generate_colors(len(frame.columns)) 
    lines = [] 
    print(frame.head(3))
    for i, country in enumerate(frame):
        #lines = nframe[i].plot(kind='line', x='Year', y='Population',ax=ax, ylabel='Population', title ='Population Change of Migrant Groups (1992-2018)', color='green')  
        axes = frame[country].plot.line(color={ "{}".format(country): "{}".format(hex_values[i])}, title= "{}".format(title))
    plt.xlabel("Year")
    plt.ylabel("Population")    
    plt.legend(bbox_to_anchor=(1.3,0.5), loc='center', borderaxespad=0., fontsize=5)
    plt.savefig(dest_path + '/{}.png'.format(outputName), dpi=300)
    plt.cla()
    plt.close()"""

## ## ## ## ## ----- CREATE LINE DIAGRAM FROM SPECIFIC EXCEL FILE ----- ## ## ## ## ##
def createLineDiagramFromExcel(path, region, regionName, outputName, title):
    frame = pd.read_excel(path + '/EXCEL/{}.xlsx'.format(outputName), index_col=0)
    n = len(region)
    destIMAGE_path = current_path + '/IMAGES/'
    createFolder(destIMAGE_path)
    lineDiagram(frame, outputName, n, title, destIMAGE_path)    

# Sum population change by country by region in EXCEL and then visualize in line diagram PNG
def main(dictionary):
    for key in dictionary:
        outputName = "PopChangeCountry_{}".format(key)
        title = "Population Change by Country in Amsterdam ({})".format(key)
        countriesList = list(dictionary[key])
        print(key, countriesList)
        # Create frames of sums from each region and save it to EXCEL
        createFrame(countriesList, years_list, outputName)
        # Read Excel and make line diagram for each region, save it to PNG 
        createLineDiagramFromExcel(current_path, countriesList, key, outputName, title)

main(country_Orig)
