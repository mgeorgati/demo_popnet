"""
## ## ## ## ## ----- UPDATE HOUSING PRICES  ----- ## ## ## ## ##
def updatePricesHousing(bbr_folder_path, city, conn, cur, engine, year):
    print("---------- Creating table for housing {}, if it doesn't exist ----------".format(year))
    prev_year = year - 1 
    path00 = bbr_folder_path + "/{0}_bbr/housing/{1}_bbr_housing.gpkg".format(city, prev_year)
    cond = pathlib.Path(path00)
    if cond.exists():
        print("File is being updated!")
        cur.execute("update bbr_housing_{0} SET "KONTANT_KO" = bbr_housing_{1}."KONTANT_KO" FROM bbr_housing_{1} \
                    WHERE\
                    bbr_housing_{0}."KONTANT_KO" is null AND bbr_housing_{1}."KONTANT_KO" is NOT null \
                    AND bbr_housing_{0}.etrs89koor = bbr_housing_{1}.etrs89koor\
                    AND bbr_housing_{0}.etrs89ko_1 = bbr_housing_{1}.etrs89ko_1\
                    AND bbr_housing_{0}."Etagebeteg" = bbr_housing_{1}."Etagebeteg"\
                    AND bbr_housing_{0}."SIDE_DOERN" = bbr_housing_{1}."SIDE_DOERN";".format(year, prev_year))
        conn.commit()

        # Create SQL Query
        sql = "SELECT * FROM bbr_housing_{0}".format(year)
        # Read the data with Geopandas
        gdf = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col='geometry' )
        print(gdf.head(4))
        housing_pathUpdated = bbr_folder_path + "/{}_bbr/housingUpdated".format(city)
        createFolder(housing_pathUpdated)

        # exporting water cover from postgres
        #print("Exporting {0} in {1} from postgres".format(BBRrasterizeType,year))        
        gdf.to_file(housing_pathUpdated + "/{0}_housingUpdated.gpkg".format(year),  driver="GPKG")

    else: 
        print("File is not updated!")
"""