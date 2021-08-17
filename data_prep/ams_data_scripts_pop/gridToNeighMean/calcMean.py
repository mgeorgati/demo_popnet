import os

import gdal
import pandas as pd
import geopandas as gpd
#from geopandas.tools import sjoin
#from shapely.wkt import loads
import json
from rasterstats import zonal_stats
from functools import reduce

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print(base_dir)
city="ams"
year= "2018"
ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_ProjectData/PopData".format(city)

"""def createPoints(year, path):
    gridPath = ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridDivs.geojson".format(year)
    grid = gpd.read_file(gridPath)
    df = grid.copy()
    # change the geometry
    df.geometry = df['geometry'].centroid
    # same crs
    df.crs = grid.crs
    df.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorPoints.geojson".format(year), driver='GeoJSON', crs='epsg:3035')"""

"""# Read Files
districts = gpd.read_file("C:/FUME/PopNetV2/data_prep/ams_ProjectData/AncillaryData/adm/neighborhood_orig.geojson")
districts =districts.to_crs("EPSG:3035")
zs= zonal_stats(districts, "C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/2018/temp_tifPercentages/2018_Z0_totalMig.tif",
            stats="mean", geojson_out=True)
result = {"type": "FeatureCollection", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::3035" } }, "features": zs}
dest_file =  "C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/Neighborhood&districtData/migrationProcess/1_SognMean_mig.geojson"
with open(dest_file , 'w') as outfile:
    json.dump(result, outfile)

"""
def createSognMean(year, src_file, destPath, districtsPath, name):
    # Read Files
    districts = gpd.read_file(districtsPath)
    districts =districts.to_crs("EPSG:3035")
    #gdf_points = gpd.read_file(src_file)
    zs = zonal_stats(districts, src_file,
                stats="mean".format(name), geojson_out=True)
    
    for row in zs:
        newDict = row['properties']
        print(newDict)
        for i in newDict.keys():
            print(i)
            if i == 'mean':
                newDict['mean_{}'.format(name)] = newDict.pop(i)
        
    result = {"type": "FeatureCollection", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::3035" } }, "features": zs}
    dest_file = destPath + "{0}_SognMean_{1}.geojson".format(year,name)
    with open(dest_file , 'w') as outfile:
        
        json.dump(result, outfile)

years_list= [ 2012,2014,2016,2018 ]
#years_list= [ 1990, 1992, 1994, 1996, 1998,2000, 2002,2004,2006, 2008,2010,2012, 2014,2016,2018 ] 
srcPath = "C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/2018/temp_tifPercentages/"
destPath = "C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/Neighborhood&districtData/migrationProcess/"
districtsPath = "C:/FUME/PopNetV2/data_prep/ams_ProjectData/AncillaryData/adm/neighborhood_orig.geojson"

def generateSognMean(srcPath,year):
    for file in os.listdir(srcPath):
        if file.startswith("{}_Z0_".format(year)) and file.endswith(".tif"):
            name = file.split("{}_Z0_".format(year))[1].split(".tif")[0]
            print(name)
            srcFile = srcPath + file
            createSognMean(year, srcFile, destPath, districtsPath, name)

def combineFiles(destPath):
    """#demoPath = "C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/Neighborhood&districtData/demographicProcess/neighDemo_2019.geojson"
    incomePath = "C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/Neighborhood&districtData/incomeProcess/neighIncome_2018.geojson"
    eduPath = "C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/Neighborhood&districtData/educationProcess/neighEduc_2019.geojson"
    dataI = gpd.read_file(incomePath)
    #dataI = dataI.set_index("Buurtcombinatie", inplace=True)
    dataI= dataI.iloc[:,4:-1]
    print(dataI)
    """
    appended_data = []
    for file in os.listdir(destPath):
        srcFile = destPath + file
        data = gpd.read_file(srcFile)
        options = ['mean', 'Buurt']
        a = data.columns[data.columns.str.startswith(tuple(options)) ]
        
        data = data[a]
        print(data.columns)
        #data=data.set_index("Buurtcombinatie", inplace=True)
        #print(data)
        # store DataFrame in list
        appended_data.append(data)
    #print(appended_data)
    dfs = pd.concat(appended_data, join='inner')
    #dfs = reduce(lambda left,right: pd.merge(left,right,on='Buurtcombinatie_code'), appended_data)
    print(dfs.set_index("Buurtcombinatie_code"))
    """# see pd.concat documentation for more info
    appended_data = pd.concat(appended_data)
    # write DataFrame to an excel sheet 
    #appended_data.to_file("C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/Neighborhood&districtData/migrationProcess/{}_mig.geojson".format(year), driver='GeoJSON', crs='epsg:3035')
    demoPath = "C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/Neighborhood&districtData/demographicProcess/neighDemo_2019.geojson"
    incomePath = "C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/Neighborhood&districtData/incomeProcess/neighIncome_2018.geojson"
    eduPath = "C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/Neighborhood&districtData/educationProcess/neighEduc_2019.geojson"
    
    #dataI = gpd.read_file(incomePath)
    extralist = [demoPath,incomePath, eduPath]
    
    for file in extralist:
        data = gpd.read_file(file)
        #data.set_index("Buurtcombinatie", inplace=True)
        data = data.iloc[:,:-1]
        # data.set_index("Buurtcombinatie_code", inplace=True)
        # store DataFrame in list
        appended_data.append(data)

    #dfs = reduce(lambda left,right: pd.merge(left,right,on='Buurtcombinatie_code'), appended_data)
    print(appended_data)
    # write DataFrame to an excel sheet 
    #dfs.to_file("C:/FUME/PopNetV2/data_prep/ams_ProjectData/PopData/Neighborhood&districtData/{}_total.geojson".format(year), driver='GeoJSON', crs='epsg:3035')
    """
def deleteIrr(path):
    for file in os.listdir(path):
        if not file.endswith("_mig.geojson"):
            os.remove(file)

#generateSognMean(srcPath,year)
combineFiles(destPath)
#deleteIrr(destPath)

#for year in years_list:
    #createSognMean(year)

