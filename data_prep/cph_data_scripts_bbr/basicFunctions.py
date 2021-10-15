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

def importToDB_BBR(bbr_folder_path, city, conn, cur,  engine, year):
    # Loading shapefiles into postgresql and creating necessary 
    #_______________________Housing_________________________
    print("Importing files to postgres")
    path = bbr_folder_path + "/{0}_bbr/{1}_{0}_bbr.gpkg".format(city, year )
    src_file = gpd.read_file(path)
    
    print(src_file .head(2))
    # Create Table for Country Case Study
    print("---------- Creating table for {1} {0}, if it doesn't exist ----------".format(year, city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_{1}_bbr');".format(year,  city))
    check = cur.fetchone()
    if check[0] == True:
        print("{0} {1} table already exists".format(year,city))

    else:
        print("Creating {0} BBR FOR CPH table".format(year))
        src_file.to_postgis('bbr_{1}_{0}'.format(year, city),con =engine)

def psqltoshp(city, engine, temp_shp_path, BBRtype, year):
    # Create SQL Query
    sql = """SELECT id, "{0}_{1}", geom FROM {2}_cover_analysis""".format(year, BBRtype, city)
    # Read the data with Geopandas
    gdf = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col='geom' )
    print(gdf.head(4))
    src_path = temp_shp_path + "/{0}_{1}".format(city, BBRtype)
    createFolder(src_path)

    # exporting water cover from postgres
    print("Exporting {0} in {1} from postgres".format(BBRtype,year))
    gdf.to_file(src_path + "/{0}_{1}.gpkg".format(year, BBRtype),  driver="GPKG")   

def shptoraster(city, gdal_rasterize_path, xres, yres, temp_shp_path, temp_tif_path, year, BBRtype):
    # Getting extent of ghs pop raster
    data = gdal.Open(temp_tif_path + "/{0}_CLC_2012_2018.tif".format(city))
    
    wkt = data.GetProjection()
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None
    
    # Rasterizing layer
    print("Rasterizing {0} layer, {1}".format(BBRtype,year))
    src_path = temp_shp_path + "/{0}_{1}".format(city, BBRtype)
    dst_path = temp_tif_path + "/{0}_{1}".format(city, BBRtype)
    createFolder(dst_path)

    src_file = src_path + "/{0}_{1}.gpkg".format(year, BBRtype)
    dst_file = dst_path + "/{0}_{1}.tif".format(year, BBRtype)
    cmd = '{0}/gdal_rasterize.exe -a {9}_{10} -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
        .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, year, BBRtype)
    subprocess.call(cmd, shell=True)


    