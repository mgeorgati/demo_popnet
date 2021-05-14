import os
import subprocess
import gdal
import psycopg2
import time

#_______________________Railway Stations_________________________
# Process shp adding field and defining the train stations (0),metro stations M1,2 (2000), metro stations M3,4 (2020)
# Import shp to postgres, clip to case study extent,

def calculateRail(ancillary_data_folder_path, city,country,conn,cur):
   
    print("Checking {0} cover analysis - train stations column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                                FROM information_schema.columns \
                                WHERE table_schema='public' AND table_name='{0}_cover_analysis' \
                                AND column_name='station');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - train stations column".format(city))
        # Adding train stations column to country cover analysis table
        cur.execute("Alter table {0}_cover_analysis ADD column station int default 0;".format(city))
        conn.commit()
    else:
        print("{0} cover analysis - train stations column already exists".format(city))

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
            cur.execute("with a as (select chunk_nr{1}.id, count(*) from {0}_trainst, chunk_nr{1} \
            where st_dwithin(chunk_nr{1}.geom, {0}_trainst.geom, 1500) \
            group by chunk_nr{1}.id) \
            update {0}_cover_analysis set station = a.count from a where a.id = {0}_cover_analysis.id;".format(city, chunk))  # 4.1 sec
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



def calculateRailBuffers(city,conn,cur):
# Calculating train buffers for trains before 2006 (without metro) ----------------------------------------------------------------------------------------
    print("Checking {0} cover analysis - train stations column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                                FROM information_schema.columns \
                                WHERE table_schema='public' AND table_name='{0}_cover_analysis' \
                                AND column_name='trainst_buffer_1990');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - train stations column".format(city))
        # Adding train stations column to country cover analysis table
        cur.execute("Alter table {0}_cover_analysis ADD column trainst_buffer_1990 int default 0;".format(city))
        conn.commit()
    else:
        print("{0} cover analysis - train trainst_buffer_1990 column already exists".format(city))

     # Calculating train stations----------------------------------------------------------------------------------------
    print("---------- Calculating train stations for 1990s ----------")
    # start total query time timer
    start_query_time = time.time()

    # Here I can change it in for loop with dictionary/lists#################
    t0 = time.time()
    print("---------- Calculating 1st buffer ----------")
    # Calculating the grids in distance 0-500m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where {0}_trainst.year= '0'\
            AND ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 500), ST_Buffer({0}_trainst.geom, 0)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_1990 = 1 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 2nd buffer ----------")
    # Calculating the grids in distance 500-1000m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where {0}_trainst.year= '0'\
            AND ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 1000), ST_Buffer({0}_trainst.geom, 500)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_1990 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_1990 = 2 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 3rd buffer ----------")
    # Calculating the grids in distance 1000-1500m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where {0}_trainst.year= '0'\
            AND ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 1500), ST_Buffer({0}_trainst.geom, 1000)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_1990 != 2\
            AND {0}_cover_analysis.trainst_buffer_1990 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_1990 = 3 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 4rth buffer ----------")
    # Calculating the grids in distance 1500-2000m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where {0}_trainst.year= '0'\
            AND ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 2000), ST_Buffer({0}_trainst.geom, 1500)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_1990 != 3\
            AND {0}_cover_analysis.trainst_buffer_1990 != 2\
            AND {0}_cover_analysis.trainst_buffer_1990 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_1990 = 4 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 5th buffer ----------")
    # Calculating the grids in distance 2000-2500m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where {0}_trainst.year= '0'\
            AND ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 2500), ST_Buffer({0}_trainst.geom, 2000)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_1990 != 4\
            AND {0}_cover_analysis.trainst_buffer_1990 != 3\
            AND {0}_cover_analysis.trainst_buffer_1990 != 2\
            AND {0}_cover_analysis.trainst_buffer_1990 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_1990 = 5 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

# Calculating train buffers for trains before 2020 (with M1,M2)----------------------------------------------------------------------------------------
    print("Checking {0} cover analysis - train stations column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                                FROM information_schema.columns \
                                WHERE table_schema='public' AND table_name='{0}_cover_analysis' \
                                AND column_name='trainst_buffer_2000');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - train stations column".format(city))
        # Adding train stations column to country cover analysis table
        cur.execute("Alter table {0}_cover_analysis ADD column trainst_buffer_2000 int default 0;".format(city))
        conn.commit()
    else:
        print("{0} cover analysis - train trainst_buffer_1990 column already exists".format(city))

     # Calculating train stations----------------------------------------------------------------------------------------
    print("---------- Calculating train stations for 2000s----------")
    # start total query time timer
    start_query_time = time.time()

    # Here I can change it in for loop with dictionary/lists################# OR {0}_cover_analysis.trainst_buffer_2000=0\
    t0 = time.time()
    print("---------- Calculating 1st buffer ----------")
    # Calculating the grids in distance 0-500m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where {0}_trainst.year= '0' AND {0}_trainst.year= '2000'\
            AND ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 500), ST_Buffer({0}_trainst.geom, 0)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_2000 = 1 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 2nd buffer ----------")
    # Calculating the grids in distance 500-1000m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where {0}_trainst.year= '0' AND {0}_trainst.year= '2000'\
            AND ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 1000), ST_Buffer({0}_trainst.geom, 500)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_2000 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_2000 = 2 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 3rd buffer ----------")
    # Calculating the grids in distance 1000-1500m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where {0}_trainst.year= '0' AND {0}_trainst.year= '2000'\
            AND ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 1500), ST_Buffer({0}_trainst.geom, 1000)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_2000 != 2\
            AND {0}_cover_analysis.trainst_buffer_2000 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_2000 = 3 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 4rth buffer ----------")
    # Calculating the grids in distance 1500-2000m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where {0}_trainst.year= '0' AND {0}_trainst.year= '2000'\
            AND ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 2000), ST_Buffer({0}_trainst.geom, 1500)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_2000 != 3\
            AND {0}_cover_analysis.trainst_buffer_2000 != 2\
            AND {0}_cover_analysis.trainst_buffer_2000 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_2000 = 4 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 5th buffer ----------")
    # Calculating the grids in distance 2000-2500m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where {0}_trainst.year= '0' AND {0}_trainst.year= '2000'\
            AND ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 2500), ST_Buffer({0}_trainst.geom, 2000)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_2000 != 4\
            AND {0}_cover_analysis.trainst_buffer_2000 != 3\
            AND {0}_cover_analysis.trainst_buffer_2000 != 2\
            AND {0}_cover_analysis.trainst_buffer_2000 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_2000 = 5 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    # Calculating train buffers for trains AFTER 2020 (with M3,M4)----------------------------------------------------------------------------------------
    print("Checking {0} cover analysis - train stations column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                                FROM information_schema.columns \
                                WHERE table_schema='public' AND table_name='{0}_cover_analysis' \
                                AND column_name='trainst_buffer_2020');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - train stations column".format(city))
        # Adding train stations column to country cover analysis table
        cur.execute("Alter table {0}_cover_analysis ADD column trainst_buffer_2020 int default 0;".format(city))
        conn.commit()
    else:
        print("{0} cover analysis - train trainst_buffer_2020 column already exists".format(city))

     # Calculating train stations----------------------------------------------------------------------------------------
    print("---------- Calculating train stations 2020 ----------")
    # start total query time timer
    start_query_time = time.time()

    # Here I can change it in for loop with dictionary/lists#################
    t0 = time.time()
    print("---------- Calculating 1st buffer ----------")
    # Calculating the grids in distance 0-500m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 500), ST_Buffer({0}_trainst.geom, 0)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_2020 = 1 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 2nd buffer ----------")
    # Calculating the grids in distance 500-1000m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 1000), ST_Buffer({0}_trainst.geom, 500)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_2020 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_2020 = 2 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 3rd buffer ----------")
    # Calculating the grids in distance 1000-1500m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 1500), ST_Buffer({0}_trainst.geom, 1000)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_2020 != 2\
            AND {0}_cover_analysis.trainst_buffer_2020 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_2020 = 3 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 4rth buffer ----------")
    # Calculating the grids in distance 1500-2000m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 2000), ST_Buffer({0}_trainst.geom, 1500)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_2020 != 3\
            AND {0}_cover_analysis.trainst_buffer_2020 != 2\
            AND {0}_cover_analysis.trainst_buffer_2020 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_2020 = 4 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    print("---------- Calculating 5th buffer ----------")
    # Calculating the grids in distance 2000-2500m
    cur.execute("with a as (select {0}_cover_analysis.gid, ST_Centroid({0}_cover_analysis.geom) from {0}_trainst, {0}_cover_analysis\
            where ST_Intersects(ST_Centroid({0}_cover_analysis.geom), ST_Difference(ST_Buffer({0}_trainst.geom, 2500), ST_Buffer({0}_trainst.geom, 2000)))\
            AND {0}_cover_analysis.water_cover < 99.999\
            AND {0}_cover_analysis.trainst_buffer_2020 != 4\
            AND {0}_cover_analysis.trainst_buffer_2020 != 3\
            AND {0}_cover_analysis.trainst_buffer_2020 != 2\
            AND {0}_cover_analysis.trainst_buffer_2020 != 1\
            group by {0}_cover_analysis.gid, {0}_cover_analysis.geom)\
            update {0}_cover_analysis set trainst_buffer_2020 = 5 from a where a.gid = {0}_cover_analysis.id;".format(city))  # 4.1 sec
    conn.commit()

    t1 = time.time()

        # calculate single chunk query time in minutes
    total = (t1 - t0) / 60

    # stop total query time timer
    stop_query_time = time.time()

    # calculate total query time in minutes
    total_query_time = (stop_query_time - start_query_time) / 60
    print("Total train distance query time : {0} minutes".format(total_query_time)) #

    