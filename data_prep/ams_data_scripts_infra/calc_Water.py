import os
import subprocess
import gdal
import psycopg2
import time
import geopandas as gpd
from owslib.wfs import WebFeatureService


def importWaterLayers(ancillary_data_folder_path, temp_shp_path, city):
    bbox = gpd.read_file(temp_shp_path + "/{}_bbox.geojson".format(city))
    geoPortal = ["hy-p", "sr", "vin", "nl" ] # "hy-p", "sr", "vin", "nl"
    for i in geoPortal:
        wfs = WebFeatureService(url='https://geodata.nationaalgeoregister.nl/inspire/{}/wfs'.format(i), version='2.0.0')  
        contents = list(wfs.contents)
        for content in contents:  
            url = "https://geodata.nationaalgeoregister.nl/inspire/{0}/wfs?request=GetFeature&service=WFS&version=2.0.0&typeName={1}&outputFormat=application%2Fgml%2Bxml%3B%20version%3D3.2".format(i,content)
            print(url)
            df = gpd.read_file(url)
            df = df.to_crs("EPSG:3035")
            ndf = gpd.sjoin(df, bbox, op='intersects')
            
            if not ndf.empty:
                print(ndf.head(3))
                name = content.split(":")[-1]
                print(content, name)
                ndf.to_file(ancillary_data_folder_path + "/NLD_geoportal/{0}_{1}_{2}.geojson".format(city,i,name), driver="GeoJSON", crs='epsg:3035')

def processCanals(ancillary_data_folder_path, temp_shp_path, city, country, engine, cur ):
    waterCanals = gpd.read_file(ancillary_data_folder_path + "/water/noord-holland-latest-free.shp/gis_osm_water_a_free_1.shp")
    bbox = gpd.read_file(temp_shp_path + "/{}_bbox.geojson".format(city))
    waterCanals = waterCanals.to_crs('epsg:3035')
    ndf = gpd.clip(waterCanals, bbox)
    ndf.to_postgis('{0}_water'.format(city),engine)
        
    

def calculateWater(city,country,conn,cur):
    print("Set Coordinate system for GRID")
    cur.execute("SELECT UpdateGeometrySRID('{0}_grid','geometry',3035);;".format(city))  # 4.3 sec
    conn.commit()

    #-------------------------------------------------------------------------------------------------------------------
    print("Checking {0} cover analysis table".format(city))
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_cover_analysis');".format(
            city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis table".format(city))
        # Watercover percentage:
        cur.execute("Create table {0}_cover_analysis as \
                            (SELECT * \
                            FROM {0}_grid);".format(city))  # 4.3 sec
        conn.commit()
    else:
        print("{0} cover analysis table already exists".format(city))
    #-------------------------------------------------------------------------------------------------------------------

    print("Set Coordinate system for cover analysis")
    cur.execute("SELECT UpdateGeometrySRID('{0}_cover_analysis','geometry',3035);;".format(city))  # 4.3 sec
    conn.commit()

    # Adding necessary columns to city cover analysis table ---------------------------------------------------------
    print("---------- Adding necessary column to {0}_cover_analysis table, if they don't exist ----------".format(city))

    print("Checking {0} cover analysis - water cover column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                FROM information_schema.columns \
                WHERE table_schema='public' AND table_name='{0}_cover_analysis' AND column_name='water_cover');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - water cover column".format(city))
        # Adding water cover column to cover analysis table
        cur.execute(
            "Alter table {0}_cover_analysis \
            ADD column water_cover double precision default 0, \
            add column id SERIAL PRIMARY KEY;".format(city))  # 11.3 sec
        conn.commit()
    else:
        print("{0} cover analysis - water cover column already exists".format(city))

# Indexing necessary tables ----------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    print("Checking gist index on {0} water table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace \
                    WHERE c.relname = '{0}_water_gix' AND n.nspname = 'public');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating gist index on {0} water table".format(city))
        # Creating index on water layer
        cur.execute("CREATE INDEX {0}_water_gix ON {0}_water USING GIST (geometry);".format(city))  # 32 msec
        conn.commit()
    else:
        print("Gist index on {0} water table already exists".format(city))
    #-------------------------------------------------------------------------------------------------------------------
    print("Checking id index on {0} cover analysis table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace \
                        WHERE c.relname = '{0}_cover_analysis_id_index' AND n.nspname = 'public');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating id index on {0} cover analysis table".format(city))
        # Create index on city water cover id
        cur.execute("CREATE INDEX {0}_cover_analysis_id_index ON {0}_cover_analysis (id);".format(city))  # 4.8 sec
        conn.commit()
    else:
        print("Id index on {0} cover analysis table already exists".format(city))
    #-------------------------------------------------------------------------------------------------------------------
    print("Checking gist index on {0} cover analysis table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace \
                            WHERE c.relname = '{0}_cover_analysis_gix' AND n.nspname = 'public');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating gist index on {0} cover analysis table".format(city))
        # Creating index on water layer
        cur.execute("CREATE INDEX {0}_cover_analysis_gix ON {0}_cover_analysis USING GIST (geometry);".format(city))
        conn.commit()
    else:
        print("Gist index on {0} cover analysis table already exists".format(city))

    #-------------------------------------------------------------------------------------------------------------------
    print("Set Coordinate system for ITERATION GRID")
    cur.execute("SELECT UpdateGeometrySRID('{0}_iteration_grid','geometry',3035);;".format(city))  # 4.3 sec
    conn.commit()

    # getting id number of chunks within the iteration grid covering the city ---------------------------------------
    ids = []
    cur.execute("SELECT gid FROM {0}_iteration_grid;".format(city))
    chunk_id = cur.fetchall()

    # saving ids to list
    for id in chunk_id:
        ids.append(id[0])
    # Processing queries / running the cover analysis-----------------------------------------------------------------------------------------------
    print("-------------------- PROCESSING COVERAGE ANALYSIS: {0} consists of {1} big chunks --------------------".format(city, len(ids)))

    # Calculating water cover percentage -------------------------------------------------------------------------------

    print("---------- Calculating water cover percentage ----------")
    # start total query time timer
    start_query_time = time.time()

    # preparing water table by subdividing city water table
    print("Creating subdivided water table")
    cur.execute(
        "CREATE TABLE subdivided_{0}_water AS (SELECT ST_Subdivide({0}_water.geometry, 40) AS geometry FROM {0}_water)".format(
            city))

    # create index on water
    cur.execute("CREATE INDEX subdivided_{0}_water_gix ON subdivided_{0}_water USING GIST (geometry);".format(city))

    # iterating through chunks
    for chunk in ids:
        # check if chunk is pure ocean
        cur.execute("SELECT {0}_iteration_grid.gid \
                            FROM {0}_iteration_grid, {0}_cs, {2}_cs \
                            WHERE ST_Intersects({0}_iteration_grid.geometry, {2}_cs.geometry) \
                            AND {0}_iteration_grid.gid = {1};".format(city, chunk, country))
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, setting water = 100 procent".format(chunk, len(ids)))
            # Setting the values of the whole chunk in city_cover_analysis - water_cover to 100 procent
            cur.execute("WITH a AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geometry \
                        FROM {0}_cover_analysis, {0}_iteration_grid \
                        WHERE {0}_iteration_grid.gid = {1} \
                        AND ST_Intersects({0}_cover_analysis.geometry, {0}_iteration_grid.geometry)) \
                        UPDATE {0}_cover_analysis SET water_cover = 100 FROM a WHERE a.id = {0}_cover_analysis.id;".format(
                city, chunk))
        else:
            print("Chunk number: {0} \ {1} is not empty, Processing...".format(chunk, len(ids)))
            # start single chunk query time timer
            t0 = time.time()
            # select cells that is within each chunk and create a new table
            cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geometry \
                            FROM {0}_cover_analysis, {0}_iteration_grid \
                            WHERE {0}_iteration_grid.gid = {1} \
                            AND ST_Intersects({0}_cover_analysis.geometry, {0}_iteration_grid.geometry));".format(city,
                                                                                                          chunk))  # 1.6 sec
            conn.commit()

            # create index on chunk
            cur.execute("CREATE INDEX chunk_nr{0}_gix ON chunk_nr{0} USING GIST (geometry);".format(chunk))  # 464 msec
            conn.commit()

            # calculating water cover percentage
            cur.execute("WITH a AS (SELECT chunk_nr{1}.id, sum(ST_AREA(ST_INTERSECTION(chunk_nr{1}.geometry, {0}_water.geometry))/10000*100) as water \
                            FROM chunk_nr{1}, {0}_water WHERE ST_intersects(chunk_nr{1}.geometry, {0}_water.geometry) \
                            GROUP BY id) \
                            UPDATE {0}_cover_analysis SET water_cover = water from a \
                            WHERE a.id = {0}_cover_analysis.id;".format(city, chunk))

            # drop chunk_nr table
            cur.execute("DROP TABLE chunk_nr{0};".format(chunk))  # 22 ms
            conn.commit()

            # stop single chunk query time timer
            t1 = time.time()

            # calculate single chunk query time in minutes
            total = (t1 - t0) / 60
            print("Chunk number: {0} took {1} minutes to process".format(chunk, total))

    # stop total query time timer
    stop_query_time = time.time()

    # calculate total query time in minutes
    total_query_time = (stop_query_time - start_query_time) / 60
    print("Total water cover query time : {0} minutes".format(total_query_time))
    
    # drop subdivided water table
    cur.execute("DROP TABLE subdivided_{0}_water;".format(city))  # 22 ms
    conn.commit()

    