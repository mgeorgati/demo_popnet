import os
import subprocess
import time
import psycopg2

def notRelevant(bikelanes):
    # Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating bikelanes tables, if it doesn't exist ----------")
    print("Checking {0} bikelanes table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_bikelanes');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} bikelanes table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_bikelanes as \
                        SELECT streets.gid, streets.vejklasse, ST_Force2D(ST_Transform(streets.geom, 3035)) as geom, streets.timeof_cre from streets, {0}_cs \
                        WHERE (ST_Intersects(ST_Transform(streets.geom, 3035), {0}_cs.geom) AND vejklasse= 'Cykelbane langs vej')\
                             OR (ST_Intersects(ST_Transform(streets.geom, 3035), {0}_cs.geom) AND vejklasse= 'Cykelsti langs vej') ;".format(city))
        conn.commit()
    else:
        print("{0} bikelanes table already exists".format(city))

#_______________________Street Network_________________________
def importStreets(pgpath,pghost,pgport, pguser, pgpassword, pgdatabase,ancillary_data_folder_path,cur,conn,city):
    # Setting environment for psql
    os.environ['PATH'] = pgpath
    os.environ['PGHOST'] = pghost
    os.environ['PGPORT'] = pgport
    os.environ['PGUSER'] = pguser
    os.environ['PGPASSWORD'] = pgpassword
    os.environ['PGDATABASE'] = pgdatabase

def createNetwork(pgpath,pghost,pgport, pguser, pgpassword, pgdatabase,ancillary_data_folder_path,cur,conn,city): 
    # Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating street table, if it doesn't exist ----------")
    print("Checking {0} streets table".format(city))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_streets');".format(city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} streets table from case study extent".format(city))
        # table for train stations in case study:
        cur.execute("create table {0}_streets as \
                        SELECT streets.gid, streets.vejklasse, ST_Force2D(ST_Transform(streets.geom, 3035)) as geom, streets.timeof_cre from streets, {0}_cs \
                        WHERE (ST_Intersects(ST_Transform(streets.geom, 3035), {0}_cs.geom)) ;".format(city))
        conn.commit()
    else:
        print("{0} streets table already exists".format(city))

    # Creating pgr topology and network with traveltime as cost for biking 
    # and walkingtime as cost for walking based on average speed and segment length 
    cur.execute("alter table {0}_streets ADD COLUMN source integer;\
                alter table {0}_streets ADD COLUMN target integer; ".format(city))
    conn.commit()

    cur.execute("select pgr_createTopology('{}_streets', 0.0005, 'geom', 'gid')".format(city))
    conn.commit()

    cur.execute("create or replace view nodes as\
                    select id, st_centroid(st_collect(pt)) as geom\
                    from (\
                        (select source as id, st_startpoint(geom) as pt\
                        from  {0}_streets\
                        ) \
                    union\
                        (select target as id, st_endpoint(geom) as pt\
                        from  {0}_streets\
                        ) \
                    ) as foo\
                    group by id; ".format(city))
    conn.commit()

    cur.execute("ALTER TABLE  {0}_streets ADD COLUMN length_m integer; \
                    UPDATE  {0}_streets SET length_m = st_length(st_transform(geom,3035));".format(city))
    conn.commit()
  
    cur.execute("ALTER TABLE  {0}_streets ADD COLUMN traveltime double precision;\
                    UPDATE  {0}_streets SET traveltime = length_m/15000.0*60;".format(city))  # average is 15 km/h
    conn.commit()

    cur.execute("ALTER TABLE {0}_streets ADD COLUMN walkingtime double precision;\
                    UPDATE {0}_streets SET walkingtime = length_m/5000.0*60;".format(city))  # average walking speed is 5 km/h
    conn.commit()

