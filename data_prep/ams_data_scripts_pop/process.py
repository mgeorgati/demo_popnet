# Imports
import subprocess
import os
import gdal
import ogr
import osr
import psycopg2
import time
import copy
import re
from itertools import combinations
from csv_to_raster import createFolder, csvtoshp, calc_Perc, shptoraster  
from normalise import normalize_Numbers, shptorasterNorm, mergeAoINorm
#from mergeSelectionCoI import sumUpTifsByGeographicalRegion, sumUpTifsByGeogrRegionCoI, mergeCoI, mergeAoI
from variables import country_Orig
                    
def process_data(base_dir, ancillary_data_folder_path, ancillary_POPdata_folder_path, gdal_rasterize_path, init_csv_to_shp, init_calcPercentages, init_shp_to_tif, create_empty_tif, init_tif_to_png, merge_tifs, 
                init_calc_Norm, init_shp_to_tif_Norm, select_Countries, merge_tifs_Norm, cph_area_path, city, python_scripts_folder_path):
    #Start total preparation time timer
    start_total_algorithm_timer = time.time()
    years_list= [ 1992, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010 ] # 2012, 2014, 2016, 2018
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
            csvtoshp(ancillary_POPdata_folder_path,ancillary_data_folder_path,year, country_Orig)
            #sumCountries(ancillary_POPdata_folder_path,year, dictNLD)
        
        if init_calcPercentages == "yes":
            print("------------------------------ Calculate percentage of migrant groups per total population and migration ------------------------------")
            calc_Perc(ancillary_POPdata_folder_path, city,year)        

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
                trialNo = "trial03"
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


        # POPData : Merging_ applicable --------------------------------------------------------------------------------------
        #if merge_tifs == "yes":
            #print(dct)     
            #print("------------------------------ Summing Tif by Geographic Region {0}------------------------------".format(year))
            #sumUpTifsByGeographicalRegion(ancillary_data_folder_path,ancillary_POPdata_folder_path,city,year,temp_tifMigGeogrGroups_path, country_dictW)
    
    """if init_tif_to_png == "yes":
        print("------------------------------ Create PNG Images for Population Data ------------------------------")
        #tiftopng(ancillary_POPdata_folder_path, cph_area_path) 
    
    
    # POPData : Optional --------------------------------------------------------------------------------------
    if create_empty_tif == "yes":
        print("------------------------------ Check folders for mismatches of countries and create empty rasters if they do not exist ------------------------------")
        
        for i in combinations(years,2):
            print(i[0], i[1])
            tif_pathA = ancillary_POPdata_folder_path  + "/{}/temp_tif".format(i[0])
            tif_pathB = ancillary_POPdata_folder_path  + "/{}/temp_tif".format(i[1])
            yearA = i[0]
            yearB = i[1]
            #temp_tif_path = ancillary_POPdata_folder_path + "/{}/temp_tif".format(dir)
            createEmptyTif(tif_pathA,tif_pathB,yearA,yearB)    

    # POPData : Merging_not applicable --------------------------------------------------------------------------------------
    if merge_tifs == "yes":
        print("------------------------------ Merge Population Data ------------------------------")
        merge_tif(ancillary_POPdata_folder_path,python_scripts_folder_path)
    
    # POPData : Merging_ applicable --------------------------------------------------------------------------------------
    if merge_tifs_trial00 == "yes":
        
        for year in years_list:
            print("------------------------------ Creating sum files for year {} ------------------------------".format(year))
            #sumUpTifsByGeographicalRegion(ancillary_data_folder_path,ancillary_POPdata_folder_path,city,year,temp_tifPopGeogrGroups_path, country_dict)
            sumUpTifsByGeographicalRegion(ancillary_data_folder_path,ancillary_POPdata_folder_path,city,year,temp_tifMigGeogrGroups_path, country_dictW)
            #sumUpTotalPop(ancillary_data_folder_path,ancillary_POPdata_folder_path,city,year,temp_tifMigGeogrGroups_path,totalPopMig_path)
        print("------------------------------ Merging Files ------------------------------")
        #mergeTifs00(ancillary_data_folder_path,ancillary_POPdata_folder_path,mergedFinal00,city,year,temp_tifPopGeogrGroups_path,python_scripts_folder_path)
    """
      

    """# POPData : Merging_ applicable --------------------------------------------------------------------------------------
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
    """
    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))


