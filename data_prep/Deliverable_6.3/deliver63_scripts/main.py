# Main Script for data preparation -------------------------------------------------------------------------------------
# imports
import os
import sys
from tkinter.tix import Select
import psycopg2
from sqlalchemy import create_engine

from dataSelection import selectEuroGrid
from dataSelectionDK import joinGridToGridDK, zonalStat
from dataSelectionICCSA import joinGridToGridDKICCSA
from dataSelectionIT import joinGridToGridIT, movements_processIT
from dataSelectionNL import joinGridToGridNL
from dataSelectionPL import joinGridToGridPL
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from variables import (ancillary_EUROdata_folder_path, base_dir, deliver_path,
                       gdal_path)

sys.path.append(gdal_path)

print('Modules successfully loaded')

#-------- GLOBAL ARGUMENTS --------
country = "DK"       
#-------- PROCESS: SELECTION --------
selectGrid = "no"
joinGrids = "no"
zonal_Stat = "no"
movementsIT = "yes"


def process_data():
    if selectGrid == "yes":
        selectEuroGrid(ancillary_EUROdata_folder_path, country, nutsArea)
    if country == "DK":
        year_list= [ 1990, 1992, 1994, 1996, 1998,2000, 2002,2004,2006, 2008,2010,2012, 2014,2016, 2018]
        if joinGrids == "yes":         
            for year in year_list:
                #joinGridToGridDK(ancillary_POPdata_folder_path,year ,ancillary_EUROdata_folder_path,country, deliver_path)
                joinGridToGridDKICCSA(ancillary_POPdata_folder_path,year, ancillary_EUROdata_folder_path, country, deliver_path)
        if zonal_Stat == "yes": 
            country = 'DK'
            polyPath = ancillary_EUROdata_folder_path + "/euroGrid/grid_1km_{}.gpkg".format(country) 
            statistics = 'mean'
            for year in year_list:
                src_file = ancillary_data_folder_path + "/temp_tif/{}_cph_busstopscount.tif".format(year) #busstopscount, stationcount
                dst_file = deliver_path + "/{1}/SpatialLayers/{0}_busstops.geojson".format(year,country)
                zonalStat(src_file, dst_file, polyPath, statistics)
                gridL = gpd.read_file(deliver_path + "/{1}/SpatialLayers/{0}_busstops.geojson".format(year,country))
                gridL = gridL[['geometry', 'GRD_ID','mean_']]
                gridL = gridL.rename(columns={'mean_':'trainst'})
                gridL.to_csv(deliver_path + "/{1}/SpatialLayers/{0}_busstops.csv".format(year,country), sep=';')
        
    if country == "NL": 
        if joinGrids == "yes": 
            year_list= [2010, 2012, 2014, 2016, 2018]
            country = 'NL'
            city ='ams'
            ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_Projectdata/PopData".format(city)
            for year in year_list:
                joinGridToGridNL(ancillary_POPdata_folder_path,year ,ancillary_EUROdata_folder_path,country, deliver_path)
    if country == "PL": 
        if joinGrids == "yes": 
            year_list= [2017, 2018, 2019, 2020, 2021]
            country = 'PL'
            city='crc'
            ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_Projectdata/PopData".format(city)
            for year in year_list:
                joinGridToGridPL(ancillary_POPdata_folder_path, year ,ancillary_EUROdata_folder_path,country, deliver_path)
    if country == "IT": 
        city = 'rom'
        # Specify database information -----------------------------------------------------------------------------------------
        # path to postgresql bin folder
        pgpath = r";C:/Program Files/PostgreSQL/9.5/bin"
        pghost = 'localhost'
        pgport = '5432'
        pguser = 'postgres'
        pgpassword = 'postgres'
        pgdatabase = '{}_data'.format(city)
        engine = create_engine(f'postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}?gssencmode=disable')
        conn = psycopg2.connect(database=pgdatabase, user=pguser, host=pghost, password=pgpassword,sslmode="disable",gssencmode="disable")
        cur = conn.cursor()
        
        year_list= [2016,2017,2018, 2019, 2020]
        ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_Projectdata/PopData".format(city)
        
        if joinGrids == "yes":            
            joinGridToGridIT(ancillary_POPdata_folder_path,ancillary_EUROdata_folder_path, country, deliver_path, cur, conn, engine, year_list)
        if movementsIT == "yes":
            movements_processIT(ancillary_POPdata_folder_path ,ancillary_EUROdata_folder_path, country, deliver_path, cur, conn, engine, year_list)
        
process_data()
