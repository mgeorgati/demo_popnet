import os
import subprocess
import time
import psycopg2

def computeTrainIsochrones(ancillary_data_folder_path,city, cur,conn,year):
    # getting id numbers for train stations covering the city ---------------------------------------
    train_ids = []
    closestPoint_ids=[]
    cur.execute("SELECT gid FROM {0}_trainst where {0}_trainst.year <= {1};".format(city,year))
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
                        ORDER BY ST_Distance({0}_streets_vertices_pgr.the_geom, {0}_trainst.geom) ASC\
                        LIMIT 1 ;".format(city,point))
        closestPoint_id = cur.fetchall()
    
        for gid in closestPoint_id:
            closestPoint_ids.append(gid[0])
    
    print(closestPoint_ids)
    
    # Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating isochrones tables, if it doesn't exist ----------")
    print("Checking {0} isochrones table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_isochrones_{1}');".format(city,year))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} isochrones table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_isochrones_{1} (id int, geom geometry);".format(city,year))
        conn.commit()
    else:
        print("{0} isochrones table already exists".format(city))

    # saving ids to list
    for cl_id in closestPoint_ids:
        # Processing queries / running the cover analysis-----------------------------------------------------------------------------------------------
        print("-------------------- CREATING IDS FOR STARTING POINTS FOR ISOCHRONES (TRAIN STATIONS) --------------------")
        cur.execute("insert into {0}_isochrones_{1} (id) values ({2})".format(city, year, cl_id)) # average is 15 km/h
        conn.commit()

        # Processing queries / running the cover analysis-----------------------------------------------------------------------------------------------
        print("-------------------- CREATING ISOCHRONES FOR {0} TRAIN STATION --------------------".format(cl_id))
        cur.execute("update {0}_isochrones_{2} SET \
                        geom = (Select ST_ConcaveHull(ST_Collect(geom),0.9,false) \
                        FROM {0}_streets   \
                        JOIN (SELECT edge FROM pgr_drivingdistance('SELECT gid as id, source, target, traveltime AS cost from {0}_streets', {1}, 15, false)) \
                        AS route \
                        ON {0}_streets.gid = route.edge) \
                        where id ={1}".format(city, cl_id, year)) # average is 15 km/h and travel time is 15'
        conn.commit()

def calculateTrainCount(ancillary_data_folder_path, city, conn, cur, year):
   
    print("Checking {0} cover analysis - train stations column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                                FROM information_schema.columns \
                                WHERE table_schema='public' AND table_name='{0}_cover_analysis' \
                                AND column_name='{1}_stationcount');".format(city,year))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - train stations column".format(city))
        # Adding train stations column to country cover analysis table
        cur.execute("""Alter table {0}_cover_analysis ADD column "{1}_stationcount" int default 0;""".format(city,year))
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
        cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT id, ST_Centroid({0}_cover_analysis.geom) AS geom \
                            FROM {0}_cover_analysis, {0}_iteration_grid \
                            WHERE {0}_iteration_grid.gid = {1} \
                            AND ST_Intersects({0}_iteration_grid.geom, {0}_cover_analysis.geom)\
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
            cur.execute("""with a as (select chunk_nr{1}.id, count(*) from {0}_isochrones_{2}, chunk_nr{1} \
            where ST_Intersects(chunk_nr{1}.geom, {0}_isochrones_{2}.geom) \
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
        

    

    