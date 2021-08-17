# Imports
import subprocess
import os
import gdal
import ogr
import osr
import psycopg2
import time
from importDataDB import initPostgis, initPgRouting, initialimports, initialProcess#, importWater, importTrainStations,importBusStops, import_buildings
from calc_Water import processCanals, calculateWater# importWaterLayers #calculateWater
from calc_Streets import createNetwork
from calc_Rails import computeTrainIsochrones,calculateTrainCount, computeTrainIsochronesWalk,calculateTrainCountWalk
#from calc_Buses import computeBusIsochrones, calculateBusCount

from DBtoRaster import psqltoshp, shptoraster

def process_data(engine, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, ancillary_data_folder_path,ancillary_EUROdata_folder_path,cur,conn, city,country,nuts3_cd1, temp_shp_path, temp_tif_path,temp_tif_corine, python_scripts_folder_path,gdal_rasterize_path,
                    initExtensionPostGIS, initExtensionPGRouting,initImports, initImportProcess, init_waterProcess, init_streetProcess, init_tramProcess,init_busProcess,init_psqltoshp ,init_shptoraster):
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
        #importWaterLayers(ancillary_data_folder_path, temp_shp_path, city)
        
        #processCanals(ancillary_data_folder_path, temp_shp_path, city, country, engine, cur )
        calculateWater(city,country,conn,cur)
        print("------------------------------ CREATING Water ------------------------------")
        #importWater(ancillary_data_folder_path, city, country, engine)
        print("------------------------------ CREATING Water ------------------------------")
        #calculateWater(city,country,conn,cur)

        # Import ocean table and create the subdividd waterbodies table in combination with lakes 
        print("------------------------------ IMPORT AND CREATE TABLE FOR WATERBODIES ------------------------------")
        #importWater(cur,conn)
    
    # Processing STREET data to postgres--------------------------------------------------------------------------------------
    if init_streetProcess == "yes":
        print("------------------------------ CREATING NETWORK ------------------------------")
        createNetwork(pgpath,pghost,pgport, pguser, pgpassword, pgdatabase,ancillary_data_folder_path,cur,conn,engine, city)
    
    # Processing Train Station data to postgres--------------------------------------------------------------------------------------
    if init_tramProcess == "yes":       
        print("------------------------------ COMPUTING ISOCHRONES FOR TRAM STATIONS BIKING------------------------------")
        #computeTrainIsochrones(ancillary_data_folder_path, city, cur, conn)
        print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR TRAIN STATIONS {0} ------------------------------")
        #calculateTrainCount(ancillary_data_folder_path, city, conn, cur)
        print("------------------------------ COMPUTING ISOCHRONES FOR TRAIN STATIONS WALKING------------------------------")
        computeTrainIsochronesWalk(ancillary_data_folder_path, city, cur, conn)
        print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR TRAIN STATIONS {0} ------------------------------")
        calculateTrainCountWalk(ancillary_data_folder_path, city, conn, cur)

    """
    # Import table for train stations and create table for the case study 
        print("------------------------------ IMPORT AND CREATE TABLE FOR TRAIN STATIONS ------------------------------")
        #importTrainStations(ancillary_data_folder_path,cur,conn)
    
    # Import table for bus and streets and create table for the case study 
        print("------------------------------ IMPORT AND CREATE TABLE FOR BUS STOPS ------------------------------")
        #importBusStops(ancillary_data_folder_path,city,conn,cur)
    
    # Processing WATER data to postgres--------------------------------------------------------------------------------------
    if init_waterProcess == "yes":
        print("------------------------------ CREATING Water ------------------------------")
        importWater(ancillary_data_folder_path,city, country, cur,conn)
        print("------------------------------ CREATING Water ------------------------------")
        calculateWater(city,country,conn,cur)
    
    # Processing STREET data to postgres--------------------------------------------------------------------------------------
    if init_streetProcess == "yes":
        print("------------------------------ CREATING NETWORK ------------------------------")
        createNetwork(pgpath,pghost,pgport, pguser, pgpassword, pgdatabase,ancillary_data_folder_path,cur,conn,city)
    
    # Processing Train Station data to postgres--------------------------------------------------------------------------------------
    if init_trainProcess == "yes":   
        print("------------------------------ COMPUTING ISOCHRONES FOR TRAIN STATIONS ------------------------------")
        years=[1990,1992,1994,1996,1998,2000,2002,2004,2006,2008,2010,2012,2014,2016,2018,2020]
        for year in years:
            print("------------------------------ COMPUTING ISOCHRONES FOR TRAIN STATIONS {0} ------------------------------".format(year))
            computeTrainIsochrones(ancillary_data_folder_path, city, cur, conn, year)
            print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR TRAIN STATIONS {0} ------------------------------".format(year))
            calculateTrainCount(ancillary_data_folder_path, city, conn, cur, year)
      
     # Processing STREET data to postgres--------------------------------------------------------------------------------------
    if init_busProcess == "yes":
        print("------------------------------ COMPUTING ISOCHRONES FOR BUS STOPS ------------------------------")
        years=[]
        cur.execute("SELECT distinct(year) FROM {0}_busst where year% 2 = 0 AND year>2016 AND year<=2020 order by year ASC;".format(city))
        year_id = cur.fetchall()
        for id in year_id:
            years.append(id[0])
        print(years)
        
        for year in years:
            print("------------------------------ COMPUTING ISOCHRONES FOR BUS STOPS {0} ------------------------------".format(year))
            computeBusIsochrones(ancillary_data_folder_path, city, cur, conn,year)
            print("------------------------------ COMPUTING COUNT OF ISOCHRONES FOR CELL IN GRID FOR TRAIN STATIONS {0} ------------------------------".format(year))
            calculateBusCount(ancillary_data_folder_path, city, conn, cur, year)
    
    if init_psqltoshp == "yes":
        psqltoshp(city, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase,cur, conn, temp_shp_path)

    if init_shptoraster == "yes":
        shptoraster(city, gdal_rasterize_path, cur, conn, 100,100, temp_shp_path, temp_tif_path)"""
    
    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))

