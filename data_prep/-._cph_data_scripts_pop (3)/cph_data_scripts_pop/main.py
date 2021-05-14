# Main Script for data preparation -------------------------------------------------------------------------------------
# imports
import os
from process import process_data

print('Modules successfully loaded')

# ATTENSION ------------------------------------------------------------------------------------------------------------
# Before running this script, a database should be created in postgres and the database information entered below, if
# it's not the same. Furthermore, the Project_data folder, scound be placed in the same folder as the scripts
# (main, process, import_to_postgres, postgres_to_shp, postgres_queries and rast_to_vec_grid)
city ='cph'
# Folder structure:
# scripts

# choose processes to run ----------------------------------------------------------------------------------------------
# Initial preparation of Population data ("yes" / "no") csvTOtif

#csv_to_shp
init_csv_to_shp = "no"
#Rasterize shapefiles: shp_to_tif
init_shp_to_tif = "no"
# Check if there are mismatches among the tif folders for socio-demographic variables
create_empty_tif = "no"
#Create Png from tif: tif_to_png
init_tif_to_png= "no"
# Merge tifs by Geographic region for presentation
merge_tifs = "no"

#Merge files of country of origin by 18 geographical regions and then merge them with infrastructure
merge_tifs_trial00 = "no"

#Merge files of country of origin by 18 geographical regions and then merge them with infrastructure, excluding the Country of Interect
merge_tifs_trial01 = "no"

#Merge files of 18 geographical regions with infrastructure
merge_tifs_trial02 = "no"

#Merge files of 18 geographical regions with infrastructure and additional features for buildings by DST 
merge_tifs_trial03 = "yes"

#Path for CPH area
cph_area_path = "K:/FUME/popnet/PoPNetV2/data/cph_area"
# Paths for the Population Data --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path = "K:/FUME/popnet/PoPNetV2/data_scripts/{}_Projectdata/AncillaryData".format(city)
ancillary_POPdata_folder_path = "K:/FUME/popnet/PoPNetV2/data_scripts/{}_Projectdata/PopData".format(city)

parent_path = "K:/FUME/popnet/PoPNetV2"
# Other Paths to necessary python scripts and functions ----------------------------------------------------------------
# path to folder containing gdal_calc.py and gdal_merge.py
python_scripts_folder_path = r'O:/projekter/PY000014_D/popnet_env/Scripts'
#path to folder with gdal_rasterize.exe
gdal_rasterize_path = r'O:/projekter/PY000014_D/popnet_env/Library/bin'

process_data(ancillary_data_folder_path, ancillary_POPdata_folder_path, parent_path, gdal_rasterize_path, init_csv_to_shp, init_shp_to_tif, create_empty_tif, init_tif_to_png, 
                merge_tifs,  merge_tifs_trial01, merge_tifs_trial02,merge_tifs_trial03, cph_area_path, city,python_scripts_folder_path)
