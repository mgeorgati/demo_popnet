# Main Script for data preparation -------------------------------------------------------------------------------------
# imports
import os
from process import process_data

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print('Modules successfully loaded')

# ATTENSION ------------------------------------------------------------------------------------------------------------
# Before running this script, a database should be created in postgres and the database information entered below, if
# it's not the same. Furthermore, the Project_data folder, scound be placed in the same folder as the scripts
# (main, process, import_to_postgres, postgres_to_shp, postgres_queries and rast_to_vec_grid)
city ='ams'
# Folder structure:
# scripts

#----------------- ############################# -----------------
# choose processes to run fOR AMS ----------------------------------------------------------------------------------------------
# Initial preparation of Population data ("yes" / "no") csvTOtif

#csv_to_shp --> dataVectorGrid, dataVectorGridSums
init_csv_to_shp = "no"
#Calculate Percentages --> dataVectorGridDivs
init_calcPercentages= "no"

#Rasterize shapefiles: shp_to_tif
init_shp_to_tif = "no"

# Normalize columns based on max value in 1992
init_calc_Norm = "no"
#Rasterize Normalized
init_shp_to_tif_Norm = "no"
# Select the countries included in the trial
select_Countries = "no"
#Merge Normalized rasters
merge_tifs_Norm = "yes"

# Check if there are mismatches among the tif folders for socio-demographic variables
create_empty_tif = "no"
#Create Png from tif: tif_to_png
init_tif_to_png= "no"
# Merge tifs by Geographic region for presentation
merge_tifs = "no"

#Path for CPH area
cph_area_path = base_dir + "/data/cph_area"
# Paths for the Population Data --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path = base_dir + "/data_prep/{}_Projectdata/AncillaryData".format(city)
ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_Projectdata/PopData".format(city)

# Other Paths to necessary python scripts and functions ----------------------------------------------------------------
# path to folder containing gdal_calc.py and gdal_merge.py
python_scripts_folder_path = r'C:/Users/NM12LQ/Anaconda3/envs/popnet_env/Scripts' #O:/projekter/PY000014_D/popnet_env/Scripts
#path to folder with gdal_rasterize.exe
gdal_rasterize_path = r'C:/Users/NM12LQ/Anaconda3/envs/popnet_env/Library/bin' #O:/projekter/PY000014_D/popnet_env/Library/bin

process_data(base_dir, ancillary_data_folder_path, ancillary_POPdata_folder_path, gdal_rasterize_path, init_csv_to_shp,init_calcPercentages, init_shp_to_tif, create_empty_tif, init_tif_to_png, merge_tifs, 
            init_calc_Norm, init_shp_to_tif_Norm, select_Countries, merge_tifs_Norm, cph_area_path, city, python_scripts_folder_path)
