# Imports
import subprocess
import os
import gdal
import ogr
import osr
import psycopg2
import time
from basicFunctions import initPostgis,initPgRouting, clipToExtent, createFolder, psqltoshp, shptoraster
from calc_Schools import clipSelectScools,importToDBSchools, computeSchoolsIsochrones, calculateSchoolCount

#from DBtoRaster import psqltoshp, shptoraster

def process_data(engine, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, cur, conn, city, 
                    python_scripts_folder_path, gdal_rasterize_path,
                    ancillary_data_folder_path, ancillary_EUROdata_folder_path, temp_shp_path, temp_tif_path,  bbr_folder_path,
                    initExtensionPostGIS, initExtensionPGRouting, initClipBBR,
                    process_schools, clipSchools, importToDBSchools, calcIsoSchools, calcCountIsoSchools,
                    BBRpsqltoshp, BBRrasterize , BBRtype ):
                    
    #Start total preparation time timer
    start_total_algorithm_timer = time.time()
    
    createFolder(temp_shp_path)
    createFolder(temp_tif_path)
    
    # Check Extension in Database--------------------------------------------------------------------------------------
    if initExtensionPostGIS == "yes":
        print("------------------------------ CREATING NECESSARY EXTENSIONS PostGIS------------------------------")
        initPostgis(pghost, pgport, pguser, pgpassword, pgdatabase, cur, conn,city)
    
    if initExtensionPGRouting == "yes":
        print("------------------------------ CREATING NECESSARY EXTENSIONS PGRouting------------------------------")
        initPgRouting(pghost, pgport, pguser, pgpassword, pgdatabase, cur, conn)
    
    # Process BBR data --------------------------------------------------------------------------------------
    ## ## ## ## ## ----- GET IN A LOOP  ----- ## ## ## ## ##
    years_list = [2002,2004,2006,2008,2010,2012,2014,2016,2018] #2002,2004,2006,2008,2010,2012,2014,2016,2018,2020
    for year in years_list:
        if initClipBBR == "yes":
            print("------------------------------ CLIPPING BBR DATA TO bbox EXTENT------------------------------")
            clipToExtent(gdal_rasterize_path, bbr_folder_path, year, city)

        ## ## ## ## ## ----- SCHOOLS  ----- ## ## ## ## ##
        if process_schools == "yes":
            print("------------------------------ BBR SCHOOLS ------------------------------")
            if clipSchools == "yes":
                clipSelectScools(gdal_rasterize_path, bbr_folder_path, ancillary_data_folder_path, year, city)
            if importToDBSchools == "yes":
                importToDBSchools(ancillary_data_folder_path, city, cur, engine, year)
            if calcIsoSchools == "yes":
                computeSchoolsIsochrones(ancillary_data_folder_path, city, cur, conn, year)
            if calcCountIsoSchools == "yes":
                calculateSchoolCount(ancillary_data_folder_path, city, conn, cur, year)
        
        if BBRpsqltoshp == "yes" and BBRtype == "schools": 
            BBRrasterizeType = "schools"
            psqltoshp(city, engine, temp_shp_path, BBRrasterizeType, year)

        if BBRrasterize == "yes" and BBRtype == "schools": 
            BBRrasterizeType = "schools"
            shptoraster(city, gdal_rasterize_path, 100, 100, temp_shp_path, temp_tif_path, year, BBRrasterizeType)

    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))

