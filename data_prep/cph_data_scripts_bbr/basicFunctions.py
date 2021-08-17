import os
import subprocess
import psycopg2
import gdal
import geopandas as gpd
from shapely.geometry import Polygon


## ## ## ## ## ----- CREATE PostGIS EXTENSION  ----- ## ## ## ## ##
def initPostgis(pghost, pgport, pguser, pgpassword, pgdatabase, cur, conn,city):
    conn = psycopg2.connect(database=pgdatabase, user=pguser, host=pghost, password=pgpassword,sslmode="disable",gssencmode="disable")
    cur = conn.cursor()
    # check for and add postgis extension if not existing
    cur.execute("SELECT * FROM pg_available_extensions \
                    WHERE name LIKE 'postgis';")
    check_postgis = cur.rowcount
    if check_postgis == 0:
        print("Adding extension postgis")
        cur.execute("CREATE EXTENSION postgis SCHEMA public;")
        conn.commit()

## ## ## ## ## ----- CREATE PgRouting EXTENSION  ----- ## ## ## ## ##
def initPgRouting(pghost, pgport, pguser, pgpassword, pgdatabase, cur, conn):  
    # check for and add pgrouting extension if not existing
    cur.execute("SELECT * FROM pg_available_extensions \
                    WHERE name LIKE 'pgRouting';")
    check_postgis = cur.rowcount
    if check_postgis == 0:
        print("Adding extension pgRouting")
        cur.execute("CREATE EXTENSION pgRouting;")
        conn.commit()

## ## ## ## ## ----- CREATE NEW FOLDER  ----- ## ## ## ## ##
def createFolder(path):
    if not os.path.exists(path):
        print("------------------------------ Creating Folder : {} ------------------------------".format(path))
        os.makedirs(path)
    else: 
        print("------------------------------ Folder already exists------------------------------")

## ## ## ## ## ----- CLIP BBR DATA TO bbox EXTENT  ----- ## ## ## ## ##
def clipToExtent(gdal_path, xmin, ymin, xmax, ymax, bbr_folder_path, year, city): 
    city_bbr_folder_path = bbr_folder_path + '/{}_bbr'.format(city)
    createFolder(city_bbr_folder_path)
    cmd_tif_merge = '{0}/ogr2ogr.exe -spat {1} {2} {3} {4} -s_srs \
                    EPSG:25832 -t_srs EPSG:3035 -f GPKG {6}/{7}_cph_bbr.gpkg \
                    {5}/rawData/bbr_{7}.gpkg'.format(gdal_path, xmin, ymin, xmax, ymax, bbr_folder_path, city_bbr_folder_path, year)
    print(cmd_tif_merge)
    subprocess.call(cmd_tif_merge, shell=False)

## ## ## ## ## ----- CLIP BBR DATA TO bbox EXTENT  ----- ## ## ## ## ##
def clipSelectCulture(gdal_path, city, ancillary_data_folder_path, bbr_folder_path,  year): 
    csPath =  os.path.dirname(ancillary_data_folder_path) + "/temp_shp/{0}_bbox.shp".format(city)
    cs = gpd.read_file(csPath).to_crs("epsg:25832")
    xmin, ymin, xmax, ymax = cs.geometry.total_bounds
    print(xmin, ymin, xmax, ymax)
    out_path = bbr_folder_path + "/{}_bbr/culture".format(city)
    createFolder( out_path)
    cmd_tif_merge = '{0}/ogr2ogr.exe -spat {1} {2} {3} {4} -where "\"BYG_ANVEND\" = 410" -s_srs EPSG:25832 -t_srs \
                    EPSG:3035 -f GPKG {7}/{6}_bbr_culture.gpkg \
                    {5}/rawData/bbr_{6}.gpkg'.format(gdal_path, xmin, ymin, xmax, ymax, ancillary_data_folder_path, year, out_path)
    print(cmd_tif_merge)
    subprocess.call(cmd_tif_merge, shell=False)

def psqltoshp(city, engine, temp_shp_path, BBRrasterizeType,year):
    # Create SQL Query
    sql = """SELECT id, "{0}_{1}count", geom FROM {2}_cover_analysis""".format(year, BBRrasterizeType, city)
    # Read the data with Geopandas
    gdf = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col='geom' )
    print(gdf.head(4))
    src_path = temp_shp_path + "/{0}_{1}".format(city, BBRrasterizeType)
    createFolder(src_path)

    # exporting water cover from postgres
    print("Exporting {0} in {1} from postgres".format(BBRrasterizeType,year))
    gdf.to_file(src_path + "/{0}_{1}.gpkg".format(year, BBRrasterizeType),  driver="GPKG")  
    
    

def shptoraster(city, gdal_rasterize_path, xres, yres, temp_shp_path, temp_tif_path, year, BBRrasterizeType):
    # Getting extent of ghs pop raster
    data = gdal.Open(temp_tif_path + "/{0}_CLC_2012_2018.tif".format(city))
    
    wkt = data.GetProjection()
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None
    
    # Rasterizing schools layer
    print("Rasterizing schools layer")
    src_path = temp_shp_path + "/{0}_{1}".format(city, BBRrasterizeType)
    dst_path = temp_tif_path + "/{0}_{1}".format(city, BBRrasterizeType)
    createFolder(dst_path)

    src_file = src_path + "/{0}_{1}.gpkg".format(year, BBRrasterizeType)
    dst_file = dst_path + "/{0}_{1}.tif".format(year, BBRrasterizeType)
    cmd = '{0}/gdal_rasterize.exe -a {9}_{10}count -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
        .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, year, BBRrasterizeType)
    subprocess.call(cmd, shell=True)


    