# Imports

import copy
import os
import time

from csv_to_raster import csvtoshp, shptoraster, sumGroups
#from fill_empty_rasters import createEmptyTif
#from tif_to_png import tiftopng, create_png
#from merge import merge_tif, getListOfFiles #Not Applicable
#from mergeSelection import sumUpTifsByGeographicalRegion,mergeTifs00,sumUpTotalPop #Not Applicable
from mergeSelectionCoI import (mergeAoI, mergeAoI3, mergeCoI,
                               sumUpTifsByGeographicalRegion,
                               sumUpTifsByGeogrRegionCoI)
from sumByCountry import sumCountries
from variables import ( country_dictEU, country_dictEurope)


def process_data(ancillary_data_folder_path, ancillary_POPdata_folder_path, parent_path, gdal_rasterize_path, init_csv_to_shp, init_shp_to_tif, create_empty_tif, init_tif_to_png, sum_tifs, 
                sum_Groups, merge_tifs_trial01, merge_tifs_trial02,merge_tifs_trial03, city, python_scripts_folder_path):
    #Start total preparation time timer
    start_total_algorithm_timer = time.time()
    years_list= [2017,2018,2019,2020,2021]  #,2018,2019,2020,2021
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
    
    if init_shp_to_tif == "yes":
        for year in years_list:
            print("------------------------------ Rasterize the Population Data {}------------------------------".format(year))
            sumCountries(ancillary_POPdata_folder_path,year)
            #shptoraster(ancillary_POPdata_folder_path,ancillary_data_folder_path, gdal_rasterize_path, city,year)
    if sum_Groups == "yes":
        for year in years_list:
            sumGroups(ancillary_POPdata_folder_path,year, country_dictEU)

    # POPData : Merging_ applicable --------------------------------------------------------------------------------------
    if sum_tifs == "yes":
        temp_tifMigGeogrGroups_path = os.path.dirname(ancillary_POPdata_folder_path) + "/GeogrGroups" 
        # It includes folders by geographic group for all years and 
        if not os.path.exists(temp_tifMigGeogrGroups_path):
            print("------------------------------ Creating GeogrGroups folder  ------------------------------")
            os.makedirs(temp_tifMigGeogrGroups_path)
        else: 
            print("------------------------------ Folder already exists------------------------------")
        for year in years_list: 
            #print(dct)     
            print("------------------------------ Summing Tif by Geographic Region {0}------------------------------".format(year))
            sumUpTifsByGeographicalRegion(ancillary_data_folder_path,ancillary_POPdata_folder_path,city,year,temp_tifMigGeogrGroups_path, country_dictEurope)  

    # POPData : Merging_ applicable --------------------------------------------------------------------------------------
    if merge_tifs_trial01 == "yes":
        CoIs = ['tur', 'pak', 'irq','pol','deu']
        for CoI in CoIs:
            save_path = os.path.dirname(ancillary_POPdata_folder_path) + '/SumMig_GeogrGroups/SUM_{}/'.format(CoI)
            print(save_path)
            if not os.path.exists(save_path):
                print("------------------------------ Creating folder  ------------------------------")
                os.makedirs(save_path)
            else: 
                print("------------------------------ Folder already exists------------------------------")

            merge_path = os.path.dirname(ancillary_POPdata_folder_path) + "/merged_trial01/{}".format(CoI) 
            # merged_trial01 takes trial01 with 35Bands
            if not os.path.exists(merge_path):
                print("------------------------------ Creating folder for ------------------------------")
                os.makedirs(merge_path)
            else: 
                print("------------------------------ Folder already exists------------------------------")
                
            dct= copy.deepcopy(country_dict)
            for v in dct.values():
                if CoI in v : 
                    v.remove(CoI)
            
            for year in years_list: 
                #print(dct)     
                #print("------------------------------ Summing Tif by Geographic Region for {0},{1}------------------------------".format(CoI, year))
                #sumUpTifsByGeogrRegionCoI(ancillary_data_folder_path,ancillary_POPdata_folder_path,city,year,save_path, dct, CoI)
             
                print("------------------------------ Merging Layers for {0},{1}------------------------------".format(CoI, year))
                mergeCoI(ancillary_data_folder_path,ancillary_POPdata_folder_path,merge_path,city,year,save_path,python_scripts_folder_path,CoI)
                # Final Bands: 35 
                # 1 Country of Interest, 18 geographic regions, 11 Socioeconomic, 1bus, 1train, 1water, 2corine       
    
    # POPData : Merging_ applicable --------------------------------------------------------------------------------------
    # Merge files by region of origin
    if merge_tifs_trial02 == "yes":
        AoIs = []
        folder_path = os.path.dirname(ancillary_POPdata_folder_path)  + "/GeogrGroups"
        
        mergedFinal02 = os.path.dirname(ancillary_POPdata_folder_path)  + "/merged_trial02"
        if not os.path.exists( mergedFinal02):
            print("------------------------------ Creating folder for ------------------------------")
            os.makedirs( mergedFinal02)
        else: 
            print("------------------------------ Folder already exists------------------------------")
        for AoI in os.listdir(folder_path):
            
            AoIs.append(AoI)
            print(AoIs)
            mergedFinal02AoI = mergedFinal02 + "/{}".format(AoI) 
            # merged_trial01 takes trial01 with 35Bands
            if not os.path.exists(mergedFinal02AoI):
                print("------------------------------ Creating folder for ------------------------------")
                os.makedirs(mergedFinal02AoI)
            else: 
                print("------------------------------ Folder already exists------------------------------")        
            
            for year in years_list: 
                mergeAoI(ancillary_data_folder_path,ancillary_POPdata_folder_path,folder_path,city, mergedFinal02,python_scripts_folder_path,year,AoI)
    
    # POPData : Merging_ applicable --------------------------------------------------------------------------------------
    # Merge files by region of origin
    if merge_tifs_trial03 == "yes":
        
        AoIs = []
        folder_path = os.path.dirname(ancillary_POPdata_folder_path)  + "/GeogrGroups"
        
        mergedFinal03 = parent_path  + "/data/{}/trial05B".format(city)
        if not os.path.exists( mergedFinal03):
            print("------------------------------ Creating folder for ------------------------------")
            os.makedirs( mergedFinal03)
        else: 
            print("------------------------------ Folder already exists------------------------------")
        for AoI in os.listdir(folder_path):
            
            AoIs.append(AoI)
            print(AoIs)
            mergedFinal03AoI = mergedFinal03 + "/{}".format(AoI) 
            # merged_trial01 takes trial01 with 35Bands
            if not os.path.exists(mergedFinal03AoI):
                print("------------------------------ Creating folder for ------------------------------")
                os.makedirs(mergedFinal03AoI)
            else: 
                print("------------------------------ Folder already exists------------------------------")        
            
            for year in years_list: 
                mergeAoI3(ancillary_data_folder_path,ancillary_POPdata_folder_path,folder_path,city, mergedFinal03,python_scripts_folder_path,year,AoI)
    
    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))


