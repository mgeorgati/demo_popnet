# Imports
import os
import time
from importDataDB import initPostgis, initPgRouting, initialimports, initialProcess#, importWater, importTrainStations,importBusStops, import_buildings
from calc_Water import processCanals ,calculateWater, water_dbTOtif
from calc_Streets import createNetwork
from calc_Rails import computeTrainIsochrones, calculateTrainCount
from calc_Buses import computeBusIsochronesWalk, calculatebusCountWalk
from DBtoRaster import bdTOraster

def process_data(engine, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, ancillary_data_folder_path,ancillary_EUROdata_folder_path,cur,conn, 
                 city,country,nuts3_cd1, temp_shp_path, temp_tif_path, temp_tif_corine, python_scripts_folder_path, gdal_rasterize_path,
                    initExtensionPostGIS, initExtensionPGRouting,initImports, initImportProcess, 
                    init_waterProcess, waterProcess00, waterProcess01, waterProcess02,
                    init_streetProcess, 
                    init_trainProcess, trainProcess00, trainProcess01, trainProcess02,
                    init_busProcess, busProcess00, busProcess01, busProcess02):
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
        initialProcess(engine, ancillary_data_folder_path,ancillary_EUROdata_folder_path,pgpath, pghost, pgport, pguser, pgpassword,pgdatabase,conn, cur, nuts3_cd1, city,country, temp_shp_path, temp_tif_path, temp_tif_corine, python_scripts_folder_path)
    
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
        createNetwork(ancillary_data_folder_path,cur,conn,engine, city, temp_shp_path)
 
    # Processing train and metro Station data to postgres--------------------------------------------------------------------------------------
    if init_trainProcess == "yes":       
        if trainProcess00 == "yes":
            print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR TRAIN STATIONS {0} ------------------------------")
            print("------------------------------ COMPUTING ISOCHRONES FOR TRAIN STATIONS BIKING 15' with 15km/h------------------------------")
            computeTrainIsochrones(ancillary_data_folder_path,city,cur,conn, engine, temp_shp_path)
        if trainProcess01 == "yes":
            print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR TRAIN STATIONS {0} ------------------------------")
            calculateTrainCount(city, conn, cur)
        if trainProcess02 == "yes":
            print("------------------------------ RASTERIZING TRAIN STATIONS ------------------------------")
            layer = "{}_trainstopscount".format(city)
            layerFolder = "{}_trainstations".format(city)
            layerName = "{}_trainstations".format(city)
            bdTOraster(city, gdal_rasterize_path,engine, 100,100 , temp_shp_path, temp_tif_path, layer, layerFolder, layerName)
   
    # Processing Train Station data to postgres--------------------------------------------------------------------------------------
    if init_busProcess == "yes": 
        if busProcess00 == "yes":  
            print("------------------------------ IMPORT OSM DATA FOR BUS STOPS ------------------------------")   
            print("------------------------------ COMPUTE ISOCHRONES FOR BUS STOPS WALKING------------------------------")
            computeBusIsochronesWalk(ancillary_data_folder_path,city,cur,conn, engine, temp_shp_path)
        if busProcess01 == "yes":
            print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR BUS STOPS {0} ------------------------------")
            calculatebusCountWalk(ancillary_data_folder_path, city, conn, cur)
        if busProcess02 == "yes":
            print("------------------------------ RASTERIZING BUS STOPS ------------------------------")
            layer = "{}_busstopscount".format(city)
            layerFolder = "{}_busstops".format(city)
            bdTOraster(city, gdal_rasterize_path,engine, 100,100, temp_shp_path, temp_tif_path, layer, layerFolder, layerFolder )
    
    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))

