import os
from calcMean import createSognMean, combineFiles

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from variables import ancillary_POPdata_folder_path, ancillary_data_folder_path, city
from csv_to_raster import createFolder

districtsPath = ancillary_data_folder_path + "/adm/neighborhood_orig.geojson"
## ## ## ## ## ----- CHOOSE DATASET TO PROCESS  ----- ## ## ## ## ##
migration = "no"
propertyValue ="yes"
## ## ## ## ## ----- CHOOSE PROCESS TO RUN  ----- ## ## ## ## ##
calc_Mean = "yes" # Create geojsons for each migrant group aggregated with Zonal Statistics to neighborhood level
combineGJSON = "no" # Combine all geojsons in one for each year in new folder

if propertyValue == "yes":
    years_list= [ 2002,2004,2006, 2008,2010,2012, 2014,2016,2018 ] 
    for year in years_list:
        srcPath = os.path.dirname(ancillary_data_folder_path) + "/temp_tif/{}_home_prices/".format(city)
        dstPath = ancillary_POPdata_folder_path + "/Neighborhood&districtData/home_prices/"
        createFolder(dstPath)
        if calc_Mean == "yes":
            for file in os.listdir(srcPath):
                if file.startswith("{}_".format(year)) and file.endswith(".tif"):
                    name = file.split("{}_".format(year))[1].split(".tif")[0]
                    srcFile = srcPath + file
                    dstFile = "{0}_Neigh_{1}.geojson".format(year,name)
                    createSognMean(year, srcFile, dstPath, dstFile, districtsPath, name)

if migration =="yes":
    years_list= [ 1992, 1994, 1996, 1998,2000, 2002,2004,2006, 2008,2010,2012, 2014,2016,2018 ] 

    for year in years_list:
        srcPath = ancillary_POPdata_folder_path + "/{}/temp_tif_Z0/".format(year)
        dstPath = ancillary_POPdata_folder_path + "/Neighborhood&districtData/migrationProcess/{}/".format(year)
        createFolder(dstPath)
        comb = os.path.dirname(os.path.dirname(dstPath)) + "/MigInNeigh_regions/"
        createFolder(comb)
        if calc_Mean == "yes":
            for file in os.listdir(srcPath):
                if file.startswith("{}_Z0_".format(year)) and file.endswith(".tif"):
                    name = file.split("{}_Z0_".format(year))[1].split(".tif")[0]
                    srcFile = srcPath + file
                    dstFile = "{0}_NeighPerc_{1}.geojson".format(year,name)
                    createSognMean(year, srcFile, dstPath, dstFile, districtsPath, name)
        if combineGJSON == "yes":
            srcFile = dstPath + "/{0}_NeighPerc_nld.geojson".format(year)
            combineFiles(srcFile, dstPath, year, comb)

