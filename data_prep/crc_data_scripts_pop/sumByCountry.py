import os
import pandas as pd
import geopandas as gpd
import gdal

def sumCountries(ancillary_POPdata_folder_path,year):
   
    # spatial join between the vector grid and the points
    points = gpd.read_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataPoints.shp".format(year), crs="EPSG:3035")
    
    # Create EU population column
    EU_EE = ["BGR","CZE","HUN","POL","ROU","SVK"]
    select_EU_EE = [x for x in points.columns if x in EU_EE]
    points['EU_EE'] = points.loc[:, select_EU_EE].sum(axis=1)

    EU_EEnotPol = ["BGR","CZE","HUN","ROU","SVK"]
    select_EU_EEnotPol = [x for x in points.columns if x in EU_EEnotPol]
    points['EU_EEnotPol'] = points.loc[:, select_EU_EEnotPol].sum(axis=1)

    EU_NE = ["DNK","FIN","IRL","LVA","LTU","SWE","GBR","ISL","NOR","GBR"]
    select_EU_NE = [x for x in points.columns if x in EU_NE]
    points['EU_NE'] = points.loc[:, select_EU_NE].sum(axis=1)

    EU_SE = ["HRV","GRC","ITA","MLT","PRT","SVN","ESP","CYP"]
    select_EU_SE = [x for x in points.columns if x in EU_SE]
    points['EU_SE'] = points.loc[:, select_EU_SE].sum(axis=1)

    EU_WE = ["AUT","BEL","FRA","DEU","LUX","MCO","NLD","LIE","CHE"]
    select_EU_WE = [x for x in points.columns if x in EU_WE]
    points['EU_WE'] = points.loc[:, select_EU_WE].sum(axis=1)

    # Create not EU population column
    notEU_EE = ["BLR","MDA","RUS","UKR"]
    select_notEU_EE = [x for x in points.columns if x in notEU_EE]
    points['notEU_EE'] = points.loc[:, select_notEU_EE].sum(axis=1)

    notEU_NE = ["ALA","GGY","JEY","FRO","IMN","SJM"]
    select_notEU_NE = [x for x in points.columns if x in notEU_NE]
    points['notEU_NE'] = points.loc[:, select_notEU_NE].sum(axis=1)

    notEU_SE = ["ALB","AND","BIH","GIB","VAT","MNE","MKD","SMR","SRB"]
    select_notEU_SE = [x for x in points.columns if x in notEU_SE]
    points['notEU_SE'] = points.loc[:, select_notEU_SE].sum(axis=1)
    
    #save shapefiles to folder
    print("------------------------------ Creating shapefile:{0} on Points------------------------------".format(year)) 
    points.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataPointsSums.shp".format(year))