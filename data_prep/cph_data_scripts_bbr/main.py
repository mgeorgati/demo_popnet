# Main Script for data preparation -------------------------------------------------------------------------------------
# imports
import os
import psycopg2
from sqlalchemy import create_engine
from process import process_data

# ATTENTION ------------------------------------------------------------------------------------------------------------
# Before running this script, a database should be created in postgres and the database information entered below, if
# it's not the same. Furthermore, the Project_data folder, shound be placed in the same folder as the scripts
# (main, process, basicFunctions, )
city= 'cph' #cph

# Folder strudture:
# scripts
# Project_data

# Specify database information -----------------------------------------------------------------------------------------
# path to postgresql bin folder
pgpath = r";C:/Program Files/PostgreSQL/9.5/bin"
pghost = 'localhost'
pgport = '5432'
pguser = 'postgres'
pgpassword = 'postgres'
pgdatabase = '{}_data'.format(city)

# Database connections
engine = create_engine(f'postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}?gssencmode=disable')
conn = psycopg2.connect(database=pgdatabase, user=pguser, host=pghost, password=pgpassword,sslmode="disable",gssencmode="disable")
cur = conn.cursor()

# DIFFERENT PATHS ------------------------------------------------------------------------------------------------------
# Get path to main script
python_script_dir = os.path.dirname(os.path.abspath(__file__))
print(python_script_dir)
parent_path = os.path.dirname(os.path.dirname(python_script_dir))

# Paths for the data / folders in the Project_data folder --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path =  parent_path + "/data_prep/{}_ProjectData/AncillaryData".format(city)
bbr_folder_path = ancillary_data_folder_path + "/BBR"
ancillary_EUROdata_folder_path =  parent_path + "/data_prep/euroData"

# Other Paths to necessary python scripts and functions ----------------------------------------------------------------
# path to folder containing gdal_calc.py and gdal_merge.py
python_scripts_folder_path = r'C:/Users/NM12LQ/Anaconda3/Scripts'
#path to folder with gdal_rasterize.exe
gdal_rasterize_path = r'C:/Users/NM12LQ/Anaconda3/Lib/site-packages/osgeo'


#-------- PROCESS: Create Extensions --------`
initExtensionPostGIS = "no"
initExtensionPGRouting = "no"

#-------- PROCESS: Clip Data to Extent --------
initClipBBR = "no"

#-------- PROCESS: BBR DATA --------
# Process BBR data --------------------------------------------------------------------------------------
## ## ## ## ## ----- SCHOOLS  ----- ## ## ## ## ##
process_schools = "no"

clipSchools = "no"
importToDBSchools = "no"
calcIsoSchools = "no"
calcCountIsoSchools = "no"

# Rasterize BBR data --------------------------------------------------------------------------------------
## ## ## ## ## ----- YOU NEED TO SELECT BOTH PROCESS AND TYPE  ----- ## ## ## ## ##
BBRpsqltoshp = "yes" 
BBRrasterize = "yes" 
## ## ## ## ## ----- SCHOOLS  ----- ## ## ## ## ##
BBRtype= "schools" 
"""#HERE


initImportProcess = "no" 

#-------- PROCESS: WATER --------
init_waterProcess = "no"

#-------- PROCESS: STREETS --------
init_streetProcess = "no" # This is required before railways and busses to create PGR topology

#-------- PROCESS: RAILWAYS --------
# Creating Isochones for each year for train stations and counting the accessibility of each cell  
init_trainProcess = "no" 

#-------- PROCESS: BUSES --------
# Creating Isochones for each year for bus stops and counting the accessibility of each cell in grid
init_busProcess = "no"

#-------- PROCESS: SHAPEFILIZE --------
# Save processed data from cover analysis table to SHP
init_psqltoshp = "no" 

#-------- PROCESS: RASTERIZE --------
# Save processed data from SHP to Raster
init_shptoraster = "no" """

# Paths to storage during the data preparation (AUTOMATICALLY CREATED) -------------------------------------------------
#path to folder for intermediate shapefiles 
temp_shp_path = parent_path + "/data_prep/{0}_ProjectData/temp_shp".format(city)
temp_tif_path = parent_path + "/data_prep/{0}_ProjectData/temp_tif".format(city)


process_data(engine, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, cur, conn, city, 
                    python_scripts_folder_path, gdal_rasterize_path,
                    ancillary_data_folder_path, ancillary_EUROdata_folder_path, temp_shp_path, temp_tif_path, bbr_folder_path,
                    initExtensionPostGIS, initExtensionPGRouting, initClipBBR,
                    process_schools, clipSchools, importToDBSchools, calcIsoSchools, calcCountIsoSchools,
                    BBRpsqltoshp, BBRrasterize , BBRtype )
