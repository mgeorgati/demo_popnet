# Main Script for data preparation -------------------------------------------------------------------------------------
# imports
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from variables import base_dir,ancillary_POPdata_folder_path, ancillary_data_folder_path, city, gdal_path, gdal_rasterize_path, python_scripts_folder_path
sys.path.append(gdal_path)

from process import process_data
print('Modules successfully loaded')

# ATTENSION ------------------------------------------------------------------------------------------------------------
# Before running this script, a database should be created in postgres and the database information entered below, if
# it's not the same. Furthermore, the Project_data folder, scound be placed in the same folder as the scripts
# (main, process, csv_to_raster, mergeSelection, normalise) 

# Folder structure:
# scripts

#----------------- ############################# -----------------
# choose processes to run fOR AMS ----------------------------------------------------------------------------------------------
# Initial preparation of Population data ("yes" / "no") csvTOtif

#csv_to_shp --> dataVectorGrid, dataVectorGridSums
init_csv_to_shp = "yes"
#Calculate Percentages --> dataVectorGridDivs
init_calcPercentages = "no"
calcPerc = "no" #Calculate the percentages and store vector data _Divs
rasterizePerc = "no" #Rasterize the percentages in 2folders for Z0 & Z1

#Rasterize shapefiles: shp_to_tif
init_shp_to_tif = "no"

# Normalize columns based on max value in 1992
init_calc_Norm = "no"
#Rasterize Normalized
init_shp_to_tif_Norm = "no"
# Select the countries included in the trial
select_Countries = "no"
#Merge Normalized rasters
merge_tifs_Norm = "no"

# Check if there are mismatches among the tif folders for socio-demographic variables
create_empty_tif = "no"
#Create Png from tif: tif_to_png
init_tif_to_png= "no"
# Merge tifs by Geographic region for presentation
merge_tifs = "no"

process_data(base_dir, ancillary_data_folder_path, ancillary_POPdata_folder_path, gdal_rasterize_path, 
            init_csv_to_shp, init_calcPercentages, calcPerc, rasterizePerc, init_shp_to_tif, create_empty_tif, init_tif_to_png, merge_tifs, 
            init_calc_Norm, init_shp_to_tif_Norm, select_Countries, merge_tifs_Norm, city, python_scripts_folder_path)
