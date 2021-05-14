import os
import subprocess
import psycopg2
import time
city= 'cph'
pgpath = r';C:\Program Files\PostgreSQL\9.5\bin'
pghost = 'localhost'
pgport = '5432'
pguser = 'postgres'
pgpassword = 'postgres'
pgdatabase = '{}_data'.format(city)
ancillary_data_folder_path = "C:/FUME/popnetv2/data_scripts/ProjectData/AncillaryData"

#_______________________Roads_________________________
# Process shp adding field and defining the train stations (0),metro stations M1,2 (2000), metro stations M3,4 (2020)
# Import shp to postgres, clip to case study extent,

def all_aboutBuses(ancillary_data_folder_path,city,conn,cur):

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

def bus_columns(conn,cur,city, endYear):
        print("Checking {0} bus analysis - distance column per year of analysis".format(city))
        cur.execute("SELECT EXISTS (SELECT 1 \
                        FROM information_schema.columns \
                        WHERE table_schema='public' AND table_name='{0}_cover_analysis' AND column_name='busst_2000');".format(
            city))
        check = cur.fetchone()
        if check[0] == False:
            print("Creating {0} bus analysis - bus stop distance column".format(city))
            # Adding road distance column to cover analysis table
            cur.execute(
                "Alter table {0}_cover_analysis ADD column busst_2000 int default 0;".format(
                    city))  # 14.8 sec
            conn.commit()
        else:
            print("{0} cover analysis - bus stop busst_2000 column already exists".format(city))

        print("Checking {0} bus analysis - distance column per year of analysis".format(city))
        cur.execute("SELECT EXISTS (SELECT 1 \
                        FROM information_schema.columns \
                        WHERE table_schema='public' AND table_name='{0}_cover_analysis' AND column_name='busst_{1}');".format(
            city,endYear))
        check = cur.fetchone()
        if check[0] == False:
            print("Creating {0} bus analysis - bus stop distance column".format(city))
            # Adding road distance column to cover analysis table
            cur.execute(
                "Alter table {0}_cover_analysis ADD column busst_{1} int default 0;".format(
                    city, endYear))  # 14.8 sec
            conn.commit()
        else:
            print("{0} cover analysis - bus stop busst_{1} column already exists".format(city,endYear))

def bus_analysis(conn,cur,city, startYear,midYear, endYear):
        # Calculating bus stops based on count ----------------------------------------------------------------------------------------
        print("---------- Calculating bus stops for years: {0}, {1}----------".format(startYear, endYear))
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
                                AND ST_Intersects({0}_iteration_grid.geom, {0}_cover_analysis.geom) \
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
                
                # Counting number of train stations within x km distance
                cur.execute("with a as (select chunk_nr{1}.id, count(*) from {0}_busst, chunk_nr{1} \
                where st_dwithin(chunk_nr{1}.geom, {0}_busst.geom, 400) AND \
                {0}_busst.year = 2000  \
                group by chunk_nr{1}.id) \
                update {0}_cover_analysis set busst_2000 = a.count from a where a.id = {0}_cover_analysis.id;".format(city, chunk))  # 4.1 sec
                conn.commit()

                # Counting number of train stations within x km distance
                cur.execute("with a as (select chunk_nr{1}.id, count(*) from {0}_busst, chunk_nr{1} \
                where st_dwithin(chunk_nr{1}.geom, {0}_busst.geom, 400) AND \
                {0}_busst.year <={2} \
                group by chunk_nr{1}.id) \
                update {0}_cover_analysis set busst_{3} = a.count from a where a.id = {0}_cover_analysis.id;".format(city, chunk, midYear, endYear))  # 4.1 sec
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

def iterate_busAnalysis(conn,cur,city):
    startYear = 2000
    
    while startYear <= 2022:
        start = 2000
        midYear = startYear+1
        endYear = startYear+2
        print("1.",start, startYear, midYear, endYear)
        
        bus_columns(conn,cur,city, endYear)
        bus_analysis(conn,cur,city,startYear,midYear, endYear)
        startYear += 2

def computeBusIsochrones(ancillary_data_folder_path, city, cur, conn, year):
    # getting id numbers for bus stops covering the city ---------------------------------------
    bus_ids = []
    closestPoint_ids=[]
    cur.execute("SELECT gid FROM {0}_busst where {0}_busst.year <= {1};".format(city,year))
    bus_id = cur.fetchall()
    for id in bus_id:
        bus_ids.append(id[0])
    print(bus_ids)
    
    for point in bus_ids:
        cur.execute("SELECT {0}_streets_vertices_pgr.id as start\
                        FROM\
                        {0}_streets_vertices_pgr,\
                        {0}_busst\
                        WHERE {0}_busst.gid = {1}\
                        ORDER BY ST_Distance({0}_streets_vertices_pgr.the_geom, {0}_busst.geom) ASC\
                        LIMIT 1 ;".format(city,point))
        closestPoint_id = cur.fetchall()
    
        for gid in closestPoint_id:
            closestPoint_ids.append(gid[0])
    
    print(closestPoint_ids)
    
    # Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating busIsochrones table, if it doesn't exist ----------")
    print("Checking {0} busIsochrones table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_busIsochrones_{1}');".format(city,year))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} busIsochrones table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_busIsochrones_{1} (id int, geom geometry);".format(city,year))
        conn.commit()
    else:
        print("{0} busIsochrones table already exists".format(city))

    # saving ids to list
    for cl_id in closestPoint_ids:
        # Processing queries / running the cover analysis-----------------------------------------------------------------------------------------------
        print("-------------------- CREATING IDS FOR STARTING POINTS FOR ISOCHRONES (BUS STOPS) --------------------")
        cur.execute("insert into {0}_busIsochrones_{1} (id) values ({2})".format(city, year, cl_id)) # average is 5 km/h
        conn.commit()

        # Processing queries / running the cover analysis-----------------------------------------------------------------------------------------------
        print("-------------------- CREATING ISOCHRONES FOR {0} BUS STATIONS {1}--------------------".format(cl_id,year))
        cur.execute("update {0}_busIsochrones_{2} SET \
                        geom = (Select ST_ConcaveHull(ST_Collect(geom),0.9,false) \
                        FROM {0}_streets   \
                        JOIN (SELECT edge FROM pgr_drivingdistance('SELECT gid as id, source, target, traveltime AS cost from {0}_streets', {1}, 5, false)) \
                        AS route \
                        ON {0}_streets.gid = route.edge) \
                        where id ={1}".format(city, cl_id, year)) 
        conn.commit()

def calculateBusCount(ancillary_data_folder_path, city, conn, cur, year):
   
    print("Checking {0} cover analysis - train stations column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                                FROM information_schema.columns \
                                WHERE table_schema='public' AND table_name='{0}_cover_analysis' \
                                AND column_name='busstopscount_{1}');".format(city,year))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - train stations column".format(city))
        # Adding train stations column to country cover analysis table
        cur.execute("Alter table {0}_cover_analysis ADD column busstopscount_{1} int default 0;".format(city,year))
        conn.commit()
    else:
        print("{0} cover analysis - train busstopscount_{1} column already exists".format(city,year))

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
            cur.execute("with a as (select chunk_nr{1}.id, count(*) from {0}_busIsochrones_{2}, chunk_nr{1} \
            where ST_Intersects(chunk_nr{1}.geom, {0}_busIsochrones_{2}.geom) \
            group by chunk_nr{1}.id) \
            update {0}_cover_analysis set busstopscount_{2} = a.count from a where a.id = {0}_cover_analysis.id;".format(city, chunk, year))  # 4.1 sec
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


        