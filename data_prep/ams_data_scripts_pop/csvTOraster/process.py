# Imports
import os
import sys
import time
import copy
import re
from itertools import combinations
from csv_to_raster import csvtoshp, shptoraster 
from calcPercentages import calc_Perc, shptorasterPercentages
from normalise import normalize_Numbers, shptorasterNorm, mergeAoINorm
from mergeSelectionCoI import mergeAoI
#from mergeSelectionCoI import sumUpTifsByGeographicalRegion, sumUpTifsByGeogrRegionCoI, mergeCoI, mergeAoI
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from variables import country_Orig, country_OrigWnW
from mainFunctions import createFolder
                    
def process_data(base_dir, ancillary_data_folder_path, ancillary_POPdata_folder_path, gdal_rasterize_path, 
                init_csv_to_shp, init_calcPercentages, calcPerc, rasterizePerc, init_shp_to_tif, create_empty_tif, init_tif_to_png, merge_tifs, 
                init_calc_Norm, init_shp_to_tif_Norm, select_Countries, merge_tifs_Norm, city, python_scripts_folder_path):
    #Start total preparation time timer
    start_total_algorithm_timer = time.time()
    years_list= [2018] 
    #1992, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018
    for year in years_list:
        temp_shp_path = ancillary_POPdata_folder_path + "/{}/temp_shp".format(year)
        createFolder(temp_shp_path)
        
        temp_tif_path = ancillary_POPdata_folder_path + "/{}/temp_tif".format(year)
        createFolder(temp_tif_path)
       
        print("------------------------------ Initial Processing of Population Data {}------------------------------".format(year))
    # POPData : Initial Processing of csv files --------------------------------------------------------------------------------------
        if init_csv_to_shp == "yes": 
            print("------------------------------ Convert XLSX to shapefile ------------------------------")
            csvtoshp(ancillary_POPdata_folder_path,ancillary_data_folder_path,year, country_OrigWnW) #<<<<---
        
        if init_calcPercentages == "yes":
            if calcPerc == "yes":
                print("------------------------------ Calculate percentage of migrant groups per total population and migration ------------------------------")
                calc_Perc(ancillary_POPdata_folder_path, city,year) 
            if rasterizePerc == "yes":
                print("------------------------------ Rasterize percentages of migrant groups per total population and migration ------------------------------")
                shptorasterPercentages(ancillary_POPdata_folder_path,ancillary_data_folder_path, gdal_rasterize_path, city,year)       

        if init_shp_to_tif == "yes":
            print("------------------------------ Rasterize the Population Data {}------------------------------".format(year))
            shptoraster(ancillary_POPdata_folder_path,ancillary_data_folder_path, gdal_rasterize_path, city,year, country_Orig)

        ## ## ## ## ## ----- Normalisation Process ----- ## ## ## ## ##
        if init_calc_Norm == "yes":
            print("------------------------------ Normalize the Population Data {}------------------------------".format(year))
            normalize_Numbers(ancillary_POPdata_folder_path, city,year)
        
        if init_shp_to_tif_Norm == "yes":
            print("------------------------------ Rasterise Normalized Population Data {}------------------------------".format(year))
            shptorasterNorm(ancillary_POPdata_folder_path,ancillary_data_folder_path, gdal_rasterize_path, city, year, country_Orig)
        
        # Merge files by region of origin
        if select_Countries == "yes":

            ## ## ## ## ## ----- Select migrant groups included in the analysis ----- ## ## ## ## ##
            AoIs = ["Oceania", "EurNotEU", "EurEUNoL", "Centr_Asia", "East_Asia", "SEast_Asia", "South_Asia", "West_Asia",
                    "North_Amer", "Latin_Amer", "North_Afr" ,"SubSah_Afr", "Others", "Colonies" ]
            for AoI in AoIs:
                src_path = os.path.dirname(ancillary_POPdata_folder_path) + "/Normalized/{1}/{0}_{1}.tif".format(year, AoI)
                destination_path = os.path.dirname(ancillary_POPdata_folder_path)  + "/Normalized/00GeogrGroups_sel_Norm/{1}".format(year, AoI)
                createFolder(destination_path)
                copy(src_path, destination_path)
        
        if merge_tifs_Norm == "yes":
            folder_path = os.path.dirname(ancillary_POPdata_folder_path) + "/Normalized/00GeogrGroups_sel_Norm"
            AoIs = []
            for AoI in os.listdir(folder_path):
                AoIs.append(AoI)
                
                ## ## ## ## ## ----- Specify the trial number of input layers ----- ## ## ## ## ##
                trialNo = "trial08"
                ## ## ## ## ## ----- Select categories to include in input layers ----- ## ## ## ## ##
                # Add age groups
                demo_age = "yes"
                #Add natural growth (births,deaths, marriages)
                demo_ng = "no"
                #Add inclome and education 
                demo_se = "no"
                #Add buildings
                buildings = "no"
                # Add proximity to bus stops and train stations
                transport = "no"
                # Add corine data
                corine = "yes"
                # Add home price
                home_prices = "yes"

                mergedFolder = base_dir + "/model/{0}_model/data/{1}/{2}".format(city, trialNo, AoI)  
                createFolder(mergedFolder)  
                
                mergeAoINorm(ancillary_data_folder_path, ancillary_POPdata_folder_path, folder_path, city, mergedFolder, python_scripts_folder_path, year, AoI, demo_age, demo_ng, demo_se, buildings, transport, corine, home_prices)

        if merge_tifs == "yes":
            folder_path = os.path.dirname(ancillary_POPdata_folder_path) + "/GeogrGroups_sel"
            AoIs = []
            for AoI in os.listdir(folder_path):
                AoIs.append(AoI)
                
                ## ## ## ## ## ----- Specify the trial number of input layers ----- ## ## ## ## ##
                trialNo = "trial09"
                ## ## ## ## ## ----- Select categories to include in input layers ----- ## ## ## ## ##
                # Add age groups
                demo_age = "yes"
                #Add natural growth (births,deaths, marriages)
                demo_ng = "no"
                #Add inclome and education 
                demo_se = "no"
                #Add buildings
                buildings = "no"
                # Add proximity to bus stops and train stations
                transport = "no"
                # Add corine data
                corine = "yes"
                # Add home price
                home_prices = "yes"

                mergedFolder = base_dir + "/model/{0}_model/data/{1}/{2}".format(city, trialNo, AoI)  
                createFolder(mergedFolder)  
                
                mergeAoI(ancillary_data_folder_path, ancillary_POPdata_folder_path, folder_path, city, mergedFolder, python_scripts_folder_path, year, AoI, demo_age, demo_ng, demo_se, buildings, transport, corine, home_prices)


    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))


