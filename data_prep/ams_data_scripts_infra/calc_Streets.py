import os
import subprocess
import time
import geopandas as gpd
import psycopg2

def createNetwork(pgpath,pghost,pgport, pguser, pgpassword, pgdatabase,ancillary_data_folder_path,cur,conn, engine, city): 
    #_______________________STREETS_________________________
    streetsPath = ancillary_data_folder_path + "/roads/streets.geojson"
    streets = gpd.read_file(streetsPath)
    streets  = streets.to_crs('epsg:3035')
    # Create Table for Railway
    print("---------- Creating table for city, if it doesn't exist ----------")
    print("Checking {0} Case Study table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_streetsKatiAllo');".format(city))
    check = cur.fetchone()
    if check[0] == True:
        print("{0} streets table already exists".format(city))
        cur.execute("DROP TABLE IF EXISTS {0}_streets;".format(city))
        conn.commit()
    else:
        print("Creating {0} streets ".format(city))
        streets.to_postgis('{0}_streets'.format(city),engine)
        
    """# Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating street table, if it doesn't exist ----------")
    print("Checking {0} streets table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_streets');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} streets table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_streets as \
                        SELECT streets.WVK_ID, ST_Force2D(ST_Transform(streets.geometry, 3035)) as geom from streets, {0}_cs \
                        WHERE (ST_Intersects(ST_Transform(streets.geometry, 3035), {0}_bbox.geom)) ;".format(city))
        conn.commit()
    else:
        print("{0} streets table already exists".format(city))
    """
    # Creating pgr topology and network with traveltime as cost for biking 
    # and walkingtime as cost for walking based on average speed and segment length 
    cur.execute("alter table {0}_streets ADD COLUMN source integer;\
                alter table {0}_streets ADD COLUMN target integer; ".format(city))
    conn.commit() 

    cur.execute("select pgr_createTopology('{0}_streets', 0.0005, 'geometry', 'gid')".format(city))
    conn.commit()
    
    cur.execute("create or replace view nodes as\
                    select id, st_centroid(st_collect(pt)) as geom\
                    from (\
                        (select source as id, st_startpoint(geometry) as pt\
                        from  {0}_streets\
                        ) \
                    union\
                        (select target as id, st_endpoint(geometry) as pt\
                        from  {0}_streets\
                        ) \
                    ) as foo\
                    group by id; ".format(city))
    conn.commit()
    
    cur.execute("ALTER TABLE  {0}_streets ADD COLUMN length_m integer; \
                    UPDATE  {0}_streets SET length_m = st_length(st_transform(geometry,3035));".format(city))
    conn.commit()
  
    cur.execute("ALTER TABLE  {0}_streets ADD COLUMN traveltime double precision;\
                    UPDATE  {0}_streets SET traveltime = length_m/15000.0*60;".format(city))  # average is 15 km/h
    conn.commit()

    cur.execute("ALTER TABLE {0}_streets ADD COLUMN walkingtime double precision;\
                    UPDATE {0}_streets SET walkingtime = length_m/5000.0*60;".format(city))  # average walking speed is 5 km/h
    conn.commit()
     
    