import os
import subprocess
import time
import geopandas as gpd
from basicFunctions import createFolder

# 120: Detached single-family house (detached house).
# 121: Attached single-family house.
# 122: Detached single-family house in dense-low-rise area.
# 130: Townhouse, chain, or semi-detached house (vertical separation between the units).
# 131: Row and cluster housing.
# 132: Semi-detached house (double house). 
# 140: Multi-storey residential building (multi-family house, including two-family house (horizontal separation between the units).

def clipSelectHousing(gdal_path, bbr_folder_path, ancillary_data_folder_path, year, city, BBRtype):
    csPath =  os.path.dirname(ancillary_data_folder_path) + "/temp_shp/{0}_bbox.shp".format(city)
    cs = gpd.read_file(csPath).to_crs("epsg:25832")
    xmin, ymin, xmax, ymax = cs.geometry.total_bounds
    out_path = bbr_folder_path + "/{0}_bbr/{1}".format(city, BBRtype)
    createFolder(out_path)
    cmd_tif_merge = '{0}/ogr2ogr.exe -spat {1} {2} {3} {4} -where " ("OVERDRAGEL" = 1 OR "OVERDRAGEL" = 3)  AND ("BYG_ANVEND"  =  140 or \
                    "BYG_ANVEND"  =  120 or "BYG_ANVEND"  =  121 or  "BYG_ANVEND"  =  122 or  \
                    "BYG_ANVEND"  =  130 or  "BYG_ANVEND"  =  131 or  "BYG_ANVEND"  =  132) " -s_srs \
                    EPSG:25832 -t_srs EPSG:3035 -f GPKG {7}/{6}_bbr_{8}.gpkg \
                    {5}/rawData/bbr_{6}.gpkg'.format(gdal_path, xmin, ymin, xmax, ymax, bbr_folder_path, year, out_path, BBRtype)
    #print(cmd_tif_merge)
    subprocess.call(cmd_tif_merge, shell=False)

def importToDBHousing(bbr_folder_path, city, conn, cur,  engine, year,  BBRtype):
    # Loading shapefiles into postgresql and creating necessary 
    #_______________________Housing_________________________
    print("Importing files to postgres")
    path = bbr_folder_path + "/{0}_bbr/{2}/{1}_bbr_{2}.gpkg".format(city, year,  BBRtype)
    src_file = gpd.read_file(path)
    
    print(src_file .head(2))
    # Create Table for Country Case Study
    print("---------- Creating table for {1} {0}, if it doesn't exist ----------".format(year, BBRtype))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_bbr_{1}');".format(year,  BBRtype))
    check = cur.fetchone()
    if check[0] == True:
        print("{0} {1} table already exists".format(year, BBRtype))

    else:
        print("Creating {0} housing table".format(year))
        src_file.to_postgis('bbr_{1}_{0}'.format(year, BBRtype),con =engine)

def calculateMeanPriceHousing(ancillary_data_folder_path, city, conn, cur, year, BBRtype):
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
                            FROM {0}_iteration_grid, bbr_{3}_{2} \
                            WHERE ST_Intersects({0}_iteration_grid.geom, bbr_{3}_{2}.geometry) \
                            AND bbr_{3}_{2}."KONTANT_KO" is NOT null \
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
            cur.execute("""WITH a AS (select chunk_nr{1}.id, avg("KONTANT_KO") AS prices, avg("BEBO_ARL"), \
                CASE 
                    WHEN avg("BEBO_ARL")>0 THEN avg("BEBO_ARL")
                ELSE 1
                    END area \
                FROM bbr_{3}_{2}, chunk_nr{1} \
            WHERE bbr_{3}_{2}."KONTANT_KO" IS NOT NULL \
                AND ST_Intersects(chunk_nr{1}.geom, bbr_{3}_{2}.geometry) \
                GROUP BY chunk_nr{1}.id) \
            UPDATE {0}_cover_analysis \
                SET "{2}_{3}" = CAST(ROUND(CAST(FLOAT8 (prices/area) AS NUMERIC),2 ) AS FLOAT) \
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