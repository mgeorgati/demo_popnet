# Main Script for data preparation -------------------------------------------------------------------------------------
# imports
import os
import psycopg2
from sqlalchemy import create_engine
from process import process_data

# ATTENTION ------------------------------------------------------------------------------------------------------------
# Before running this script, a database should be created in postgres and the database information entered below, if
# it's not the same. Furthermore, the Project_data folder, shound be placed in the same folder as the scripts
# (main, process, importDataDB, postgres_to_shp, postgres_queries and rast_to_vec_grid)
country = 'ita'
city= 'rom' #cph


# Folder strudture:
# scripts
# Project_data

# Specify database information -----------------------------------------------------------------------------------------
# path to postgresql bin folder
pgpath = r";C:/Program Files/PostgreSQL/9.5/bin" #changed from 9.5
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
parent_path = os.path.dirname(os.path.dirname(python_script_dir))

# Paths for the data / folders in the Project_data folder --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path =  parent_path + "/data_prep/{}_ProjectData/AncillaryData".format(city)
print(ancillary_data_folder_path )
ancillary_EUROdata_folder_path =  parent_path + "/data_prep/euroData"
# Other Paths to necessary python scripts and functions ----------------------------------------------------------------
# path to folder containing gdal_calc.py and gdal_merge.py
python_scripts_folder_path = r'C:/Users/NM12LQ/Anaconda3/Scripts'
#path to folder with gdal_rasterize.exe
gdal_rasterize_path = r'C:/Users/NM12LQ/Anaconda3/envs/pop_env/Library/bin'

#-------- PROCESS: Create Extensions --------`
initExtensionPostGIS = "no"
initExtensionPGRouting = "no"

#-------- PROCESS: Import Data to Postgres Database --------
initImportProcess = "no"    

#-------- PROCESS: WATER --------
init_waterProcess = "no"
waterProcess00 = "no"
waterProcess01 = "no"

#-------- PROCESS: STREETS --------
init_streetProcess = "no" # This is required before railways and busses to create PGR topology

#-------- PROCESS: BUSES --------
# Creating Isochones for each year for bus stops and counting the accessibility of each cell in grid
init_busProcess = "yes"
busProcess00 = "no"
busProcess01 = "no" 
busProcess02 = "no"
busProcess03 = "yes"

#-------- PROCESS: RAILWAYS --------
# Creating Isochones for each year for train stations and counting the accessibility of each cell  
init_trainProcess = "no" 
trainProcess00 = "no" 
trainProcess01 = "no"
trainProcess02 = "no"
trainProcess03 = "yes"
"""

#-------- PROCESS: SHAPEFILIZE --------
# Save processed data from cover analysis table to SHP
init_psqltoshp = "no" 

#-------- PROCESS: RASTERIZE --------
# Save processed data from SHP to Raster
init_shptoraster = "no" 
"""

# Paths to storage during the data preparation (AUTOMATICALLY CREATED) -------------------------------------------------
#path to folder for intermediate shapefiles 
temp_shp_path = parent_path + "/data_prep/{0}_ProjectData/temp_shp".format(city)
temp_tif_path = parent_path + "/data_prep/{0}_ProjectData/temp_tif".format(city)
temp_tif_corine = parent_path + "/data_prep/{0}_ProjectData/temp_tif/corine".format(city)

process_data(engine, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, ancillary_data_folder_path,ancillary_EUROdata_folder_path,cur,conn, city,country, temp_shp_path, temp_tif_path, temp_tif_corine, python_scripts_folder_path, gdal_rasterize_path,
                    initExtensionPostGIS, initExtensionPGRouting, initImportProcess, 
                    init_waterProcess, waterProcess00, waterProcess01, 
                    init_streetProcess, 
                    init_trainProcess, trainProcess00, trainProcess01, trainProcess02, trainProcess03, #trainProcess04,
                    init_busProcess, busProcess00, busProcess01, busProcess02, busProcess03,
                    #init_psqltoshp ,init_shptoraster
                    ) #init_buildingsProcess, 
