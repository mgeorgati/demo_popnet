# Imports
import subprocess
import os
import gdal
import ogr
import osr
import psycopg2
import time

from basicFunctions import initPostgis,initPgRouting, clipToExtent, importToDB_BBR, createFolder, psqltoshp, shptoraster
from calc_Schools import clipSelectScools, clipSelectCulture, importToDB, computeIsochrones, calculateIsochronesCount
from calc_PrimarySchools import calcPrimarySchools
from calc_ResidPrices import clipSelectHousing, importToDBHousing, calculateMeanPriceHousing
#from DBtoRaster import psqltoshp, shptoraster

def process_data(engine, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, cur, conn, city, 
                    python_scripts_folder_path, gdal_rasterize_path,
                    ancillary_data_folder_path, ancillary_EUROdata_folder_path, temp_shp_path, temp_tif_path,  bbr_folder_path,
                    initExtensionPostGIS, initExtensionPGRouting, initClipBBR, initImportBBR,
                    process_schools, clipSchools,  importTo_DB, calcIso, calcCountIso,
                    process_PrimSchools, clipPrimarySchools,
                    process_culture, clipCulture, 
                    process_housing, clipHousing, importToDBHousing, calcHousingPrices,
                    BBRpsqltoshp, BBRrasterize , BBRtype):
                    
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
    years_list = [2002,2004,2006,2008,2010,2012,2014,2016,2018 ] #2002,2004,2006,2008,2010,2012,2014,2016,2018,2020
    #2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016,
    #2003,2005,2007,2009,2011,2013,2015,2017,2019
    for year in years_list:
        if initClipBBR == "yes":
            print("------------------------------ CLIPPING BBR DATA TO bbox EXTENT------------------------------")
            clipToExtent(gdal_rasterize_path, bbr_folder_path, year, city)

        if initImportBBR == "yes":
            print("------------------------------ IMPORTING BBR TO DB------------------------------")
            importToDB_BBR(bbr_folder_path, city, conn, cur,  engine, year)

        ## ## ## ## ## ----- SCHOOLS  ----- ## ## ## ## ## ----> NEEDS CHANGES
        if process_schools == "yes" and BBRtype == "schools":
            print("------------------------------ BBR SCHOOLS ------------------------------")
            if clipSchools == "yes":
                clipSelectScools(gdal_rasterize_path, bbr_folder_path, ancillary_data_folder_path, year, city, BBRtype)
            if importTo_DB == "yes":
                importToDB(ancillary_data_folder_path, city, cur, engine, year, BBRtype)
            if calcIso == "yes":
                computeIsochrones(ancillary_data_folder_path, city, cur, conn, year, BBRtype)
            if calcCountIso == "yes":
                calculateIsochronesCount(ancillary_data_folder_path, city, conn, cur, year, BBRtype)
        
        ## ## ## ## ## ----- SCHOOLS  ----- ## ## ## ## ## ----> NEEDS CHANGES
        if process_PrimSchools == "yes" and BBRtype == "primaryschools":
            if clipPrimarySchools == "yes":
                comp_year = 2020
                calcPrimarySchools(ancillary_data_folder_path,city,cur,conn,year, comp_year, BBRtype)
            if calcIso == "yes":
                computeIsochrones(ancillary_data_folder_path, city, cur, conn, year, BBRtype)
            if calcCountIso == "yes":
                calculateIsochronesCount(ancillary_data_folder_path, city, conn, cur, year, BBRtype)

        ## ## ## ## ## ----- CULTURE  ----- ## ## ## ## ##
        if process_culture == "yes" and BBRtype == "culture":
            print("------------------------------ BBR CULTURE ------------------------------")
            if clipCulture == "yes":
                clipSelectCulture(gdal_rasterize_path, city, ancillary_data_folder_path, bbr_folder_path, year, BBRtype)
            if importTo_DB == "yes":
                print("import")
                importToDB(bbr_folder_path, city, cur, engine, year, BBRtype)
            if calcIso == "yes":
                computeIsochrones(ancillary_data_folder_path, city, cur, conn, year, BBRtype)
            if calcCountIso == "yes":
                calculateIsochronesCount(ancillary_data_folder_path, city, conn, cur, year, BBRtype)
        
        ## ## ## ## ## ----- PROCESS HOUSING PRICES  ----- ## ## ## ## ##
        if process_housing == "yes" and BBRtype == "housing":
            print("------------------------------ BBR HOUSING PRICES ------------------------------")
            if clipHousing == "yes":
                clipSelectHousing(gdal_rasterize_path, bbr_folder_path, ancillary_data_folder_path, year, city, BBRtype)
            if importToDBHousing == "yes":
                importToDBHousing(bbr_folder_path, city, conn, cur, engine, year, BBRtype)
            if calcHousingPrices == "yes":
                calculateMeanPriceHousing(ancillary_data_folder_path, city, conn, cur, year, BBRtype)

        # ## ## ## ## ----- EXPORT GPKG  ----- ## ## ## ## ##       
        if BBRpsqltoshp == "yes": 
            print("------------------------------ EXPORTING GPKG FROM DB {0},{1} ------------------------------".format(BBRtype,year))
            psqltoshp(city, engine, temp_shp_path, BBRtype, year)
        
        # ## ## ## ## ----- RASTERIZE  ----- ## ## ## ## ##
        if BBRrasterize == "yes" :
            print("------------------------------ RASTERIZING GPKG TO TIF {0},{1} ------------------------------".format(BBRtype,year))
            shptoraster(city, gdal_rasterize_path, 100, 100, temp_shp_path, temp_tif_path, year, BBRtype)    

    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))

