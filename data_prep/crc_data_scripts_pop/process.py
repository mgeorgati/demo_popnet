# Imports

import copy
import os
import time

from csv_to_raster import csvtoshp, shptoraster, sumGroups



def process_data(ancillary_data_folder_path, ancillary_POPdata_folder_path, parent_path, gdal_rasterize_path, init_csv_to_shp, init_shp_to_tif, create_empty_tif, init_tif_to_png, sum_tifs, 
                sum_Groups, merge_tifs_trial01, merge_tifs_trial02,merge_tifs_trial03, city, python_scripts_folder_path):
    #Start total preparation time timer
    start_total_algorithm_timer = time.time()
    years_list= [2017,2018,2019,2020,2021]  
    # 1990, 1992, 1994, 1996, 1998,2000, 2002,2004,2006, 2008,2010,2012, 2014,2016, 2018
    for year in years_list:
        temp_shp_path = ancillary_POPdata_folder_path + "/{}/temp_shp".format(year)
        if not os.path.exists(temp_shp_path):
            print("------------------------------ Creating temp_shp_folder for {}------------------------------".format(year))
            os.makedirs(temp_shp_path) 
        else: 
            print("------------------------------ Folder already exists------------------------------")
        
        temp_tif_path = ancillary_POPdata_folder_path + "/{}/temp_tif".format(year)
        if not os.path.exists(temp_tif_path):
            print("------------------------------ Creating temp_tif_folder for {}------------------------------".format(year))
            os.makedirs(temp_tif_path)
        else: 
            print("------------------------------ Folder already exists------------------------------")
       
        # POPData : Initial Processing of csv files --------------------------------------------------------------------------------------
        if init_csv_to_shp == "yes":
            #for year in years_list:
            print("------------------------------ Initial Processing of Population Data ------------------------------")
            csvtoshp(ancillary_POPdata_folder_path,ancillary_data_folder_path,city, year, country_dictEurope)
    
    
    
    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))


