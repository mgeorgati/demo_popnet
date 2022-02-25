import os
import geopandas as gpd
import json
import glob
from rasterstats import zonal_stats
from pathlib import Path
# Calculate zonal statistics from tiffs
def zonalStat(src_file, dst_file, polyPath, statistics):  
    # Read Files
    districts = gpd.read_file(polyPath)
    districts = districts.to_crs("EPSG:3035")
    
    zs = zonal_stats(districts, src_file,
                stats='{}'.format(statistics), all_touched = False, percent_cover_selection=None, percent_cover_weighting=False, #0.5-->dubled the population
                percent_cover_scale=None,geojson_out=True)
    
    for row in zs:
        newDict = row['properties']
        for i in newDict.keys():
            if i == '{}'.format(statistics):
                newDict['{}_'.format(statistics)] = newDict.pop(i)
        
    result = {"type": "FeatureCollection", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::3035" } }, "features": zs}
    #dst_file = dstPath + "{0}".format(dstFile) #
    with open(dst_file , 'w') as outfile:
        json.dump(result, outfile)

## ## ## ## ## ----- CREATE NEW FOLDER  ----- ## ## ## ## ##
def createFolder(path):
    if not os.path.exists(path):
        print("------------------------------ Creating Folder : {} ------------------------------".format(path))
        os.makedirs(path)
    else: 
        print("------------------------------ Folder already exists------------------------------")
        
listOfFiles = glob.glob("C:/FUME/PopNetV2/data_prep/Deliverable/PL/SpatialLayers/100x100m/*/*.tif")
#gridL = gpd.read_file( "C:/FUME/PopNetV2/data_prep/euroData/euroGrid/grid_1km_NL.gpkg")
for i in listOfFiles:
    file = Path(i)
    name= file.stem
    print(name)
    fold = Path('/'.join(list(file.parts)[-2:-1])+'/')
    print(fold)
    dst_path = "C:/FUME/PopNetV2/data_prep/Deliverable/PL/SpatialLayers/1000x1000m/{}".format(fold)
    createFolder(dst_path)
    dst_file = dst_path + '/{}_1km.geojson'.format(name)
    polyPath = "C:/FUME/PopNetV2/data_prep/euroData/euroGrid/grid_1km_PL.gpkg"
    statistics = 'mean'
    zonalStat(file, dst_file, polyPath, statistics)
    grid = gpd.read_file(dst_file)
    grid = grid[['GRD_ID', 'geometry', 'mean_']]
    grid = grid.rename(columns={'mean_':'{}'.format(name)})
    grid.to_csv(dst_path + "/{}_1km.csv".format(name), sep=';')
    grid.to_file(dst_path + "/{}_1km.gpkg".format(name),driver='GPKG',crs="EPSG:3035")
    os.remove(dst_file)