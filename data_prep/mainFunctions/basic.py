import os
import numpy as np
#Python get unique values from list using numpy.unique

# function to get unique values
def unique(list1):
    x = np.array(list1)
    print(np.unique(x))

## ## ## ## ## ----- CREATE NEW FOLDER  ----- ## ## ## ## ##
def createFolder(path):
    if not os.path.exists(path):
        print("------------------------------ Creating Folder : {} ------------------------------".format(path))
        os.makedirs(path)
    else: 
        print("------------------------------ Folder already exists------------------------------")
import geopandas as gpd
import json
from rasterstats import zonal_stats
# Calculate zonal statistics from tiffs
def zonalStat(src_file, dst_file, polyPath):  
    # Read Files
    districts = gpd.read_file(polyPath)
    districts = districts.to_crs("EPSG:3035")
    
    zs = zonal_stats(districts, src_file,
                stats='mean', geojson_out=True)
    for row in zs:
        newDict = row['properties']
        for i in newDict.keys():
            if i == 'mean':
                newDict['mean_'] = newDict.pop(i)
        
    result = {"type": "FeatureCollection", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::3035" } }, "features": zs}
    #dst_file = dstPath + "{0}".format(dstFile) #
    with open(dst_file , 'w') as outfile:
        json.dump(result, outfile)
        
# Calculate zonal statistics from tiffs
def createSognMean(year, src_file, dstPath, dstFile, districtsPath, name):
    # Read Files
    districts = gpd.read_file(districtsPath)
    districts = districts.to_crs("EPSG:3035")
    
    zs = zonal_stats(districts, src_file,
                stats='mean', geojson_out=True)
    for row in zs:
        newDict = row['properties']
        for i in newDict.keys():
            if i == 'mean':
                newDict['mean_{}'.format(name)] = newDict.pop(i)
        
    result = {"type": "FeatureCollection", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::3035" } }, "features": zs}
    dst_file = dstPath + "{0}".format(dstFile) #
    with open(dst_file , 'w') as outfile:
        json.dump(result, outfile)
        
