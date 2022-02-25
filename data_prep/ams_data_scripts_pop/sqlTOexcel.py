# Imports
import os
import pandas as pd
from sqlalchemy import create_engine
import openpyxl
city="ams"
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath("__file__"))))
# Paths for the Population Data --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path = base_dir + "/data_prep/{}_Projectdata/AncillaryData".format(city)
ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_Projectdata/PopData".format(city)

# Instantiate sqlachemy.create_engine object
engine = create_engine('postgresql://postgres:postgres@localhost:5432/fume?gssencmode=disable')
df = pd.read_sql_query('SELECT * FROM unsd',con=engine)

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(ancillary_POPdata_folder_path + "/EXCEL/unsd.xlsx",  index = False,  header=True)

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Sheet1')

# Close the Pandas Excel writer and output the Excel file.
writer.save()


