# Imports
import subprocess
import os
import gdal
import ogr
import osr
import psycopg2
import time
from importDataDB import initPostgis, initPgRouting, initialimports, initialProcess  #, importWater, importTrainStations,importBusStops, import_buildings
from calc_Water import processCanals, calculateWater, water_dbTOtif 
from calc_Streets import createNetwork
from calc_Rails import importTrainsToDB, openingYeartoMetroStations, computeTrainIsochronesWalk,calculateTrainCountWalk #computeTrainIsochrones,calculateTrainCount,
from calc_Buses import importBusStops, computeBusIsochronesWalk, calculatebusCountWalk 

from DBtoRaster import psqltoshp, shptoraster, bdTOraster

def process_data(engine, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, ancillary_data_folder_path,ancillary_EUROdata_folder_path,cur,conn, city,country,nuts3_cd1, temp_shp_path, temp_tif_path,temp_tif_corine, python_scripts_folder_path,gdal_rasterize_path,
                    initExtensionPostGIS, initExtensionPGRouting,initImports, initImportProcess, 
                    init_waterProcess, waterProcess00, waterProcess01, waterProcess02,
                    init_streetProcess, 
                    init_tramProcess, tramProcess00, tramProcess01, tramProcess02, tramProcess03, tramProcess04,
                    init_busProcess,busProcess00, busProcess01, busProcess02, busProcess03,
                    init_psqltoshp ,init_shptoraster):
                    #init_buildingsProcess,
    #Start total preparation time timer
    start_total_algorithm_timer = time.time()

    if not os.path.exists(temp_shp_path):
        os.makedirs(temp_shp_path)

    if not os.path.exists(temp_tif_path):
        os.makedirs(temp_tif_path)

    if not os.path.exists(temp_tif_corine):
        os.makedirs(temp_tif_corine)
    
    # Importing data to postgres--------------------------------------------------------------------------------------
    if initExtensionPostGIS == "yes":
        print("------------------------------ CREATING NECESSARY EXTENSIONS PostGIS------------------------------")
        initPostgis(pghost, pgport, pguser, pgpassword, pgdatabase, cur, conn,city)
    
    if initExtensionPGRouting == "yes":
        print("------------------------------ CREATING NECESSARY EXTENSIONS PGRouting------------------------------")
        initPgRouting(pghost, pgport, pguser, pgpassword, pgdatabase, cur, conn)
    
    if initImports == "yes":
        print("------------------------------ CREATING NECESSARY EXTENSIONS PGRouting------------------------------")
        initialimports(engine,conn, cur, ancillary_data_folder_path,ancillary_EUROdata_folder_path,nuts3_cd1,city,country, temp_shp_path) #pgpath, pghost, pgport, pguser, pgpassword,pgdatabase,conn, cur, 
    
    # Import and create Nuts,Case study extent, bbox, corine, grids
    if initImportProcess == "yes": 
        print("------------------------------ IMPORT AND CREATE BASIC TABLES ------------------------------")
        initialProcess(engine, gdal_rasterize_path, ancillary_data_folder_path,ancillary_EUROdata_folder_path,pgpath, pghost, pgport, pguser, pgpassword,pgdatabase,conn, cur, nuts3_cd1, city,country, temp_shp_path, temp_tif_path, python_scripts_folder_path)
    
    # Processing WATER data to postgres--------------------------------------------------------------------------------------
    if init_waterProcess == "yes":
        if waterProcess00 == "yes":
            print("------------------------------ IMPORT AND CREATE TABLE FOR WATERBODIES ------------------------------")
            print("------------------------------ PROCESS WATERBODIES ------------------------------")
            processCanals(ancillary_data_folder_path, temp_shp_path, city, country, engine, cur )
        if waterProcess01 == "yes":
            print("------------------------------ CALCULATE WATER COVERGAE PERCENTAGE ------------------------------")
            calculateWater(city,country,conn,cur)
        if waterProcess02 == "yes":
            print("------------------------------ DB TO SHP AND RASTERIZE AND COMBINE TO CORINE WATER ------------------------------")
            water_dbTOtif(city, gdal_rasterize_path, cur, conn, engine, 100, 100, temp_shp_path, temp_tif_path, python_scripts_folder_path)
    
    # Processing STREET data to postgres--------------------------------------------------------------------------------------
    if init_streetProcess == "yes":
        print("------------------------------ CREATING NETWORK ------------------------------")
        createNetwork(pgpath,pghost,pgport, pguser, pgpassword, pgdatabase,ancillary_data_folder_path,cur,conn,engine, city)
    
    # Processing Tram and metro Station data to postgres--------------------------------------------------------------------------------------
    if init_tramProcess == "yes":       
        if tramProcess00 == "yes":
            importTrainsToDB(ancillary_data_folder_path,city,cur,conn,engine)
        if tramProcess01 == "yes":
            print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR TRAIN STATIONS {0} ------------------------------")
            openingYeartoMetroStations(ancillary_data_folder_path,city,cur,conn)
        
        years_list= [ 1992, 1998, 2004, 2006, 2018 ] 
        for year in years_list:
            if tramProcess02 == "yes":
                print("------------------------------ COMPUTING ISOCHRONES FOR TRAIN STATIONS BIKING 15' with 15km/h------------------------------")
                computeTrainIsochronesWalk(ancillary_data_folder_path, city, cur, conn, year)
            if tramProcess03 == "yes":
                print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR TRAIN STATIONS {0} ------------------------------")
                calculateTrainCountWalk(ancillary_data_folder_path, city, conn, cur, year)
            if tramProcess04 == "yes":
                print("------------------------------ RASTERIZING TRAIN STATIONS ------------------------------")
                layer = "{}_stationcount".format(year)
                layerFolder = "{}_trainstations".format(city)
                layerName = "{}_trainstations".format(year)
                bdTOraster(city, gdal_rasterize_path,engine, 100,100 , temp_shp_path, temp_tif_path, layer, layerFolder, layerName)

    # Processing Train Station data to postgres--------------------------------------------------------------------------------------
    if init_busProcess == "yes": 
        if busProcess00 == "yes":  
            print("------------------------------ IMPORT OSM DATA FOR BUS STOPS ------------------------------")
            importBusStops(ancillary_data_folder_path,city,engine)
        if busProcess01 == "yes":    
            print("------------------------------ COMPUTE ISOCHRONES FOR BUS STOPS WALKING------------------------------")
            computeBusIsochronesWalk(ancillary_data_folder_path,city,cur,conn, engine, temp_shp_path)
        if busProcess02 == "yes":
            print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR BUS STOPS {0} ------------------------------")
            calculatebusCountWalk(ancillary_data_folder_path, city, conn, cur)
        if busProcess03 == "yes":
            print("------------------------------ RASTERIZING BUS STOPS ------------------------------")
            layer = "{}_busstopscount".format(city)
            layerFolder = "{}_busstops".format(city)
            bdTOraster(city, gdal_rasterize_path,engine, 100,100, temp_shp_path, temp_tif_path, layer, layerFolder, layerFolder )

    """    
    if init_psqltoshp == "yes":
        psqltoshp(city, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase,cur, conn, temp_shp_path)

    if init_shptoraster == "yes":
        shptoraster(city, gdal_rasterize_path, cur, conn, 100,100, temp_shp_path, temp_tif_path)"""
    
    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))

