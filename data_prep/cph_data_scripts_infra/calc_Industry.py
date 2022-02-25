import os

import time
import geopandas as gpd

def calculateIndustry(ancillary_data_folder_path, temp_shp_path, engine, city, conn, cur):
    print(city)
    gdf = gpd.read_file(ancillary_data_folder_path + "/OSM/denmark-latest-free.shp/gis_osm_landuse_a_free_1.shp")
    gdf = gdf.loc[gdf['fclass'] == 'industrial' ]
    print('kati edo')
    path = "{0}/grootams_bbox.geojson".format(temp_shp_path,city)
    print(path)
    print('kati edo1')
    bbox = gpd.read_file(os.path.join(temp_shp_path + "/{}_bbox.geojson".format(city)))
    industryCanals = gdf.to_crs('epsg:3035')
    ndf = gpd.clip(industryCanals, bbox)
    ndf.to_postgis('{0}_industry'.format(city),engine)
    
    print("Set Coordinate system for GRID")
    cur.execute("SELECT UpdateGeometrySRID('{0}_grid','geom',3035);;".format(city))  # 4.3 sec
    conn.commit()

    # Adding necessary columns to city cover analysis table ---------------------------------------------------------
    print("---------- Adding necessary column to {0}_cover_analysis table, if they don't exist ----------".format(city))

    print("Checking {0} cover analysis - industry cover column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                FROM information_schema.columns \
                WHERE table_schema='public' AND table_name='{0}_cover_analysis' AND column_name='industry_cover');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - industry cover column".format(city))
        # Adding industry cover column to cover analysis table
        cur.execute(
            "Alter table {0}_cover_analysis \
            ADD column industry_cover double precision default 0;".format(city))  # 11.3 sec
        conn.commit()
    else:
        print("{0} cover analysis - industry cover column already exists".format(city))

# Indexing necessary tables ----------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------------------------------------
    print("Checking gist index on {0} industry table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace \
                    WHERE c.relname = '{0}_industry_gix' AND n.nspname = 'public');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating gist index on {0} industry table".format(city))
        # Creating index on industry layer
        cur.execute("CREATE INDEX {0}_industry_gix ON {0}_industry USING GIST (geometry);".format(city))  # 32 msec
        conn.commit()
    else:
        print("Gist index on {0} industry table already exists".format(city))
    #-------------------------------------------------------------------------------------------------------------------
    print("Checking id index on {0} cover analysis table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace \
                        WHERE c.relname = '{0}_cover_analysis_id_index' AND n.nspname = 'public');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating id index on {0} cover analysis table".format(city))
        # Create index on city industry cover id
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
        # Creating index on industry layer
        cur.execute("CREATE INDEX {0}_cover_analysis_gix ON {0}_cover_analysis USING GIST (geom);".format(city))
        conn.commit()
    else:
        print("Gist index on {0} cover analysis table already exists".format(city))

    # getting id number of chunks within the iteration grid covering the city ---------------------------------------
    ids = []
    cur.execute("SELECT gid FROM {0}_iteration_grid;".format(city))
    chunk_id = cur.fetchall()

    # saving ids to list
    for id in chunk_id:
        ids.append(id[0])
    # Processing queries / running the cover analysis-----------------------------------------------------------------------------------------------
    print("-------------------- PROCESSING COVERAGE ANALYSIS: {0} consists of {1} big chunks --------------------".format(city, len(ids)))

    # Calculating industry cover percentage -------------------------------------------------------------------------------

    print("---------- Calculating industry cover percentage ----------")
    # start total query time timer
    start_query_time = time.time()

    # iterating through chunks
    for chunk in ids:
        # check if chunk is pure ocean
        cur.execute("SELECT {0}_iteration_grid.gid \
                            FROM {0}_iteration_grid, {0}_industry \
                            WHERE ST_Intersects({0}_iteration_grid.geom, {0}_industry.geometry) \
                            AND {0}_iteration_grid.gid = {1};".format(city, chunk))
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, setting industry = 0 procent".format(chunk, len(ids)))
            # Setting the values of the whole chunk in city_cover_analysis - industry_cover to 100 procent
            cur.execute("WITH a AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geom \
                        FROM {0}_cover_analysis, {0}_iteration_grid \
                        WHERE {0}_iteration_grid.gid = {1} \
                        AND ST_Intersects({0}_cover_analysis.geom, {0}_iteration_grid.geom)) \
                        UPDATE {0}_cover_analysis SET industry_cover = 0 FROM a WHERE a.id = {0}_cover_analysis.id;".format(
                city, chunk))
        else:
            print("Chunk number: {0} \ {1} is not empty, Processing...".format(chunk, len(ids)))
            # start single chunk query time timer
            t0 = time.time()
            # select cells that is within each chunk and create a new table
            cur.execute("CREATE TABLE chunk_nr{1} AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geom \
                            FROM {0}_cover_analysis, {0}_iteration_grid \
                            WHERE {0}_iteration_grid.gid = {1} \
                            AND ST_Intersects({0}_cover_analysis.geom, {0}_iteration_grid.geom));".format(city,
                                                                                                          chunk))  # 1.6 sec
            conn.commit()

            # create index on chunk
            cur.execute("CREATE INDEX chunk_nr{0}_gix ON chunk_nr{0} USING GIST (geom);".format(chunk))  # 464 msec
            conn.commit()

            # calculating industry cover percentage
            cur.execute("WITH a AS (SELECT chunk_nr{1}.id, sum(ST_AREA(ST_INTERSECTION(chunk_nr{1}.geom, {0}_industry.geometry))/10000*100) as industry \
                            FROM chunk_nr{1}, {0}_industry WHERE ST_intersects(chunk_nr{1}.geom, {0}_industry.geometry) \
                            GROUP BY id) \
                            UPDATE {0}_cover_analysis SET industry_cover = industry from a \
                            WHERE a.id = {0}_cover_analysis.id;".format(city, chunk))

            # drop chunk_nr table
            cur.execute("DROP TABLE chunk_nr{0};".format(chunk))  # 22 ms
            conn.commit()

            # stop single chunk query time timer
            t1 = time.time()

            # calculate single chunk query time in minutes
            total = (t1 - t0) / 60
            print("Chunk number: {0} took {1} minutes to process".format(chunk, total))

    print("Alter water cover column")
    cur.execute("UPDATE {0}_cover_analysis SET industry_cover = 100 WHERE industry_cover > 100  ".format( city))
    conn.commit()
    # stop total query time timer
    stop_query_time = time.time()

    # calculate total query time in minutes
    total_query_time = (stop_query_time - start_query_time) / 60
    print("Total industry cover query time : {0} minutes".format(total_query_time))
    