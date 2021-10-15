import os 
import imageio
from pathlib import Path
import zipfile
import psycopg2
from sqlalchemy import create_engine

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
city ='rom'
# Paths for the Population Data --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path = base_dir + "/data_prep/{}_ProjectData/AncillaryData".format(city)
ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_ProjectData/PopData".format(city)

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

# Other Paths to necessary python scripts and functions ----------------------------------------------------------------
# path to folder containing gdal_calc.py and gdal_merge.py
python_scripts_folder_path = r'C:/Users/NM12LQ/Anaconda3/envs/popnet_env/Scripts' #O:/projekter/PY000014_D/popnet_env/Scripts
#path to folder with gdal_rasterize.exe
gdal_path = r'C:/Users/NM12LQ/Anaconda3/envs/popnet_env/Library/bin' #O:/projekter/PY000014_D/popnet_env/Library/bin

## ## ## ## ## ----- CREATE NEW FOLDER  ----- ## ## ## ## ##
def createFolder(path):
    if not os.path.exists(path):
        print("------------------------------ Creating Folder : {} ------------------------------".format(path))
        os.makedirs(path)
    else: 
        print("------------------------------ Folder already exists------------------------------")

## ## ## ## ## ----- Unzip Folder  ----- ## ## ## ## ##
def unzip(path_to_zip_file, directory_to_extract_to, folderName):
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to + "/{}".format(folderName))

def createGIFs(src_path, export_path, fileName):
    filePaths=[]
    for file in os.listdir(src_path):
        if file.endswith('.png'):
            filePath = Path(src_path + "/" + file)
            filePaths.append(filePath)
    print(filePaths)
    images = []
    for i in filePaths:
        images.append(imageio.imread(i))
    imageio.mimsave(export_path + '/{}.gif'.format(fileName), images, fps=24, duration=1)