import os
import subprocess
import gdal
import geopandas as gpd

## ## ## ## ## ----- CREATE NEW FOLDER  ----- ## ## ## ## ##
def createFolder(path):
    if not os.path.exists(path):
        print("------------------------------ Creating Folder : {} ------------------------------".format(path))
        os.makedirs(path)
    else: 
        print("------------------------------ Folder already exists------------------------------")

def psqltoshp(city, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, cur, conn, temp_shp_path):
    os.environ['PATH'] = pgpath
    os.environ['PGHOST'] = pghost
    os.environ['PGPORT'] = pgport
    os.environ['PGUSER'] = pguser
    os.environ['PGPASSWORD'] = pgpassword
    os.environ['PGDATABASE'] = pgdatabase

    # exporting water cover from postgres
    print("Exporting water cover from postgres")
    path = temp_shp_path + "/{0}_water_cover.shp".format(city)
    cmd = 'pgsql2shp -f {0} -h localhost -u postgres -P postgres {1} "SELECT id, water_cover, geom FROM {2}_cover_analysis"'.format(path, pgdatabase, city)
    subprocess.call(cmd, shell=True)

    # exporting train station- counts by isochrones
    years=[1990,1992,1994,1996,1998,2000,2002,2004,2006,2008,2010,2012,2014,2016,2018,2020]
    for year in years: 
    
        print("Exporting train station counts from postgres {0}".format(year))
        path = temp_shp_path + "/{1}_{0}_stationcount.shp".format(city,year)
        cmd = 'pgsql2shp -f {0} -h localhost -u postgres -P postgres {1} "SELECT id, stationcount_{3}, geom FROM {2}_cover_analysis"'.format(path, pgdatabase, city, year)
        print(cmd)
        subprocess.call(cmd, shell=True)
    
    # exporting bus stops- counts by isochrones
    busyears=[]
    cur.execute("SELECT distinct(year) FROM {0}_busst where year% 2 = 0 order by year ASC;".format(city))
    year_id = cur.fetchall()
    for id in year_id:
        busyears.append(id[0])
    print(busyears)
        
    for year in busyears:
        print("Exporting bus stops counts from postgres {0}".format(year))
        path = temp_shp_path + "/{0}_busstopscount{1}.shp".format(city,year)
        cmd = 'pgsql2shp -f {0} -h localhost -u postgres -P postgres {1} "SELECT id, busst_{3}, geom FROM {2}_cover_analysis"'.format(path, pgdatabase, city, year)
        subprocess.call(cmd, shell=True)

def shptoraster(city, gdal_rasterize_path,cur, conn, xres, yres, temp_shp_path, temp_tif_path):
    # Getting extent of ghs pop raster
    data = gdal.Open(temp_tif_path + "/{0}_CLC_2012_2018.tif".format(city))
    wkt = data.GetProjection()
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None
    
    # Rasterizing water_cover layer
    print("Rasterizing water_cover layer")
    src_file = temp_shp_path +"/{0}_water_cover.shp".format(city)
    dst_file = temp_tif_path +"/{0}_water_cover.tif".format(city)
    cmd = '{0}/gdal_rasterize.exe -a WATER_COVE -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
        .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)

    # exporting train station- counts by isochrones
    years=[1990,1992,1994,1996,1998,2000,2002,2004,2006,2008,2010,2012,2014,2016,2018,2020]
    for year in years: 
    
        print("Rasterizing train station counts layer {0}".format(year))
        src_file = temp_shp_path +"/{1}_{0}_stationcount.shp".format(city,year)
        dst_file = temp_tif_path +"/{1}_{0}_stationcount.tif".format(city,year)
        cmd = '{0}/gdal_rasterize.exe -a STATIONCOU -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file)
        subprocess.call(cmd, shell=True)

    # exporting bus stops- counts by isochrones
    years=[]
    cur.execute("SELECT distinct(year) FROM {0}_busst where year% 2 = 0 order by year ASC;".format(city))
    year_id = cur.fetchall()
    for id in year_id:
        years.append(id[0])
    print(years)
        
    for year in years:
        print("Rasterizing bus stops counts layer {0}".format(year))
        src_file = temp_shp_path +"/{0}_busstopscount{1}.shp".format(city,year)
        dst_file = temp_tif_path +"/{1}_{0}_busstopscount.tif".format(city,year)
        cmd = '{0}/gdal_rasterize.exe -a BUSST_{9} -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file,year)
        subprocess.call(cmd, shell=True)

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
    cmd = '{0}/gdal_rasterize.exe -a "{9}" -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
            .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, layer)
    subprocess.call(cmd, shell=True)

    