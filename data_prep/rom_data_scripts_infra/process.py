# Imports

import os

import time
from importDataDB import initPostgis, initPgRouting, initialProcess  #, importWater, importTrainStations,importBusStops, import_buildings
from calc_Water import  calculateWater, water_dbTOtif #processCanals,
from calc_Streets import createNetwork
from calc_Rails import importTrainStops, computeTrainIsochrones, calculateTrainCount
from calc_Buses import importBusStops, computeBusIsochronesWalk, calculatebusCountWalk 
from DBtoRaster import bdTOraster

#from DBtoRaster import psqltoshp, shptoraster, bdTOraster

def process_data(engine, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, ancillary_data_folder_path,ancillary_EUROdata_folder_path,cur,conn, city,country, temp_shp_path, temp_tif_path,temp_tif_corine, python_scripts_folder_path,gdal_rasterize_path,
                    initExtensionPostGIS, initExtensionPGRouting, initImportProcess, 
                    init_waterProcess,  waterProcess00, waterProcess01, 
                    init_streetProcess, 
                    init_trainProcess, trainProcess00, trainProcess01, trainProcess02, trainProcess03, #trainProcess04,
                    init_busProcess,busProcess00, busProcess01, busProcess02, busProcess03,
                    #init_psqltoshp ,init_shptoraster
                    ):
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
    
    # Import and create Nuts,Case study extent, bbox, corine, grids
    if initImportProcess == "yes": 
        print("------------------------------ IMPORT AND CREATE BASIC TABLES ------------------------------")
        initialProcess(engine, gdal_rasterize_path, ancillary_data_folder_path, ancillary_EUROdata_folder_path,conn, cur, city, temp_shp_path, temp_tif_path,  python_scripts_folder_path)
    
    # Processing WATER data to postgres--------------------------------------------------------------------------------------
    if init_waterProcess == "yes":
        if waterProcess00 == "yes":
            print("------------------------------ IMPORT AND CREATE TABLE FOR WATERBODIES ------------------------------")
            print("------------------------------ PROCESS WATERBODIES ------------------------------")
            print("------------------------------ CALCULATE WATER COVERGAE PERCENTAGE ------------------------------")
            calculateWater(ancillary_data_folder_path, temp_shp_path, city, engine, cur,conn)
        if waterProcess01 == "yes":
            print("------------------------------ DB TO SHP AND RASTERIZE AND COMBINE TO CORINE WATER ------------------------------")
            water_dbTOtif(city, gdal_rasterize_path, cur, conn, engine, 100, 100, temp_shp_path, temp_tif_path, python_scripts_folder_path)
    
    # Processing STREET data to postgres--------------------------------------------------------------------------------------
    if init_streetProcess == "yes":
        print("------------------------------ CREATING NETWORK ------------------------------")
        createNetwork(pgpath,pghost,pgport, pguser, pgpassword, pgdatabase,ancillary_data_folder_path,cur,conn,engine, city, temp_shp_path)
    
    # Processing Train Station data to postgres--------------------------------------------------------------------------------------
    if init_busProcess == "yes": 
        if busProcess00 == "yes":  
            print("------------------------------ IMPORT OSM DATA FOR BUS STOPS ------------------------------")
            importBusStops(ancillary_data_folder_path,city,engine, temp_shp_path)
        if busProcess01 == "yes":    
            print("------------------------------ COMPUTE ISOCHRONES FOR BUS STOPS WALKING------------------------------")
            computeBusIsochronesWalk(ancillary_data_folder_path,city,cur,conn, engine, temp_shp_path)
        if busProcess02 == "yes":
            print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR BUS STOPS {0} ------------------------------")
            calculatebusCountWalk(ancillary_data_folder_path, city, conn, cur)
        if busProcess03 == "yes":
            layer = '{}_busstopscount'.format(city)
            layerFolder= '{}_busstops'.format(city)
            layerName = '{}_busstops'.format(city)
            bdTOraster(city, gdal_rasterize_path,engine, 100, 100, temp_shp_path, temp_tif_path, layer, layerFolder, layerName)

    # Processing train and metro Station data to postgres--------------------------------------------------------------------------------------
    if init_trainProcess == "yes":       
        if trainProcess00 == "yes":
            importTrainStops(ancillary_data_folder_path, city, engine, temp_shp_path)
        if trainProcess01 == "yes":
            print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR TRAIN STATIONS {0} ------------------------------")
            computeTrainIsochrones(ancillary_data_folder_path,city,cur,conn, engine, temp_shp_path)
        if trainProcess02 == "yes":
            print("------------------------------ COMPUTING ISOCHRONES FOR TRAIN STATIONS BIKING 15' with 15km/h------------------------------")
            calculateTrainCount(ancillary_data_folder_path, city, conn, cur)
        if trainProcess03 == "yes":
            layer = '{}_trainstopscount'.format(city)
            layerFolder= '{}_trainstations'.format(city)
            layerName = '{}_trainstations'.format(city)
            bdTOraster(city, gdal_rasterize_path,engine, 100, 100, temp_shp_path, temp_tif_path, layer, layerFolder, layerName)
            

    """    
    if init_psqltoshp == "yes":
        psqltoshp(city, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase,cur, conn, temp_shp_path)

    if init_shptoraster == "yes":
        shptoraster(city, gdal_rasterize_path, cur, conn, 100,100, temp_shp_path, temp_tif_path)
    """
    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))

