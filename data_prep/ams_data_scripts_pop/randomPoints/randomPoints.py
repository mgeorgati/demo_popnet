import os
import geopandas as gpd

import sys
base_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(base_path)
sys.path.append(base_path)
from variables import ancillary_POPdata_folder_path, ancillary_data_folder_path, city, engine, cur, conn
from csv_to_raster import createFolder
year=2018

def importToDB_BBR(src_file, city, conn, cur,  engine, year):
    # Loading shapefiles into postgresql and creating necessary 
    #_______________________Housing_________________________
    print("Importing files to postgres") 
    gdf = gpd.read_file(src_file)
    #gdf = gdf.to_crs("EPSG:3035")
    print(gdf.crs)
    selectList=["grid_id","geometry"]
    for col in gdf.columns:
        if col.startswith("Z0_"):
            selectList.append(col)
    df_select = [x for x in gdf if x in selectList]
    ndf = gdf.loc[:, df_select]
    print(ndf.head(3))
    print(ndf.crs)
    ndf.to_postgis('ams_z0_{}'.format(year), con =engine)

    #cur.execute("""Alter table ams_z1_2018 ADD column "{1}_{2}" int default 0;""".format(city,year, BBRtype))
    #conn.commit()

src_file = ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridDivs.geojson".format(year)
#importToDB_BBR(src_file, city, conn, cur,  engine, year)
def restructureTableSQL(ancillary_POPdata_folder_path):

    gdf = gpd.read_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridDivs.geojson".format(year))
     
    sql1="""CREATE TABLE ams_z0_new (grid_id bigint, origin varchar, pop integer, geometry geometry(MultiPolygon,3035));"""   
    cur.execute(sql1)
    conn.commit()
    count = cur.rowcount
    print (count, "Table successfully created")
    
    for col in gdf.columns:
        if col.startswith("Z0_"):

        # using psycopg2
            sql3="""INSERT INTO ams_z0_new (grid_id, pop, geometry) SELECT grid_id,"{0}",geometry FROM ams_z0_{1} WHERE "{0}"!=0;""".format(col,2018) #{}
            sql4=""" UPDATE ams_z0_new SET origin='{0}' where origin IS NULL;""".format(col) #{}
            print(sql3, sql4)
            cur.execute(sql3)
            cur.execute(sql4)

        conn.commit()
        count = cur.rowcount
        print (count, "Record inserted successfully into table")
    
    sql = """CREATE TABLE ams_z0_random AS
        SELECT ams_z0_new.grid_id as grid_id, ams_z0_new.origin as origin, ams_z0_new.pop as pop, ST_GeneratePoints(ams_z0_new.geometry, ams_z0_new.pop) as geom
            FROM ams_z0_new"""
    cur.execute(sql)
    conn.commit()
    count = cur.rowcount
    print (count, "Done")


restructureTableSQL(ancillary_POPdata_folder_path)