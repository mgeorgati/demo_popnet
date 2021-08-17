import os
import subprocess
import time
import geopandas as gpd
from basicFunctions import createFolder

# Building for teaching and research (school, high school, research laboratory, etc.) + Building for day care.
def clipSelectScools(gdal_path, bbr_folder_path, ancillary_data_folder_path, year, city):
    csPath =  os.path.dirname(ancillary_data_folder_path) + "/temp_shp/{0}_bbox.shp".format(city)
    cs = gpd.read_file(csPath).to_crs("epsg:25832")
    xmin, ymin, xmax, ymax = cs.geometry.total_bounds
    out_path = bbr_folder_path + "/{}_bbr1/schools".format(city)
    createFolder( out_path)
    cmd_tif_merge = '{0}/ogr2ogr.exe -spat {1} {2} {3} {4} -where "BYG_ANVEND = 420 or BYG_ANVEND = 421 \
                    or BYG_ANVEND = 440 or BYG_ANVEND = 441" -s_srs \
                    EPSG:25832 -t_srs EPSG:3035 -f GPKG {7}/{6}_bbr_schools.gpkg \
                    {5}/rawData/bbr_{6}.gpkg'.format(gdal_path, xmin, ymin, xmax, ymax, bbr_folder_path, year, out_path)
    print(cmd_tif_merge)
    subprocess.call(cmd_tif_merge, shell=False)

def importToDBSchools(ancillary_data_folder_path, city, cur, engine, year):

    # Loading shapefiles into postgresql and creating necessary 
    #_______________________SCHOOLS_________________________
    print("Importing files to postgres")
    school_path = os.path.dirname(ancillary_data_folder_path) + "/bbr/{0}_bbr/schools/{1}_bbr_schools.gpkg".format(city, year)
    school_file = gpd.read_file(school_path)
    school_file = school_file.drop_duplicates(subset=['ESREjdNr'], keep='last')
    school_file['gid'] = school_file.index
    print(school_file.head(2))
    # Create Table for Country Case Study
    print("---------- Creating table for schools {}, if it doesn't exist ----------".format(year))
    print("Checking {0} Case Study table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_bbr_schools');".format(year))
    check = cur.fetchone()
    if check[0] == True:
        print("{0} Schools table already exists".format(year))

    else:
        print("Creating {0} Schools table".format(year))
        school_file.to_postgis('bbr_schools_{}'.format(year),con =engine)

def computeSchoolsIsochrones(ancillary_data_folder_path, city, cur, conn, year):
    # getting id numbers for schoolss covering the city ---------------------------------------
    schools_ids = []
    closestPoint_ids=[]
    cur.execute("SELECT gid FROM bbr_schools_{};".format(year))
    train_id = cur.fetchall()
    for id in train_id:
        schools_ids.append(id[0])
    print(schools_ids)
    
    for point in schools_ids:
        cur.execute("SELECT {0}_streets_vertices_pgr.id as start\
                        FROM\
                        {0}_streets_vertices_pgr,\
                        bbr_schools_{2}\
                        WHERE bbr_schools_{2}.gid = {1}\
                        ORDER BY ST_Distance({0}_streets_vertices_pgr.the_geom, bbr_schools_{2}.geometry) ASC\
                        LIMIT 1 ;".format(city,point, year))
        closestPoint_id = cur.fetchall()
    
        for gid in closestPoint_id:
            closestPoint_ids.append(gid[0])
    
    print(closestPoint_ids)
    
    # Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating isochrones tables, if it doesn't exist ----------")
    print("Checking {0} isochrones table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_isochrones_Schools_{1}');".format(city,year))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} isochrones_Schools table from case study extent".format(city))
        # table for schoolss in case study:
        cur.execute("create table {0}_isochrones_Schools_{1} (id int, geom geometry);".format(city,year))
        conn.commit()
    else:
        print("{0} isochrones_Schools table already exists".format(city))

    # saving ids to list
    for cl_id in closestPoint_ids:
        # Processing queries / running the cover analysis-----------------------------------------------------------------------------------------------
        print("-------------------- CREATING IDS FOR STARTING POINTS FOR ISOCHRONES (SCHOOLS) --------------------")
        cur.execute("insert into {0}_isochrones_Schools_{1} (id) values ({2})".format(city, year, cl_id)) # average is 15 km/h
        conn.commit()

        # Processing queries / running the cover analysis-----------------------------------------------------------------------------------------------
        print("-------------------- CREATING ISOCHRONES FOR {0} SCHOOL --------------------".format(cl_id))
        cur.execute("update {0}_isochrones_Schools_{2} SET \
                        geom = (Select ST_ConcaveHull(ST_Collect(geom),0.9,false) \
                        FROM {0}_streets   \
                        JOIN (SELECT edge FROM pgr_drivingdistance('SELECT gid as id, source, target, traveltime AS cost from {0}_streets', {1}, 15, false)) \
                        AS route \
                        ON {0}_streets.gid = route.edge) \
                        where id ={1}".format(city, cl_id, year)) # average is 15 km/h and travel time is 15'
        conn.commit()

def calculateSchoolCount(ancillary_data_folder_path, city, conn, cur, year):
   
    print("Checking {0} cover analysis - schools column".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 \
                                FROM information_schema.columns \
                                WHERE table_schema='public' AND table_name='{0}_cover_analysis' \
                                AND column_name='{1}_schoolscount');".format(city,year))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis - schools column".format(city))
        # Adding schoolss column to country cover analysis table
        cur.execute("""Alter table {0}_cover_analysis ADD column "{1}_schoolscount" int default 0;""".format(city,year))
        conn.commit()
    else:
        print("""{0} cover analysis - train "{1}_schoolscount" column already exists""".format(city,year))

    # Calculating schoolss based on count ----------------------------------------------------------------------------------------
    print("---------- Calculating schoolss ----------")
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

            # Counting number of schoolss 
            cur.execute("""with a as (select chunk_nr{1}.id, count(*) from {0}_isochrones_Schools_{2}, chunk_nr{1} \
            where ST_Intersects(chunk_nr{1}.geom, {0}_isochrones_Schools_{2}.geom) \
            group by chunk_nr{1}.id) \
            update {0}_cover_analysis set "{2}_schoolscount" = a.count from a where a.id = {0}_cover_analysis.id;""".format(city, chunk, year))  # 4.1 sec
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



    
        
