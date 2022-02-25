import os
import subprocess
from osgeo import gdal
import time
import geopandas as gpd

def calculateindustry(ancillary_data_folder_path, temp_shp_path, engine, city,country,conn,cur):
    gdf = gpd.read_file(ancillary_data_folder_path + "/OSM/noord-holland-latest-free.shp/gis_osm_landuse_a_free_1.shp")
    gdf = gdf.loc[gdf['fclass'] == 'industrial' ]
    bbox = gpd.read_file(temp_shp_path + "/{}_bbox.geojson".format(city))
    industryCanals = gdf.to_crs('epsg:3035')
    ndf = gpd.clip(industryCanals, bbox)
    ndf.to_postgis('{0}_industry'.format(city),engine)
    
    print("Set Coordinate system for GRID")
    cur.execute("SELECT UpdateGeometrySRID('{0}_grid','geometry',3035);;".format(city))  # 4.3 sec
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

    # Calculating industry cover percentage -------------------------------------------------------------------------------

    print("---------- Calculating industry cover percentage ----------")
    # start total query time timer
    start_query_time = time.time()

    # iterating through chunks
    for chunk in ids:
        # check if chunk is pure ocean
        cur.execute("SELECT {0}_iteration_grid.gid \
                            FROM {0}_iteration_grid, {0}_cs, {2}_cs \
                            WHERE ST_Intersects({0}_iteration_grid.geometry, {2}_cs.geometry) \
                            AND {0}_iteration_grid.gid = {1};".format(city, chunk, country))
        result_check = cur.rowcount

        if result_check == 0:
            print("Chunk number: {0} \ {1} is empty, setting industry = 100 procent".format(chunk, len(ids)))
            # Setting the values of the whole chunk in city_cover_analysis - industry_cover to 100 procent
            cur.execute("WITH a AS (SELECT {0}_cover_analysis.id, {0}_cover_analysis.geometry \
                        FROM {0}_cover_analysis, {0}_iteration_grid \
                        WHERE {0}_iteration_grid.gid = {1} \
                        AND ST_Intersects({0}_cover_analysis.geometry, {0}_iteration_grid.geometry)) \
                        UPDATE {0}_cover_analysis SET industry_cover = 100 FROM a WHERE a.id = {0}_cover_analysis.id;".format(
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

            # calculating industry cover percentage
            cur.execute("WITH a AS (SELECT chunk_nr{1}.id, sum(ST_AREA(ST_INTERSECTION(chunk_nr{1}.geometry, {0}_industry.geometry))/10000*100) as industry \
                            FROM chunk_nr{1}, {0}_industry WHERE ST_intersects(chunk_nr{1}.geometry, {0}_industry.geometry) \
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

    # stop total query time timer
    stop_query_time = time.time()

    # calculate total query time in minutes
    total_query_time = (stop_query_time - start_query_time) / 60
    print("Total industry cover query time : {0} minutes".format(total_query_time))
    

def industry_dbTOtif(city, gdal_rasterize_path, cur, conn, engine, xres, yres, temp_shp_path, temp_tif_path, python_scripts_folder_path):
    print("Alter industry cover column")
    cur.execute("UPDATE {0}_cover_analysis SET industry_cover = 100 WHERE industry_cover > 100  ".format( city))
    conn.commit()
    # Create SQL Query
    sql = "SELECT id, industry_cover, geometry FROM {0}_cover_analysis".format( city)
    # Read the data with Geopandas
    gdf = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col='geometry' )
    print(gdf.head(4))    

    # exporting industry cover from postgres
    print("Exporting {0} industry_cover from postgres".format(city))
    gdf.to_file(temp_shp_path + "/{0}_industry_cover.gpkg".format(city),  driver="GPKG")
    
    # Getting extent of ghs pop raster
    data = gdal.Open(temp_tif_path + "/{0}_CLC_2012_2018.tif".format(city))
    wkt = data.GetProjection()
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None
    
    # Rasterizing industry_cover layer
    print("Rasterizing industry_cover layer")
    src_file = temp_shp_path +"/{0}_industry_cover.gpkg".format(city)
    dst_file = temp_tif_path +"/{0}_industry_cover.tif".format(city)
    cmd = '{0}/gdal_rasterize.exe -a industry_cover -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
        .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file)
    subprocess.call(cmd, shell=True)
    
    for file in os.listdir(temp_tif_path + "/corine/"):
        if file.endswith('.tif') and file.startswith('industry_{}_CLC_'.format(city)):
            name = file.split("_", 1)[1]
            print(name)
            #As the industry bodies of the Corine do not include details of Amsterdam, it gets combined with other layer --> percentages of industry cover 
            print("------------------------------ Splitting Corine rasters to categories:industry Bodies and Wetlands Combines with industry cover (percentages) produced in Postgres with (vectors) lakes, wetlands and sea  ------------------------------")
            cmds = """python {2}/gdal_calc.py -A "{0}/corine/industry_{1}" -B "{3}"  \
                --A_band=1 --B_band=1 --outfile="{0}/corine/indComb_{1}" \
                --calc="maximum(A*100, B)/100" """.format(temp_tif_path, name, python_scripts_folder_path, dst_file)
            subprocess.call(cmds, shell=True)


    