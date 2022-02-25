import os
import geopandas as gpd
import json
from rasterstats import zonal_stats

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

# Combine all files from folder to new geojson file
def combineFiles(srcFile, dstPath,year,comb):
    df = gpd.read_file(srcFile)
    ndf = df.copy()
    
    ndf.drop('mean_nld', axis=1, inplace=True)
    
    for file in os.listdir(dstPath):
        
        srcFile = dstPath + file
        data = gpd.read_file(srcFile)
        
        for column in data.columns:
            if column.startswith('mean'):
                x = data[['id', '{}'.format(column)]]
                
                ndf = ndf.merge(x, how="inner", on= 'id')
    
    ndf.to_file(comb + "/{}_NeighPerc_comb.geojson".format(year),driver='GeoJSON',crs="EPSG:3035")




