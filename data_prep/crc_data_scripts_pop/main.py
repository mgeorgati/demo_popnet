# Main Script for data preparation -------------------------------------------------------------------------------------
# imports
import os
from process import process_data

print('Modules successfully loaded')

# ATTENSION ------------------------------------------------------------------------------------------------------------
# Before running this script, a database should be created in postgres and the database information entered below, if
# it's not the same. Furthermore, the Project_data folder, scound be placed in the same folder as the scripts
# (main, process, import_to_postgres, postgres_to_shp, postgres_queries and rast_to_vec_grid)
city ='crc'
# Folder structure:
# scripts

# choose processes to run ----------------------------------------------------------------------------------------------
# Initial preparation of Population data ("yes" / "no") csvTOtif

#csv_to_shp
init_csv_to_shp = "no"
#Rasterize shapefiles: shp_to_tif
init_shp_to_tif = "yes"
# Check if there are mismatches among the tif folders for socio-demographic variables
create_empty_tif = "no"
#Create Png from tif: tif_to_png
init_tif_to_png= "no"
# Merge tifs by Geographic region for presentation
sum_tifs = "no"

"""#Merge files of country of origin by 18 geographical regions and then merge them with infrastructure
merge_tifs_trial00 = "no"

#Merge files of country of origin by 18 geographical regions and then merge them with infrastructure, excluding the Country of Interect
merge_tifs_trial01 = "no"

#Merge files of 18 geographical regions with infrastructure
merge_tifs_trial02 = "no"

#Merge files of 18 geographical regions with infrastructure and additional features for buildings by DST 
merge_tifs_trial03 = "no" """


# DIFFERENT PATHS ------------------------------------------------------------------------------------------------------
# Get path to main script
python_script_dir = os.path.dirname(os.path.abspath(__file__))
# Paths for the Population Data --------------------------------------------------------------
parent_path = os.path.dirname(os.path.dirname(python_script_dir))
# Paths for the data / folders in the Project_data folder --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path =  parent_path + "/data_prep/{}_ProjectData/AncillaryData".format(city)
ancillary_POPdata_folder_path = parent_path + "/data_prep/{}_Projectdata/PopData".format(city)
ancillary_EUROdata_folder_path =  parent_path + "/data_prep/euroData"

# Other Paths to necessary python scripts and functions ----------------------------------------------------------------
# path to folder containing gdal_calc.py and gdal_merge.py
python_scripts_folder_path = r'C:/Users/NM12LQ/Anaconda3/Scripts'
#path to folder with gdal_rasterize.exe
gdal_rasterize_path = r'C:/Users/NM12LQ/Anaconda3/Lib/site-packages/osgeo'

process_data(ancillary_data_folder_path, ancillary_POPdata_folder_path, parent_path, gdal_rasterize_path, init_csv_to_shp, init_shp_to_tif, create_empty_tif, init_tif_to_png, 
                sum_tifs,  merge_tifs_trial01, merge_tifs_trial02,merge_tifs_trial03, city,python_scripts_folder_path)
