import os
import subprocess
import time
import psycopg2
import geopandas as gpd

def importTrainsToDB(ancillary_data_folder_path,city,cur,conn,engine):
        #_______________________RAILWAYS________________________    
    railwaysPath = ancillary_data_folder_path + "/railways/trammetro2018.json"
    railways = gpd.read_file(railwaysPath)
    railways = railways.to_crs('epsg:3035')
    # Create Table for Railway
    print("---------- Creating table for city, if it doesn't exist ----------")
    print("Checking {0} Case Study table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_train');".format(city))
    check = cur.fetchone()
    if check[0] == True:
        print("{0} railway table already exists".format(city))

    else:
        print("Creating {0} railway ".format(city))
        railways.to_postgis('{0}_train'.format(city),engine)

    #_______________________RAILWAYS________________________    
    railwaysstPath = ancillary_data_folder_path + "/railways/trammetrost2018.json"
    railwaysst = gpd.read_file(railwaysstPath)
    railwaysst = railwaysst.to_crs('epsg:3035')
    # Create Table for Railway
    print("---------- Creating table for city, if it doesn't exist ----------")
    print("Checking {0} Case Study table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_trainst');".format(city))
    check = cur.fetchone()
    if check[0] == True:
        print("{0} railway Stops table already exists".format(city))

    else:
        print("Creating {0} railway ".format(city))
        railwaysst.to_postgis('{0}_trainst'.format(city),engine)

def openingYeartoMetroStations (ancillary_data_folder_path,city,cur,conn):
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_trainst');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Please insert data to Database".format(city))
        
    else:

        print("Line 26 --> 2005".format(city))
        cur.execute("""ALTER TABLE {0}_trainst ADD COLUMN lines integer""".format(city))
        conn.commit()

        print("Line 26 --> 2005".format(city))
        cur.execute("""with a as ( Select gid, array_length(x, 1) AS count \
            FROM {0}_trainst \
            CROSS JOIN LATERAL string_to_array("Lijn_select", '|') AS t(x) )
        
            UPDATE {0}_trainst SET lines = a.count from a where a.gid={0}_trainst.gid""".format(city))
        conn.commit()
 
       

################################################################################################### 

def computeTrainIsochronesWalk(ancillary_data_folder_path,city,cur,conn, year):
    # getting id numbers for train stations covering the city ---------------------------------------
    train_ids = []
    closestPoint_ids=[]
    #cur.execute("alter table {0}_trainst ADD COLUMN gid serial;".format(city))
    cur.execute("SELECT gid FROM {0}_trainst WHERE {0}_trainst.year <= {1};".format(city, year))
    train_id = cur.fetchall()
    for id in train_id:
        train_ids.append(id[0])
    print(train_ids)
    
    for point in train_ids:
        cur.execute("SELECT {0}_streets_vertices_pgr.id as start\
                        FROM\
                        {0}_streets_vertices_pgr,\
                        {0}_trainst\
                        WHERE {0}_trainst.gid = {1}\
                        ORDER BY ST_Distance({0}_streets_vertices_pgr.the_geom, {0}_trainst.geometry) ASC\
                        LIMIT 1 ;".format(city,point))
        closestPoint_id = cur.fetchall()
    
        for gid in closestPoint_id:
            closestPoint_ids.append(gid[0])
    
    print(closestPoint_ids)
    
    # Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating train_isochrones tables, if it doesn't exist ----------")
    print("Checking {0} train_isochrones table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_train_isochrones_{1}');".format(city,year))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} train_isochrones table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_train_isochrones_{1} (id int, geom geometry);".format(city,year))
        conn.commit()
    else:
        print("{0} train_isochrones table already exists".format(city))

    # saving ids to list
    for cl_id in closestPoint_ids:
        # Processing queries / running the cover analysis-----------------------------------------------------------------------------------------------
        print("-------------------- CREATING IDS FOR STARTING POINTS FOR train_isochrones (TRAIN STATIONS) --------------------")
        cur.execute("insert into {0}_train_isochrones_{1} (id) values ({2})".format(city, year, cl_id)) # average is 15 km/h
        conn.commit()

        # Processing queries / running the cover analysis-----------------------------------------------------------------------------------------------
        print("-------------------- CREATING train_isochrones FOR {0} TRAIN STATION --------------------".format(cl_id))
        cur.execute("update {0}_train_isochrones_{2} SET \
                        geom = (Select ST_ConcaveHull(ST_Collect(geometry),0.9,false) \
                        FROM {0}_streets   \
                        JOIN (SELECT edge FROM pgr_drivingdistance('SELECT gid as id, source, target, traveltime AS cost from {0}_streets', {1}, 15, false)) \
                        AS route \
                        ON {0}_streets.gid = route.edge) \
                        where id ={1}".format(city, cl_id, year)) # average is 15 km/h and travel time is 15'
        conn.commit()

def calculateTrainCountWalk(ancillary_data_folder_path, city, conn, cur, year):
   
    print("Checking {0} cover analysis - train stations column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                                FROM information_schema.columns \
                                WHERE table_schema='public' AND table_name='{0}_cover_analysis' \
                                AND column_name='{1}_stationcount');".format(city, year))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - train stations column".format(city))
        # Adding train stations column to country cover analysis table
        cur.execute("""Alter table {0}_cover_analysis ADD column "{1}_stationcount" int default 0;""".format(city, year))
        conn.commit()
    else:
        print("""{0} cover analysis - train "{1}_stationcount" column already exists""".format(city,year))

    # Calculating train stations based on count ----------------------------------------------------------------------------------------
    print("---------- Calculating train stations ----------")
    # start total query time timer
    start_query_time = time.time()
     # getting id number of chunks within the iteration grid covering the city ---------------------------------------
    ids = []
    cur.execute("SELECT gid FROM {0}_iteration_grid;".format(city))
    chunk_id = cur.fetchall()

    # saving ids to list
    for id in chunk_id:
        ids.append(id[0])

    # iterate through chunks
    for chunk in ids:
        # start single chunk query time timer
        t0 = time.time()

        # Create table containing centroids of the original small grid within the land cover of the country
        cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT id, ST_Centroid({0}_cover_analysis.geometry) AS geom \
                            FROM {0}_cover_analysis, {0}_iteration_grid \
                            WHERE {0}_iteration_grid.gid = {1} \
                            AND ST_Intersects({0}_iteration_grid.geometry, {0}_cover_analysis.geometry)\
                            AND {0}_cover_analysis.water_cover < 99.999);".format(city, chunk))  # 1.7 sec
        # check if chunk query above returns values or is empty
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, moving to next chunk".format(chunk, len(ids)))
            conn.rollback()
        else:
            conn.commit()
            print("Chunk number: {0} \ {1} is not empty, Processing...".format(chunk, len(ids)))

            # Index chunk
            cur.execute("CREATE INDEX chunk_nr{0}_gix ON chunk_nr{0} USING GIST (geom);".format(chunk))  # 175 ms
            conn.commit()

            # Counting number of train stations 
            cur.execute("""with a as (select chunk_nr{1}.id, count(*) from {0}_train_isochrones_{2}, chunk_nr{1} \
            where ST_Intersects(chunk_nr{1}.geom, {0}_train_isochrones_{2}.geom) \
            group by chunk_nr{1}.id) \
            update {0}_cover_analysis set "{2}_stationcount" = a.count from a where a.id = {0}_cover_analysis.id;""".format(city, chunk, year))  # 4.1 sec
            conn.commit()

            # Drop chunk_nr table
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
    print("Total road distance query time : {0} minutes".format(total_query_time)) #13min

    