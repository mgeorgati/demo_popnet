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
init_csv_to_shp = "yes"
init_csv_to_shp_MUW = "NO"



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
python_scripts_folder_path = r'C:/Users/NM12LQ/Anaconda3/envs/pop_env/Scripts'
#path to folder with gdal_rasterize.exe
gdal_rasterize_path = r'C:/Users/NM12LQ/Anaconda3/envs/pop_env/Library/bin'

process_data(ancillary_data_folder_path, ancillary_POPdata_folder_path, parent_path, gdal_rasterize_path, init_csv_to_shp, init_csv_to_shp_MUW,  city,python_scripts_folder_path)
