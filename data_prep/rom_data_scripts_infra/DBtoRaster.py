import os
import subprocess
from osgeo import gdal
import geopandas as gpd

## ## ## ## ## ----- CREATE NEW FOLDER  ----- ## ## ## ## ##
def createFolder(path):
    if not os.path.exists(path):
        print("------------------------------ Creating Folder : {} ------------------------------".format(path))
        os.makedirs(path)
    else: 
        print("------------------------------ Folder already exists------------------------------")
        
def bdTOraster(city, gdal_rasterize_path,engine, xres, yres, temp_shp_path, temp_tif_path, layer, layerFolder, layerName):
    # Create SQL Query
    sql = """SELECT id, "{0}", geometry FROM {1}_cover_analysis""".format(layer, city)
    # Read the data with Geopandas
    gdf = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col='geometry' )
    print(gdf.head(4))
    src_path = temp_shp_path + "/{0}".format(layerFolder)
    createFolder(src_path)

    # exporting water cover from postgres
    print("Exporting {0} from postgres".format(layer))
    gdf.to_file(src_path + "/{0}.gpkg".format(layerName),  driver="GPKG")   
    
    # Getting extent of ghs pop raster
    data = gdal.Open(temp_tif_path + "/{0}_CLC_2012_2018.tif".format(city))
    wkt = data.GetProjection()
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None
    
    print("Rasterizing {} layer".format(layer))
    src_file = src_path +"/{0}.gpkg".format(layerName)
    dst_path = temp_tif_path + "/{0}".format(layerFolder)
    createFolder(dst_path)
    
    dst_file = dst_path +"/{0}.tif".format(layerName)
    print(dst_file)
    cmd = '{0}/gdal_rasterize.exe -a "{9}" -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
            .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, layer)
    subprocess.call(cmd, shell=True)

