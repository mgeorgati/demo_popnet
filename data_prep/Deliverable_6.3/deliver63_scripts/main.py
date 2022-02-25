# Main Script for data preparation -------------------------------------------------------------------------------------
# imports
import os
import sys
import psycopg2
from sqlalchemy import create_engine

from dataSelection import joinGridToGridNLD, joinGridToGridPL, selectEuroGrid, joinGridToGridIT, movements_processIT

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from variables import (ancillary_EUROdata_folder_path, base_dir, deliver_path,
                       gdal_path)

sys.path.append(gdal_path)

print('Modules successfully loaded')

#-------- GLOBAL ARGUMENTS --------
        
#-------- PROCESS: SELECTION --------

joinGridsNLD = "no"
joinGridsPL = "no"
joinGridsIT = "no"
movementsIT = "yes"
#attr_value = 'children'

def process_data():
    if joinGridsNLD == "yes": 
        year_list= [2010, 2012, 2014, 2016, 2018]
        country = 'NL'
        city ='ams'
        ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_Projectdata/PopData".format(city)
        for year in year_list:
            joinGridToGridNLD(ancillary_POPdata_folder_path,year ,ancillary_EUROdata_folder_path,country, deliver_path)
    if joinGridsPL == "yes": 
        year_list= [2017, 2018, 2019, 2020, 2021]
        country = 'PL'
        city='crc'
        ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_Projectdata/PopData".format(city)
        for year in year_list:
            joinGridToGridPL(ancillary_POPdata_folder_path, year ,ancillary_EUROdata_folder_path,country, deliver_path)
    if joinGridsIT == "yes":
        city = 'rom'
        country='IT'
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
        joinGridToGridIT(ancillary_POPdata_folder_path,ancillary_EUROdata_folder_path, country, deliver_path, cur, conn, engine, year_list)
    if movementsIT == "yes":
        city = 'rom'
        country='IT'
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
        year_list= [2015,2016,2017, 2018]
        ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_Projectdata/PopData".format(city)
        movements_processIT(ancillary_POPdata_folder_path ,ancillary_EUROdata_folder_path, country, deliver_path, cur, conn, engine, year_list)
        
process_data()
