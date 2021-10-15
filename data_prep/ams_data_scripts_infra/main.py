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
CNTR_CODE =  "NL"
city= 'ams' #cph
country = "nl" #DK
nuts3_cd1= 'NL329' # NL329

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
gdal_rasterize_path = r'C:/Users/NM12LQ/Anaconda3/Lib/site-packages/osgeo'

#-------- PROCESS: Create Extensions --------`
initExtensionPostGIS = "no"
initExtensionPGRouting = "no"

#-------- PROCESS: Import Data to Postgres Database --------
initImports = "no"
initImportProcess = "no"    

#-------- PROCESS: WATER --------
init_waterProcess = "no"
waterProcess00 = "no"
waterProcess01 = "no"
waterProcess02 = "no"

#-------- PROCESS: STREETS --------
init_streetProcess = "no" # This is required before railways and busses to create PGR topology

#-------- PROCESS: RAILWAYS --------
# Creating Isochones for each year for train stations and counting the accessibility of each cell  
init_tramProcess = "yes" 
tramProcess00 = "no" 
tramProcess01 = "no"
tramProcess02 = "no"
tramProcess03 = "no"
tramProcess04 = "yes"

#-------- PROCESS: BUSES --------
# Creating Isochones for each year for bus stops and counting the accessibility of each cell in grid
init_busProcess = "no"
busProcess00 = "no"
busProcess01 = "no" 
busProcess02 = "no" 
busProcess03 = "yes" 

#-------- PROCESS: SHAPEFILIZE --------
# Save processed data from cover analysis table to SHP
init_psqltoshp = "no" 

#-------- PROCESS: RASTERIZE --------
# Save processed data from SHP to Raster
init_shptoraster = "no" 

# choose processes to run ----------------------------------------------------------------------------------------------
# Initial preparation of Population data ("yes" / "no") csvTOdbTOshpTOtif
init_prep = "no"
#Import data to postgres? ("yes" / "no")
init_import_to_postgres = "no"
# Run postgres queries? ("yes" / "no")
restructure_tables_sql = "no"
# export data from postgres? ("yes" / "no")
init_export_data = "no"
# rasterize data from postgres? ("yes" / "no")
init_rasterize_data = "no"
# Merge data from postgres? ("yes" / "no")
#init_merge_data = "no"

# Merge data by sub_region_name and by year ("yes" / "no")
merge_data_subregion = "no"

# Paths to storage during the data preparation (AUTOMATICALLY CREATED) -------------------------------------------------
#path to folder for intermediate shapefiles 
temp_shp_path = parent_path + "/data_prep/{0}_ProjectData/temp_shp".format(city)
temp_tif_path = parent_path + "/data_prep/{0}_ProjectData/temp_tif".format(city)
temp_tif_corine = parent_path + "/data_prep/{0}_ProjectData/temp_tif/corine".format(city)

process_data(engine, pgpath, pghost, pgport, pguser, pgpassword, pgdatabase, ancillary_data_folder_path,ancillary_EUROdata_folder_path,cur,conn, city,country,nuts3_cd1, temp_shp_path, temp_tif_path, temp_tif_corine, python_scripts_folder_path, gdal_rasterize_path,
                    initExtensionPostGIS, initExtensionPGRouting,initImports, initImportProcess, 
                    init_waterProcess, waterProcess00, waterProcess01, waterProcess02, 
                    init_streetProcess, 
                    init_tramProcess, tramProcess00, tramProcess01, tramProcess02, tramProcess03, tramProcess04,
                    init_busProcess, busProcess00, busProcess01, busProcess02, busProcess03,
                    init_psqltoshp ,init_shptoraster) #init_buildingsProcess, 
