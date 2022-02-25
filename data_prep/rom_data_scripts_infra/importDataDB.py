import os
import subprocess
import psycopg2
from osgeo import gdal
import geopandas as gpd
from shapely.geometry import Polygon
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
        cur.execute("CREATE EXTENSION pgRouting;")
        conn.commit()
#_______________________First Files and Processes_________________________
# Import NutsFile, clip to Case Study extent
# Import Corine files, clip, use to create grid and iterate_grid 
# Import grids to DB and create BBox

def initialProcess(engine, gdal_rasterize_path, ancillary_data_folder_path, ancillary_EUROdata_folder_path,conn, cur, city, temp_shp_path, temp_tif_path,  python_scripts_folder_path):
    #create geodataframes from shapefiles
    # Loading shapefiles into postgresql and creating necessary 
    #_______________________NUTS3 AREAS_________________________
    print("Importing municipality")

    NutsPath = ancillary_data_folder_path + "/adm/rom_municipality.geojson"
    nuts_city = gpd.read_file(NutsPath)


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
    
    nuts_city.to_file(temp_shp_path + "/{}_cs.geojson".format(city), driver="GeoJSON")

    # ----- Clipping corine to case study extent ------------------------
    corinePath = ancillary_EUROdata_folder_path + "/corine"
    for file in os.listdir(corinePath):
        if file.endswith('.tif'):
            filePath = corinePath + "/" + file

            print("------------------------------ Clipping Corine rasters by extent of case study area ------------------------------")
            csPath =  temp_shp_path + "/{0}_cs.geojson".format(city)
            cs = gpd.read_file(csPath)
            minx, miny, maxx, maxy = cs.geometry.total_bounds
            print(minx, miny, maxx, maxy)
            p1 = Polygon([(minx, miny), (minx, maxy),  (maxx, maxy),(maxx, miny)])
            bbox = gpd.GeoSeries(p1)
            bbox.to_file(temp_shp_path + "/{}_bbox.geojson".format(city), driver="GeoJSON", crs="EPSG:3035")
            bboxPath = temp_shp_path + "/{}_bbox.geojson".format(city)
            cmds = '{6}/gdalwarp.exe -of GTiff -cutline "{0}" -crop_to_cutline -dstalpha "{2}/{5}" "{3}/{4}_{5}"'.format(bboxPath,filePath,corinePath, temp_tif_path,city, file, gdal_rasterize_path, minx, maxx, miny, maxy)
            print(cmds)
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

            print("------------------------------ Splitting Corine rasters to categories: Forests and Urban Grean Spaces and Leisure ------------------------------")
            cmds = 'python {3}/gdal_calc.py -A "{0}" --A_band=1 --outfile="{1}/corine/greenSpaces_{2}" --calc="logical_and(A>=10,A<=11)*1 + logical_and(A<=34,A>=23)*1"'.format(filePath,temp_tif_path, file, python_scripts_folder_path)
            subprocess.call(cmds, shell=True)

            print("------------------------------ Splitting Corine rasters to categories: Water Bodies and Wetlands------------------------------")
            cmds = 'python {3}/gdal_calc.py -A "{0}" --A_band=1 --outfile="{1}/corine/water_{2}" --calc="logical_and(A<=44,A>=35)"'.format(filePath,temp_tif_path, file, python_scripts_folder_path)
            subprocess.call(cmds, shell=True)

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
    outpath = temp_shp_path + "/{0}_grid.geojson".format(city)
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
              .format(city))
    outpath = temp_shp_path + "/{0}_iteration_grid.geojson".format(city)
    rasttovecgrid(outpath, minx, maxx, miny, maxy, 500, 500)

    iteration_grid = gpd.read_file(outpath)
    #iteration_grid.crs="EPSG=3035"
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

