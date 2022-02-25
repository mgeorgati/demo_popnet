import geopandas as gpd
import sys
def createNetwork(ancillary_data_folder_path,cur,conn, engine, city, temp_shp_path): 
    #_______________________STREETS_________________________
    streetsPath = ancillary_data_folder_path + "/OSM/malopolskie-latest-free.shp/gis_osm_roads_free_1.shp"
    streets = gpd.read_file(streetsPath)
    streets = streets.to_crs('epsg:3035')
    bbox = gpd.read_file(temp_shp_path + "/{}_bbox.geojson".format(city))
    
    ndf = gpd.clip(streets, bbox)
    ndf.to_postgis('{0}_streets'.format(city), engine, if_exists="replace" )
    # Creating pgr topology and network with traveltime as cost for biking 
    # and walkingtime as cost for walking based on average speed and segment length 
    cur.execute("alter table {0}_streets ADD COLUMN source integer;\
                alter table {0}_streets ADD COLUMN target integer;".format(city))
    conn.commit() 

    print("Create Serial gid for streets")
    cur.execute("ALTER TABLE {0}_streets\
	            ADD COLUMN gid SERIAL PRIMARY KEY;".format(city))  # 4.3 sec
    conn.commit()

    cur.execute("select pgr_createTopology('{0}_streets', 0.0005, 'geometry', 'gid')".format(city))
    check = cur.fetchone()
    if check[0] == "FAIL":
        print("TOPOLOGY FAILED AND PROCESS STOPS".format(city))
        sys.exit()
    else:
        print("TOPOLOGY SUCCEDED".format(city))
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