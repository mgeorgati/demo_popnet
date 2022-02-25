import geopandas as gpd
import os

def joinGridToGridIT(ancillary_POPdata_folder_path ,ancillary_EUROdata_folder_path, country, deliver_path, cur, conn, engine, year_list):
    gridL = gpd.read_file(ancillary_EUROdata_folder_path + "/euroGrid/grid_1km_{}.gpkg".format(country))
    # Create Table for population
    print("---------- Creating table for city, if it doesn't exist ----------")
    print("Checking {0} Pop table".format(country))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'grid_1km_{}');".format(country))
    check = cur.fetchone()
    if check[0] == True:
        print("{0}_dataVectorGrid already exists".format(country))

    else:
        print("Creating {0} pop table ".format(country))
        gridL.to_postgis('grid_1km_{}'.format(country),engine)
    
    for year in year_list:
        df = gpd.read_file('C:/FUME/PopNetV2/data_prep/rom_ProjectData/PopData/CensusTractsMunicipality/{}_komCensusTracts.geojson'.format(year))
        df = df.rename(columns={'Census tracts_new':'CT_CODE', 'Total population ':'totalpop', 'Foreigners':'immigrants', 'Italians':'ita', 'EU':'eu_immigrants', 'Europe (non EU)':'EurNotEU', 
                                    'Italians - 0-5':'ita0-5', 'Italians - 6-19':'ita6-19', 'Italians - 20-29':'ita20-29', 'Italians - 30-44':'ita30-44', 'Italians - 45-64':'ita45-64', 'Italians - 65-79':'ita65-79', 'Italians – 80+':'ita80+', 
                                    'Foreigners - 0-5':'mig0-5', 'Foreigners - 6-19':'mig6-19', 'Foreigners - 20-29':'mig20-29', 'Foreigners - 30-44':'mig30-44', 'Foreigners - 45-64':'mig45-64', 'Foreigners - 65-79':'mig65-79', 'Foreigners - 80+':'mig80+'})
        df['CT_CODE'] = df['CT_CODE'].astype('str')
        df['noneu_immigrants'] = df['immigrants'] - df['eu_immigrants']
        df['children'] = df['ita0-5'] + df['ita6-19'] + df['mig0-5'] + df['mig6-19']
        df['students'] = df['ita20-29'] + df['mig20-29'] 
        df['mobile_adults']= df['ita30-44'] + df['mig30-44'] 
        df['not_mobile_adults']= df['ita45-64'] + df['mig45-64'] 
        df['elderly']= df['ita65-79'] + df['ita80+'] + df['mig65-79'] + df['mig80+']
        df.dropna(subset=['geometry'], inplace=True)
        
        print(df.head(2), df.columns.to_list())
        # Create Table for neighborhoods
        print("---------- Creating table for city, if it doesn't exist ----------")
        print("Checking {0} Pop table".format(year))
        cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{}_komCensusTracts');".format(year))
        check = cur.fetchone()
        if check[0] == True:
            print("{}_komCensusTracts already exists".format(year))
        else:
            print("Creating {0} pop table ".format(year))
            df.to_postgis('{}_komCensusTracts'.format(year),engine)
        NList = [ 'CT_CODE',"Census tracts (sezioni di censimento)" , "COD_REG" , "COD_ISTAT",  "PRO_COM" , "SEZ" , "Shape_Leng" , "Shape_Area" ,'geometry']
        fields= df.columns.to_list()
        
        cur.execute("""UPDATE "{}_komCensusTracts" SET geometry = ST_MakeValid(geometry)""".format(year))
        conn.commit()
        
        for i in fields:
            if i not in NList :
                cur.execute("""ALTER TABLE "grid_1km_{0}" ADD COLUMN "{2}_{1}_1km" double precision;""".format(country, i, year))
                conn.commit()
                #cur.execute("""ALTER TABLE "grid_1km_{}" ALTER COLUMN "{2}_{1}_1km" SET DEFAULT 0.0;""".format(country, i, year))
                ids = []
                cur.execute("""SELECT "GRD_ID" FROM "grid_1km_{}";""".format(country))
                chunk_id = cur.fetchall()
                
                # saving ids to list
                for id in chunk_id:
                    ids.append(id[0])
                
                # iterate through chunks
                for chunk in ids:    
                    cur.execute( """ WITH b as (
                        WITH a as(
                            Select "grid_1km_{3}"."GRD_ID" as code,"{2}_komCensusTracts".totalpop as stud, "{2}_komCensusTracts"."Shape_Area" as shapearea,
                            "{2}_komCensusTracts".geometry as geom, "{2}_komCensusTracts"."CT_CODE" as id, 
                            ST_AREA( ST_Intersection("grid_1km_{3}".geometry,  "{2}_komCensusTracts".geometry) ) as area 
                            from "grid_1km_{3}",  "{2}_komCensusTracts"
                            WHERE "grid_1km_{3}"."GRD_ID"= '{0}' 
                            AND  ST_Intersects( "grid_1km_{3}".geometry,  "{2}_komCensusTracts".geometry) )
                        Select SUM(stud*area/shapearea) as pop from a)
                    UPDATE "grid_1km_{3}" SET "{2}_{1}_1km" = pop from b where "grid_1km_{3}"."GRD_ID"='{0}';
                    """.format(chunk, i, year, country))
                    conn.commit()
    
        query = """Select * FROM  "grid_1km_{0}" """.format(country)
    
        inter = gpd.read_postgis(query, engine, geom_col='geometry')
        selection =[]
        for col in inter.columns:
            if col.startswith('{}_'.format(year)):
                print(col)
                
                name = col.split('{}_'.format(year))[1]
                print(name)
                selection.append(name)
                inter = inter.rename(columns={'{}'.format(col): '{}'.format(name)}, )
        extra= ['geometry', 'GRD_ID']
        selection.extend(extra)
        nf = inter[selection]
        
        popMig = nf[['GRD_ID','totalpop_1km','ita_1km', 'immigrants_1km', 'eu_immigrants_1km', 'noneu_immigrants_1km', 'geometry']]
        popMig.to_csv(deliver_path + "/{1}/Population/{0}_MigrationStatus.csv".format(year,country), sep=';')
        popMig.to_file(deliver_path + "/{1}/Population/{0}_MigrationStatus.gpkg".format(year,country),driver='GPKG',crs="EPSG:3035")
        
        popAge = nf[['GRD_ID','totalpop_1km','children_1km', 'students_1km', 'mobile_adults_1km', 'not_mobile_adults_1km', 'elderly_1km', 
                    'ita0-5_1km', 'ita6-19_1km', 'ita20-29_1km', 'ita30-44_1km', 'ita45-64_1km', 'ita65-79_1km', 'ita80+_1km', 
                    'mig0-5_1km', 'mig6-19_1km', 'mig20-29_1km', 'mig30-44_1km', 'mig45-64_1km', 'mig65-79_1km', 'mig80+_1km',
                    'geometry']]
        popAge.to_csv(deliver_path + "/{1}/Population/{0}_DemographicFeatures.csv".format(year,country), sep=';')
        popAge.to_file(deliver_path + "/{1}/Population/{0}_DemographicFeatures.gpkg".format(year,country),driver='GPKG',crs="EPSG:3035")
        
def movements_processIT(ancillary_POPdata_folder_path ,ancillary_EUROdata_folder_path, country, deliver_path, cur, conn, engine, year_list):
    gridL = gpd.read_file(ancillary_EUROdata_folder_path + "/euroGrid/grid_1km_{}.gpkg".format(country))
    # Create Table for population
    print("---------- Creating table for city, if it doesn't exist ----------")
    print("Checking {0} Pop table".format(country))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'grid_1km_{}');".format(country))
    check = cur.fetchone()
    if check[0] == True:
        print("{0}_dataVectorGrid already exists".format(country))

    else:
        print("Creating {0} pop table ".format(country))
        gridL.to_postgis('grid_1km_{}'.format(country),engine)
    
    for file in os.listdir(ancillary_POPdata_folder_path + "/urbanzones/"):
        print(file)
        name = file.replace(' ','').split('_')[0]
        print(name)
        df = gpd.read_file(ancillary_POPdata_folder_path + '/urbanzones/{}'.format(file))
        df = df.rename(columns={ "ZURB code":'ZURB_CODE', "ZURB code2":'ZURB_CODE2' ,'2015':'2015_{}'.format(name), '2016':'2016_{}'.format(name), '2017':'2017_{}'.format(name), '2018':'2018_{}'.format(name)})
        
        df.dropna(subset=['geometry'], inplace=True)
        
        print(df.head(2), df.columns.to_list())
        # Create Table for neighborhoods
        print("---------- Creating table for city, if it doesn't exist ----------")
        print("Checking {0} Pop table".format(name))
        cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{}');".format(name))
        check = cur.fetchone()
        if check[0] == True:
            print("{} already exists".format(name))
        else:
            print("Creating {0} pop table ".format(name))
            df.to_postgis('{}'.format(name),engine)
        NList = [ '2015_{}'.format(name), '2016_{}'.format(name), '2017_{}'.format(name), '2018_{}'.format(name)]
        fields= df.columns.to_list()
        
        cur.execute("""UPDATE "{}" SET geometry = ST_MakeValid(geometry)""".format(name))
        conn.commit()
        
        for i in NList :
            cur.execute("""ALTER TABLE "grid_1km_{0}" ADD COLUMN "{1}_1km" double precision;""".format(country, i))
            conn.commit()
            ids = []
            cur.execute("""SELECT "GRD_ID" FROM "grid_1km_{}";""".format(country))
            chunk_id = cur.fetchall()
            
            # saving ids to list
            for id in chunk_id:
                ids.append(id[0])
            
            # iterate through chunks
            for chunk in ids:    
                cur.execute( """ WITH b as (
                    WITH a as(
                        Select "grid_1km_{3}"."GRD_ID" as code,"{2}"."{1}" as stud, "{2}"."SHAPE_Area" as shapearea,
                        "{2}".geometry as geom, "{2}"."ZURB_CODE" as id, 
                        ST_AREA( ST_Intersection("grid_1km_{3}".geometry,  "{2}".geometry) ) as area 
                        from "grid_1km_{3}",  "{2}"
                        WHERE "grid_1km_{3}"."GRD_ID"= '{0}' 
                        AND  ST_Intersects( "grid_1km_{3}".geometry,  "{2}".geometry) )
                    Select SUM(stud*area/shapearea) as pop from a)
                UPDATE "grid_1km_{3}" SET "{1}_1km" = pop from b where "grid_1km_{3}"."GRD_ID"='{0}';
                """.format(chunk, i, name, country))
                conn.commit()

def births_processIT(ancillary_POPdata_folder_path ,ancillary_EUROdata_folder_path, country, deliver_path, cur, conn, engine, year_list):
    gridL = gpd.read_file(ancillary_EUROdata_folder_path + "/euroGrid/grid_1km_{}.gpkg".format(country))
    # Create Table for population
    print("---------- Creating table for city, if it doesn't exist ----------")
    print("Checking {0} Pop table".format(country))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'grid_1km_{}');".format(country))
    check = cur.fetchone()
    if check[0] == True:
        print("{0}_dataVectorGrid already exists".format(country))

    else:
        print("Creating {0} pop table ".format(country))
        gridL.to_postgis('grid_1km_{}'.format(country),engine)
    

    df = gpd.read_excel(ancillary_POPdata_folder_path + '/Rome - Births, deaths, marriages and migrations.xlsx'.format(file))
    df = df.rename(columns={ "ZURB code":'ZURB_CODE', "ZURB code2":'ZURB_CODE2' ,'2015':'2015_{}'.format(name), '2016':'2016_{}'.format(name), '2017':'2017_{}'.format(name), '2018':'2018_{}'.format(name)})
    
    df.dropna(subset=['geometry'], inplace=True)
    
    print(df.head(2), df.columns.to_list())
    # Create Table for neighborhoods
    print("---------- Creating table for city, if it doesn't exist ----------")
    print("Checking {0} Pop table".format(name))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{}');".format(name))
    check = cur.fetchone()
    if check[0] == True:
        print("{} already exists".format(name))
    else:
        print("Creating {0} pop table ".format(name))
        df.to_postgis('{}'.format(name),engine)
    NList = [ '2015_{}'.format(name), '2016_{}'.format(name), '2017_{}'.format(name), '2018_{}'.format(name)]
    fields= df.columns.to_list()
    
    cur.execute("""UPDATE "{}" SET geometry = ST_MakeValid(geometry)""".format(name))
    conn.commit()
    
    for i in NList :
        cur.execute("""ALTER TABLE "grid_1km_{0}" ADD COLUMN "{1}_1km" double precision;""".format(country, i))
        conn.commit()
        ids = []
        cur.execute("""SELECT "GRD_ID" FROM "grid_1km_{}";""".format(country))
        chunk_id = cur.fetchall()
        
        # saving ids to list
        for id in chunk_id:
            ids.append(id[0])
        
        # iterate through chunks
        for chunk in ids:    
            cur.execute( """ WITH b as (
                WITH a as(
                    Select "grid_1km_{3}"."GRD_ID" as code,"{2}"."{1}" as stud, "{2}"."SHAPE_Area" as shapearea,
                    "{2}".geometry as geom, "{2}"."ZURB_CODE" as id, 
                    ST_AREA( ST_Intersection("grid_1km_{3}".geometry,  "{2}".geometry) ) as area 
                    from "grid_1km_{3}",  "{2}"
                    WHERE "grid_1km_{3}"."GRD_ID"= '{0}' 
                    AND  ST_Intersects( "grid_1km_{3}".geometry,  "{2}".geometry) )
                Select SUM(stud*area/shapearea) as pop from a)
            UPDATE "grid_1km_{3}" SET "{1}_1km" = pop from b where "grid_1km_{3}"."GRD_ID"='{0}';
            """.format(chunk, i, name, country))
            conn.commit()
 