
from basicFunctions import createFolder

def calcPrimarySchools(ancillary_data_folder_path,city,cur,conn,year, comp_year, BBRtype):
    # Creating necessary tables ----------------------------------------------------------------------------------------
    print("---------- Creating {} tables, if it doesn't exist ----------".format(city))
    print("Checking {0} {1} table".format(city, BBRtype))
    cur.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = 'bbr_{1}_{0}');".format(year, BBRtype))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} {1} table from case study extent".format(city,BBRtype))
        # table for train stations in case study:
        cur.execute("""CREATE TABLE bbr_{1}_{0} ("ESREjdNr" bigint, "BYG_ANVEND" bigint, geometry geometry(Point,3035));""".format(year, BBRtype))
        conn.commit()
    else:
        print("{0} bbr_{1}_{2} table already exists".format(city, BBRtype,year))

    print("-------------------- UPDATING TABLE WITH SCHOOLS FROM THE NEXT YEAR {0},{1}--------------------".format(year,comp_year))
    cur.execute("""INSERT INTO bbr_{2}_{0} (geometry, "ESREjdNr", "BYG_ANVEND" ) 
 	                SELECT DISTINCT ON (bbr_cph_{0}.geometry) bbr_cph_{0}.geometry, bbr_cph_{0}."ESREjdNr" , bbr_cph_{0}."BYG_ANVEND"
                    FROM bbr_cph_{0}, bbr_cph_{1}
                    WHERE bbr_cph_{1}."BYG_ANVEND" = 421 
                    AND bbr_cph_{0}."BYG_ANVEND" = 420
                    AND bbr_cph_{1}."ESREjdNr"= bbr_cph_{0}."ESREjdNr"
                    """.format(year, comp_year, BBRtype)) 
    conn.commit()

    print("-------------------- UPDATING TABLE WITH EXISTING PRIMARY SCHOOLS {}--------------------".format(year))
    cur.execute("""INSERT INTO bbr_{1}_{0} (geometry, "ESREjdNr","BYG_ANVEND" ) 
 	SELECT  DISTINCT ON (bbr_cph_{0}.geometry) bbr_cph_{0}.geometry, bbr_cph_{0}."ESREjdNr", bbr_cph_{0}."BYG_ANVEND" 
                    FROM bbr_cph_{0}
                    WHERE bbr_cph_{0}."BYG_ANVEND" = 421 """.format(year, BBRtype)) 
    conn.commit()

    print("-------------------- UPDATING TABLE WITH EXISTING PRIMARY SCHOOLS {}--------------------".format(year))
    cur.execute("""ALTER TABLE bbr_{1}_{0} ADD COLUMN gid SERIAL PRIMARY KEY;""".format(year, BBRtype))
    conn.commit()
 