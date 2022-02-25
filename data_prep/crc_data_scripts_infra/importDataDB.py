import os
import subprocess
import psycopg2
from osgeo import gdal
import geopandas as gpd
from rast_to_vec_grid import rasttovecgrid

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

def initPgRouting(pghost, pgport, pguser, pgpassword, pgdatabase, cur, conn):  
    # check for and add pgrouting extension if not existing
    cur.execute("SELECT * FROM pg_available_extensions \
                    WHERE name LIKE 'pgRouting';")
    check_postgis = cur.rowcount
    if check_postgis == 0:
        print("Adding extension pgRouting")
        cur.execute("CREATE EXTENSION pgRouting CASCADE;")
        conn.commit()


#_______________________First Files and Processes_________________________
# Import NutsFile, clip to Case Study extent
# Import Corine files, clip, use to create grid and iterate_grid 
# Import grids to DB and create BBox
def initialimports(engine,conn, cur, ancillary_data_folder_path,ancillary_EUROdata_folder_path, nuts3_cd1,city,country, temp_shp_path): #pgpath, pghost, pgport, pguser, pgpassword,pgdatabase,conn, cur,
    #create geodataframes from shapefiles
    # Loading shapefiles into postgresql and creating necessary 
    #_______________________NUTS3 AREAS_________________________
    print("Importing 2021 Nuts3 to postgres")

    NutsPath = ancillary_EUROdata_folder_path + "/ref-nuts-2021-01m/NUTS_RG_01M_2021_3035_LEVL_3/NUTS_RG_01M_2021_3035_LEVL_3.shp"
    nuts = gpd.read_file(NutsPath)
    nuts_country = nuts[nuts['CNTR_CODE'] == '{0}'.format(country.upper())]
    nuts_city = nuts[nuts['NUTS_ID'] == '{0}'.format(nuts3_cd1)]
    # Create Table for Country Case Study
    print("---------- Creating table for country, if it doesn't exist ----------")
    print("Checking {0} Case Study table".format(country))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_cs');".format(country))
    check = cur.fetchone()
    if check[0] == True:
        print("{0} Case Study Area Nuts3 table already exists".format(country))

    else:
        print("Creating {0} Case Study Area Nuts3".format(country))
        nuts_country.to_postgis('{0}_cs'.format(country),engine)

    # Create Table for City Case Study
    print("---------- Creating table for Case Study, if it doesn't exist ----------")
    print("Checking {0} Case Study table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_cs');".format(city))
    check = cur.fetchone()
    if check[0] == True:
        print("{0} Case Study Area Nuts3 table already exists".format(city))   
    else:
        print("Creating {0} Case Study Area Nuts3".format(city)) 
        nuts_city.to_postgis('{0}_cs'.format(city),engine)
    
    nuts_city.to_file(temp_shp_path + "/{}_cs.shp".format(city), driver="ESRI Shapefile")
    
    # Create Table for bbox
    print("---------- Creating table for Bbox, if it doesn't exist ----------")
    print("Checking {0} bounding box table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_bbox');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} bounding box table from grid".format(city))
        # bbox from NUTS3 (+buffer = 100m):
        cur.execute("create table {0}_bbox as \
                    SELECT ST_Buffer(ST_SetSRID(ST_Extent(geometry),3035) \
                    ,100,'endcap=square join=mitre') as geom FROM {0}_cs;".format(city))
        conn.commit()
    else:
        print("{0} bounding box table already exists".format(city))

    #Exporting BBox from postgres
    print("---------- Exporting BBox from postgres ----------")
    sql = "SELECT * FROM {}_bbox".format(city)
    bbox = gpd.read_postgis(sql, engine)
    bbox.to_file(temp_shp_path + "/{}_bbox.geojson".format(city), driver="GeoJSON", crs='epsg:3035')

def initialProcess(engine, ancillary_data_folder_path,ancillary_EUROdata_folder_path,pgpath, pghost, pgport, pguser, pgpassword,pgdatabase,conn, cur, nuts3_cd1, city,country, temp_shp_path, temp_tif_path, temp_tif_corine, python_scripts_folder_path):
   
    # ----- Clipping corine to case study extent ------------------------
    corinePath = ancillary_EUROdata_folder_path + "/corine"
    for file in os.listdir(corinePath):
        if file.endswith('.tif'):
            filePath = corinePath + "/" + file

            print("------------------------------ Clipping Corine rasters by extent of case study area ------------------------------")
            csPath =  temp_shp_path + "/{0}_bbox.geojson".format(city)
            print(csPath)
            cmds = 'gdalwarp -of GTiff -cutline "{0}" -crop_to_cutline -dstalpha "{2}/{5}" "{3}/{4}_{5}"'.format(csPath,filePath,corinePath, temp_tif_path,city, file)
            subprocess.call(cmds, shell=True)
    
    # ----- Splitting corine to categories ------------------------
    for file in os.listdir(temp_tif_path):
        if file.endswith('.tif') and file.startswith('{}_CLC_'.format(city)):
            print(file)
            filePath = temp_tif_path + "/" + file

            print("------------------------------ Splitting Corine rasters to categories: Urban Fabric (1.1) ------------------------------")
            cmds = 'python {3}/gdal_calc.py -A "{0}" --A_band=1 --outfile="{1}/corine/urbfabr_{2}" --calc="logical_and(A<=2,A>0)"'.format(filePath,temp_tif_path, file, python_scripts_folder_path)
            subprocess.call(cmds, shell=True)

            print("------------------------------ Splitting Corine rasters to categories: Industrial and commercial units and Other sites (1.2.1, 1.3) ------------------------------")
            cmds = 'python {3}/gdal_calc.py -A "{0}" --A_band=1 --outfile="{1}/corine/industry_{2}" --calc="(A==3)*1 + logical_and(A>=7,A<=9)*1"'.format(filePath,temp_tif_path, file, python_scripts_folder_path)
            subprocess.call(cmds, shell=True)

            print("------------------------------ Splitting Corine rasters to categories: Transport (1.2.2-1.2.4) ------------------------------")
            cmds = 'python {3}/gdal_calc.py -A "{0}" --A_band=1 --outfile="{1}/corine/transp_{2}" --calc="logical_and(A<=6,A>=4)"'.format(filePath,temp_tif_path, file, python_scripts_folder_path)
            subprocess.call(cmds, shell=True)

            print("------------------------------ Splitting Corine rasters to categories: Agriculture ------------------------------")
            cmds = 'python {3}/gdal_calc.py -A "{0}" --A_band=1 --outfile="{1}/corine/agric_{2}" --calc="logical_and(A<=22,A>=12)"'.format(filePath,temp_tif_path, file, python_scripts_folder_path)
            subprocess.call(cmds, shell=True)

            #print("------------------------------ Splitting Corine rasters to categories: Forests ------------------------------")
            #cmds = 'python {3}/gdal_calc.py -A "{0}" --A_band=1 --outfile="{1}/corine/fonat_{2}" --calc="logical_and(A<=34,A>=23)"'.format(filePath,temp_tif_path, file, python_scripts_folder_path)
            #subprocess.call(cmds, shell=True)

            print("------------------------------ Splitting Corine rasters to categories: Forests and Urban Grean Spaces and Leisure ------------------------------")
            cmds = 'python {3}/gdal_calc.py -A "{0}" --A_band=1 --outfile="{1}/corine/greenSpaces_{2}" --calc="logical_and(A>=10,A<=11)*1 + logical_and(A<=34,A>=23)*1"'.format(filePath,temp_tif_path, file, python_scripts_folder_path)
            subprocess.call(cmds, shell=True)

            #print("------------------------------ Splitting Corine rasters to categories:wetlands ------------------------------")
            #cmds = 'python {3}/gdal_calc.py -A "{0}" --A_band=1 --outfile="{1}/corine/wetln_{2}" --calc="logical_and(A<=39,A>=35)"'.format(filePath,temp_tif_path, file, python_scripts_folder_path)
            #subprocess.call(cmds, shell=True)

            print("------------------------------ Splitting Corine rasters to categories: Water Bodies and Wetlands------------------------------")
            cmds = 'python {3}/gdal_calc.py -A "{0}" --A_band=1 --outfile="{1}/corine/water_{2}" --calc="logical_and(A<=44,A>=35)"'.format(filePath,temp_tif_path, file, python_scripts_folder_path)
            subprocess.call(cmds, shell=True)

            #As the water bodies do not include the port of Copenhagen, it gets combined with other layer --> percentages of water cover 
            waterPerc = temp_tif_path + "/cph_water_cover.tif"
            print("------------------------------ Splitting Corine rasters to categories:Water Bodies and Wetlands Combines with water cover (percentages) produced in Postgres with (vectors) lakes, wetlands and sea  ------------------------------")
            cmds = 'python {3}/gdal_calc.py -A "{1}/corine/water_{2}" -B "{4}" --A_band=1 --B_band=1 --outfile="{1}/corine/waterComb_{2}" --calc="maximum(A*100, B)/100"'.format(filePath,temp_tif_path, file, python_scripts_folder_path, waterPerc)
            #subprocess.call(cmds, shell=True)
            
    # ----- Creating Grid ------------------------
    print("------------------------------ Creating Grid ------------------------------")
    print("Extracting corine extent for {0}".format(city))
    # Getting extent of ghs pop raster
    data = gdal.Open(temp_tif_path + "/{0}_CLC_2012_2018.tif".format(city))
    wkt = data.GetProjection()
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None

    # Creating polygon grid that matches the population grid and the corine-----------------------------------------------------------
    print("------------------------------ Creating vector grid for {0} ------------------------------".format(city))
    outpath = temp_shp_path + "/{0}_grid.shp".format(city)
    rasttovecgrid(outpath, minx, maxx, miny, maxy, 100, 100)

    grid = gpd.read_file(outpath)
    # Create Table for grid
    print("---------- Creating table for grid, if it doesn't exist ----------")
    print("Checking {0} grid Case Study table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_grid');".format(city))
    check = cur.fetchone()
    if check[0] == True:
        print("{0} table already exists".format(city))

    else:
        print("Creating {0} grid Case Study Area Nuts3".format(city))
        grid.to_postgis('{0}_grid'.format(city),engine)
    
    # Creating polygon grid with larger grid size, to split the smaller grid and iterate in postgis --------------------
    print("------------------------------ Creating larger iteration vector grid for {0} ------------------------------"
              .format(country))
    outpath = temp_shp_path + "/{0}_iteration_grid.shp".format(city)
    rasttovecgrid(outpath, minx, maxx, miny, maxy, 500, 500)

    iteration_grid = gpd.read_file(outpath)
    # Create Table for grid
    print("---------- Creating table for grid, if it doesn't exist ----------")
    print("Checking {0} iteration_grid Case Study table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_iteration_grid');".format(city))
    check = cur.fetchone()
    if check[0] == True:
        print("{0} iteration_grid table already exists".format(city))

    else:
        print("Creating {0} grid Case Study Area Nuts3".format(city))
        iteration_grid.to_postgis('{0}_iteration_grid'.format(city),engine)

    
def importWater(ancillary_data_folder_path, city, country,cur,conn):

    print("Checking {0} subdivided ocean table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_subdivided_ocean');".format(country))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} subdivided ocean table".format(country))
        # Ocean from administrative + bbox:
        cur.execute("create table {0}_subdivided_ocean as \
            Select ST_Subdivide(ST_Difference({0}_bbox.geom, (Select ST_UNION({1}_cs.geom) as union))) \
            as geom from {0}_bbox, {1}_cs group by {0}_bbox.geom;".format(city,country))
        conn.commit()
    else:
        print("{0} subdivided ocean table already exists".format(country))

    #-------------------------------------------------------------------------------------------------------------------
    print("Checking {0} subdivided waterbodies table".format(city))

    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_water');".format(
                country))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} subdivided waterbodies table".format(city))
            # Creating waterbodies layer
        cur.execute("create table {0}_water as \
                                with a as ( \
                                select ST_Intersection(ST_UNION(ST_Transform(ST_Force2D(wetlands.geom), 3035),{0}_lakes.geom), {0}_cs.geom) as geom\
                                FROM {0}_lakes, {0}_cs, wetlands\
                                where ST_Intersects(ST_UNION(ST_Transform(ST_Force2D(wetlands.geom), 3035),{0}_lakes.geom), {0}_cs.geom))\
                                select geom FROM {0}_subdivided_ocean\
                                UNION\
                                select ST_Subdivide(ST_Union(geom)) from a;".format(city, country))  # 3.32 min
        conn.commit()
    else:
        print("{0} subdivided waterbodies table already exists".format(country))
    
#_______________________Train Stations_________________________
def importTrainStations(ancillary_data_folder_path,cur,conn):    
 
    # Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating necessary tables, if they don't exist ----------")
    print("Checking {0} train stations table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_trainst');".format(country))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} train stations table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_trainst as \
                    select trainst.gid, trainst.year, ST_Intersection(ST_Transform(trainst.geom, 3035), {0}_cs.geom) as geom\
                    FROM trainst, cph_cs\
                    where ST_Intersects(ST_Transform(trainst.geom, 3035), {0}_cs.geom);".format(city))
        conn.commit()
    else:
        print("{0} train stations table already exists".format(city))

    #_______________________Bus Stops_________________________
def importBusStops(ancillary_data_folder_path,city,conn,cur):
    
    # Creating table for Bus Stops ----------------------------------------------------------------------------------------
    print("---------- Creating necessary tables, if they don't exist ----------")
    print("Checking {0} bus stops table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_busst');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} bus stops table from case study extent".format(city))
        # table for bus stops in case study:
        cur.execute("create table {0}_busst as \
                    select busst.gid,busst.existsfrom, ST_Intersection(ST_Transform(busst.geom, 3035), {0}_cs.geom) as geom\
                    FROM busst, {0}_cs\
                    where ST_Intersects(ST_Transform(busst.geom, 3035), {0}_cs.geom);".format(city))
        conn.commit()
    else:
        print("{0} bus stops table already exists".format(city))

    # Creating column Year for Bus Stops ----------------------------------------------------------------------------------------
    print("Checking {0} Bus Stops - year column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                    FROM information_schema.columns \
                    WHERE table_schema='public' AND table_name='{0}_busst' AND column_name='year');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} Bus Stops - year column".format(city))
        # Adding road distance column to cover analysis table
        cur.execute(
            "Alter table {0}_busst ADD column year varchar default 0;\
            UPDATE {0}_busst SET year = LEFT(CAST(existsfrom AS varchar),4);\
                Alter table {0}_busst alter column year TYPE INT USING year::integer;".format(city))  # 14.8 sec
        conn.commit()
        
    else:
        print("{0} Bus Stops - year column already exists".format(city))
    
#_______________________Natural Environment (Forest, )_________________________
# Reprojection, Clip to Extent, Union, Rasterize

#_______________________Points of Interest_________________________

def importPointsofInterest(ancillary_data_folder_path,cur,conn):    
    # Loading shapefile into postgresql
    print("Importing PointsofInterest to postgres")
    railPath = ancillary_data_folder_path + "/pointsInterest/kkorg_enheder_offentlig.shp"
    cmds = 'shp2pgsql -I -s 4326  {0} public.pointsofinterst | psql'.format(railPath)
    print(cmds)
    subprocess.call(cmds, shell=True)

    # Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating necessary tables, if they don't exist ----------")
    print("Checking {0} schools table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_schools');".format(country))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} schools table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_schools as \
                    select pointsofinterst.id, pointsofinterst.enhedstype, pointsofinterst.enhedsnavn,\
                    pointsofinterst.type, ST_Intersection(ST_Transform(pointsofinterst.geom, 3035), {0}_cs.geom) as geom\
                    FROM pointsofinterst, cph_cs\
                    where ST_Intersects(ST_Transform(trainst.geom, 3035), {0}_cs.geom)\
                    AND pointsofinterst.enhedstype=  AND;".format(city))

        conn.commit()
    else:
        print("{0} train stations table already exists".format(city))