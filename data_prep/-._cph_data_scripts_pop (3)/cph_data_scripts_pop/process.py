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
from csv_to_raster import csvtoshp, shptoraster
#from fill_empty_rasters import createEmptyTif
#from tif_to_png import tiftopng, create_png
#from merge import merge_tif, getListOfFiles #Not Applicable
#from mergeSelection import sumUpTifsByGeographicalRegion,mergeTifs00,sumUpTotalPop #Not Applicable
from mergeSelectionCoI import sumUpTifsByGeographicalRegion, sumUpTifsByGeogrRegionCoI, mergeCoI, mergeAoI, mergeAoI3
from variables import country_dictW, country_dict, country_dictTest, country_dictCorrection

def process_data(ancillary_data_folder_path, ancillary_POPdata_folder_path, parent_path, gdal_rasterize_path, init_csv_to_shp, init_shp_to_tif, create_empty_tif, init_tif_to_png, merge_tifs, 
                merge_tifs_trial01, merge_tifs_trial02,merge_tifs_trial03, cph_area_path, city, python_scripts_folder_path):
    #Start total preparation time timer
    start_total_algorithm_timer = time.time()
    years_list= [1990, 1992, 1994, 1996, 1998,2000, 2002,2004,2006, 2008,2010,2012, 2014,2016, 2018 ] #'1990', '1992','1994', '1996', '1998', '2000', '2002', '2004', '2006', '2008', '2010', '2012', '2014', '2016', '2018'
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
       
        temp_png_path = ancillary_POPdata_folder_path + "/{}/temp_png".format(year)
        if not os.path.exists(temp_png_path):
            print("------------------------------ Creating temp_png_folder for {}------------------------------".format(year))
            os.makedirs(temp_png_path)
        else: 
            print("------------------------------ Folder already exists------------------------------")
    
    temp_tifMigGeogrGroups_path = os.path.dirname(ancillary_POPdata_folder_path) + "/GeogrGroupsRevised" 
    # It includes folders by geographic group for all years and 
    if not os.path.exists(temp_tifMigGeogrGroups_path):
        print("------------------------------ Creating GeogrGroups folder  ------------------------------")
        os.makedirs(temp_tifMigGeogrGroups_path)
    else: 
        print("------------------------------ Folder already exists------------------------------")
    
    """for j in country_dictCorrection:
        sub_MigGeogrGroups_path = temp_tifMigGeogrGroups_path + "/{}".format(j)
        if not os.path.exists(sub_MigGeogrGroups_path):
            print("------------------------------ Creating sub_GeogrGroups folder  ------------------------------")
            os.makedirs(sub_MigGeogrGroups_path)
        else: 
            print("------------------------------ Folder already exists------------------------------")"""

    """temp_tifPopGeogrGroups_path = os.path.dirname(ancillary_POPdata_folder_path) + "/PopGeogrGroups" # INcluding DNK in the Northern European Group
    if not os.path.exists(temp_tifPopGeogrGroups_path):
        print("------------------------------ Creating PopGeogrGroups folder  ------------------------------")
        os.makedirs(temp_tifPopGeogrGroups_path)
    else: 
        print("------------------------------ Folder already exists------------------------------")
    
    totalPopMig_path = os.path.dirname(ancillary_POPdata_folder_path) + "/totalPopMig" # INcluding DNK in the Northern European Group
    if not os.path.exists(totalPopMig_path):
        print("------------------------------ Creating MigGeogrGroups folder  ------------------------------")
        os.makedirs(totalPopMig_path)
    else: 
        print("------------------------------ Folder already exists------------------------------")
    
    mergedFinal00 = os.path.dirname(ancillary_POPdata_folder_path) + "/merged_all"
    if not os.path.exists(mergedFinal00):
        print("------------------------------ Creating tif Merged_folder  ------------------------------")
        os.makedirs(mergedFinal00)
    else: 
        print("------------------------------ Folder already exists------------------------------")
    """       
    # POPData : Initial Processing of csv files --------------------------------------------------------------------------------------
    if init_csv_to_shp == "yes":
        for year in years_list:
            print("------------------------------ Initial Processing of Population Data ------------------------------")
            csvtoshp(ancillary_POPdata_folder_path,ancillary_data_folder_path, year)
    
    if init_shp_to_tif == "yes":
        for year in years_list:
            print("------------------------------ Rasterize the Population Data {}------------------------------".format(year))
            shptoraster(ancillary_POPdata_folder_path,ancillary_data_folder_path, gdal_rasterize_path, city,year)
    
    if init_tif_to_png == "yes":
        print("------------------------------ Create PNG Images for Population Data ------------------------------")
        #tiftopng(ancillary_POPdata_folder_path, cph_area_path) 
    
    """
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
    # POPData : Merging_ applicable --------------------------------------------------------------------------------------
    if merge_tifs == "yes":
        
        for year in years_list: 
                #print(dct)     
                print("------------------------------ Summing Tif by Geographic Region {0}------------------------------".format(year))
                sumUpTifsByGeographicalRegion(ancillary_data_folder_path,ancillary_POPdata_folder_path,city,year,temp_tifMigGeogrGroups_path, country_dictCorrection)  

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


