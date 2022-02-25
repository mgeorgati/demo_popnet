import time
import geopandas as gpd
from basicFunctions import createFolder

# OPFOERELSE: Construction Year
def calculateMeanConstructionYear( city, conn, cur, year, BBRtype):
    print("Checking {0} cover analysis - housing column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                                FROM information_schema.columns \
                                WHERE table_schema='public' AND table_name='{0}_cover_analysis' \
                                AND column_name='{1}_{2}');".format(city,year, BBRtype))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - price column".format(city))
        # Adding prices column to country cover analysis table
        cur.execute("""Alter table {0}_cover_analysis ADD column "{1}_{2}" int default 0;""".format(city,year, BBRtype))
        conn.commit()
    else:
        print("""{0} cover analysis - housing prices "{1}_{2}" column already exists""".format(city,year, BBRtype))

    # Calculating housing prices based on mean value of the intersected points ----------------------------------------------------------------------------------------
    print("---------- Calculating mean housing value ----------")
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
        # check if chunk doesn't include any sold properties
        cur.execute("""SELECT {0}_iteration_grid.gid \
                            FROM {0}_iteration_grid, bbr_{0}_{2} \
                            WHERE ST_Intersects({0}_iteration_grid.geom, bbr_{0}_{2}.geometry) \
                            AND bbr_{0}_{2}."OPFOERELSE" is NOT null \
                            AND {0}_iteration_grid.gid = {1};""".format(city, chunk, year, BBRtype))
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, setting housingprices = 0".format(chunk, len(ids)))
            # Setting the values of the whole chunk in city_cover_analysis - housingprices to 0 
            cur.execute("""WITH a AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geom \
                        FROM {0}_cover_analysis, {0}_iteration_grid \
                        WHERE {0}_iteration_grid.gid = {1} \
                        AND ST_Intersects({0}_cover_analysis.geom, {0}_iteration_grid.geom)) \
                        UPDATE {0}_cover_analysis SET "{2}_{3}" = 0 FROM a WHERE a.id = {0}_cover_analysis.id;""".format(city, chunk, year, BBRtype))
        else:
            print("Chunk number: {0} \ {1} is not empty, Processing...".format(chunk, len(ids)))
            # start single chunk query time timer
            t0 = time.time()
            # Create table containing centroids of the original small grid within the land cover of the country
            cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geom \
                                FROM {0}_cover_analysis, {0}_iteration_grid \
                                WHERE {0}_iteration_grid.gid = {1} \
                                AND ST_Intersects({0}_iteration_grid.geom, {0}_cover_analysis.geom)\
                                AND {0}_cover_analysis.water_cover < 99.999);".format(city, chunk))  # 1.7 sec
            conn.commit()

            # Index chunk
            cur.execute("CREATE INDEX chunk_nr{0}_gix ON chunk_nr{0} USING GIST (geom);".format(chunk))  # 175 ms
            conn.commit()

            # Counting number of schoolss 
            cur.execute("""WITH a AS (select chunk_nr{1}.id, avg("OPFOERELSE") AS constr_year FROM bbr_{0}_{2}, chunk_nr{1} \
            WHERE bbr_{0}_{2}."OPFOERELSE" IS NOT NULL \
                AND ST_Intersects(chunk_nr{1}.geom, bbr_{0}_{2}.geometry) \
                GROUP BY chunk_nr{1}.id)  \
            UPDATE {0}_cover_analysis \
                SET "{2}_{3}" = CAST(ROUND(CAST(FLOAT8 (constr_year) AS NUMERIC),2 ) AS FLOAT) \
                FROM a WHERE a.id = {0}_cover_analysis.id;""".format(city, chunk, year, BBRtype))  # 4.1 sec           
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

##########################################################################################################################
# ETAGER_ANT: Number of floors
def calculateMeanFloors( city, conn, cur, year, BBRtype):
    print("Checking {0} cover analysis - housing column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                                FROM information_schema.columns \
                                WHERE table_schema='public' AND table_name='{0}_cover_analysis' \
                                AND column_name='{1}_{2}');".format(city,year, BBRtype))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - price column".format(city))
        # Adding prices column to country cover analysis table
        cur.execute("""Alter table {0}_cover_analysis ADD column "{1}_{2}" int default 0;""".format(city,year, BBRtype))
        conn.commit()
    else:
        print("""{0} cover analysis - number of floors "{1}_{2}" column already exists""".format(city,year, BBRtype))

    # Calculating housing prices based on mean value of the intersected points ----------------------------------------------------------------------------------------
    print("---------- Calculating mean housing value ----------")
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
        # check if chunk doesn't include any sold properties
        cur.execute("""SELECT {0}_iteration_grid.gid \
                            FROM {0}_iteration_grid, bbr_{0}_{2} \
                            WHERE ST_Intersects({0}_iteration_grid.geom, bbr_{0}_{2}.geometry) \
                            AND bbr_{0}_{2}."ETAGER_ANT" is NOT null \
                            AND {0}_iteration_grid.gid = {1};""".format(city, chunk, year, BBRtype))
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, setting housingprices = 0".format(chunk, len(ids)))
            # Setting the values of the whole chunk in city_cover_analysis - housingprices to 0 
            cur.execute("""WITH a AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geom \
                        FROM {0}_cover_analysis, {0}_iteration_grid \
                        WHERE {0}_iteration_grid.gid = {1} \
                        AND ST_Intersects({0}_cover_analysis.geom, {0}_iteration_grid.geom)) \
                        UPDATE {0}_cover_analysis SET "{2}_{3}" = 0 FROM a WHERE a.id = {0}_cover_analysis.id;""".format(city, chunk, year, BBRtype))
        else:
            print("Chunk number: {0} \ {1} is not empty, Processing...".format(chunk, len(ids)))
            # start single chunk query time timer
            t0 = time.time()
            # Create table containing centroids of the original small grid within the land cover of the country
            cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geom \
                                FROM {0}_cover_analysis, {0}_iteration_grid \
                                WHERE {0}_iteration_grid.gid = {1} \
                                AND ST_Intersects({0}_iteration_grid.geom, {0}_cover_analysis.geom)\
                                AND {0}_cover_analysis.water_cover < 99.999);".format(city, chunk))  # 1.7 sec
            conn.commit()

            # Index chunk
            cur.execute("CREATE INDEX chunk_nr{0}_gix ON chunk_nr{0} USING GIST (geom);".format(chunk))  # 175 ms
            conn.commit()

            # Counting number of schoolss 
            cur.execute("""WITH a AS (select chunk_nr{1}.id, avg("ETAGER_ANT") AS floors FROM bbr_{0}_{2}, chunk_nr{1} \
            WHERE bbr_{0}_{2}."ETAGER_ANT" IS NOT NULL \
                AND ST_Intersects(chunk_nr{1}.geom, bbr_{0}_{2}.geometry) \
                GROUP BY chunk_nr{1}.id)  \
            UPDATE {0}_cover_analysis \
                SET "{2}_{3}" = CAST(ROUND(CAST(FLOAT8 (floors) AS NUMERIC),2 ) AS FLOAT) \
                FROM a WHERE a.id = {0}_cover_analysis.id;""".format(city, chunk, year, BBRtype))  # 4.1 sec           
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