import os
import sys
import subprocess
import geopandas as gpd
import matplotlib.pyplot as plt
import PIL
cur_path = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(cur_path))))
city = 'cph'
print(base_dir)
from flowStudy_Functions import calc_shares, shptoraster, createSognMean, plotSognMean,  createGif, calc_cor
sys.path.append(base_dir + "/data_prep/{}_data_scripts_pop".format(city))
from csv_to_raster import createFolder
#path to folder with gdal_rasterize.exe
gdal_rasterize_path = r'O:/projekter/PY000014_D/popnet_env/Library/bin'

ancillary_data_folder_path = base_dir + "/data_prep/{}_ProjectData/AncillaryData".format(city)
ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_ProjectData/PopData".format(city)
years_list= [ 1990, 2000,  2010,  2018] # 1990, 1992, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016,

# Z0: Share of Migrant group Per total Population : select : share =  'Z0', divisor =  df['l1_sum_population']
# Z1: Share of Migrant group Per total Migration  : select : share =  'Z1', divisor =  df['totalMig'] 
# Z1: Share of Migrant group Per notEU Migration  : select : share =  'Z2', divisor =  (df['totalMig'] - df['EuropeEU']) 
share =  'Z3' #'Z0', 'Z1',
select = ['gc100m','geometry','l1_sum_population', 'EuropeEU', 'dnk', 'totalMig'] #'tur', 'pak', 'irq', 'ind', 'irn', 'lbn', 'chn', 'phl', 'afg', 'tha', 'syr', 'npl', 'som', 'mar', 'gha'
#group = ['tur', 'pak', 'irq', 'ind', 'irn', 'lbn', 'chn', 'phl', 'afg', 'tha', 'syr', 'npl', 'som', 'mar', 'gha' ] 
group = ['migoutEU'] # >>>> for z3 <<<<

districtsPath = base_dir + "/data_prep/{}_ProjectData/AncillaryData/CaseStudy/sogns.geojson".format(city)
districts = gpd.read_file(districtsPath)

cph = base_dir + "/data_prep/cph_ProjectData/AncillaryData/CaseStudy/sogns.geojson"
regions = base_dir + "/data_prep/cph_ProjectData/AncillaryData/CaseStudy/regioner.gpkg"

cph_area = gpd.read_file(cph)
regioner = gpd.read_file(regions)

# Calculate shares in geojson
calc_shares_fun = 'yes'
rasterize = 'yes'
calcMean = 'yes'
plotMap = 'no'
plotMatrix = 'no'
plotGif = 'no'
correlation = 'no'
plotMatrixCor = 'no'

if calc_shares_fun == 'yes':
    for year in years_list:
        src_file= ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridSums.geojson".format(year)
        gjson_file = cur_path + "/{}/gjson".format(share)
        createFolder(gjson_file)
        calc_shares(group, select, share, src_file, gjson_file, year)

if rasterize =='yes':
    gjson_file = cur_path + "/{}/gjson/".format(share)
    for file in os.listdir(gjson_file):
        year = file.split('_')[0]
        src_file = gjson_file + file
        dst_path = cur_path + "/{}/tif/".format(share)
        createFolder(dst_path)
        shptoraster(ancillary_data_folder_path, cur_path, src_file, dst_path, share, gdal_rasterize_path, city, year)

if calcMean=='yes':
    tif_file = cur_path + "/{}/tif/".format(share)
    for file in os.listdir(tif_file):
        year = file.split('_')[0]
        name= file.split('.tif')[0].split('{0}_{1}_'.format(year,share))[1]
        print(name)
        src_file = tif_file + file
        dst_path = cur_path + "/{}/sogn_gjson/".format(share)
        createFolder(dst_path)
        createSognMean(src_file, dst_path + "{}_{}.geojson".format(year,name), name, districts)

if plotMap == 'yes':
    sogn_gjson_file =  cur_path + "/{}/sogn_gjson/".format(share)
    for file in os.listdir(sogn_gjson_file):
        year = file.split('_')[0]
        area = file.split('.geojson')[0].split('{0}_'.format(year))[1]
        print(area)
        print("Plotting Map for {1}, {0}".format(year,area))
        src_path = sogn_gjson_file + file
        destImage_path = cur_path + "/{0}/sognMean_img/{1}".format(share, area)
        createFolder(destImage_path)
        image_path = destImage_path + "/{0}_{2}_{1}.png".format(year,area,share)
        if share== 'Z0':
            title = "Mean Share of {1} Per Total Population % ({0})".format(year,area)
        elif share== 'Z1':
            title = "Mean Share of {1} Per Total Migration % ({0})".format(year,area)
        elif share == 'Z2':
            title = "Mean Share of {1} Per not-EU Migration % ({0})".format(year,area)
        plotSognMean(year, src_path, title, image_path, area, cph_area, regioner,share)

if plotMatrix == 'yes':
    years = [1990, 1996, 2002, 2008, 2014, 2018]
    rows = 2
    cols = 3
    path_list =[]
    
    for area in group:
        for year in years:
            path = cur_path + "/{0}/sognMean_img/{1}/".format(share, area) + '{0}_{1}_{2}.png'.format(year, share, area)
            path_list.append(path)
        #print(path_list)
        fig, axs = plt.subplots(rows, cols, figsize=(20,10))
        fig.subplots_adjust(hspace = .05, wspace=.01)
        axs = axs.ravel()
        #print(path_list)
        for num, x in enumerate(path_list):
            print(num,x)
            img = PIL.Image.open(x)
            plt.subplot(rows, cols, num+1)
            plt.axis('off')
            plt.imshow(img)
        dest_path = cur_path + "/{0}/matrix_img".format(share)
        createFolder(dest_path)
        if share== 'Z0':
            genTitle = "Mean Share of {0} Per Total Population (%)".format(area)
        elif share== 'Z1':
            genTitle = "Mean Share of {0} Per Total Migration (%)".format(area)
        elif share == 'Z2':
            genTitle = "Mean Share of {0} Per not-EU Migration (%)".format(area)
        
        fig.suptitle("{0}".format(genTitle))
        plt.savefig(dest_path + '/{0}_{1}.png'.format(share, area), dpi=300, bbox_inches='tight',transparent=True)
        
        fig.clf()
        path_list.clear()
         
if plotGif == 'yes': 
    dest_path = cur_path + "/{0}/sognMean_gif".format(share)
    createFolder(dest_path)
    for area in group:
        src_path = cur_path + "/{0}/sognMean_img/{1}/".format(share, area) 
        createGif(src_path, dest_path, area) 

if correlation =='yes':
    for year in years_list:
        src_file= ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridSums.geojson".format(year)
        dest_path = cur_path + "/{0}/corr_grid".format(share)
        createFolder(dest_path)
        calc_cor(src_file, group, year, dest_path)   

if plotMatrixCor == 'yes':
    years = [1990, 1996, 2002, 2008, 2014, 2018]
    rows = 2
    cols = 3
    path_list =[]
    
    for year in years:
        path = cur_path + "/{0}/corr_grid/".format(share) + '{0}_corMatrix.png'.format(year)
        path_list.append(path)
    #print(path_list)
    fig, axs = plt.subplots(rows, cols, figsize=(20,10))
    fig.subplots_adjust(hspace = .05, wspace=.01)
    axs = axs.ravel()
    #print(path_list)
    for num, x in enumerate(path_list):
        print(num,x)
        img = PIL.Image.open(x)
        plt.subplot(rows, cols, num+1)
        plt.axis('off')
        plt.imshow(img)
    dest_path = cur_path + "/{0}/corr_grid/".format(share)
    createFolder(dest_path)
    
    genTitle = "Correlations"
    
    fig.suptitle("{0}".format(genTitle))
    plt.savefig(dest_path + '/corr.png', dpi=300, bbox_inches='tight',transparent=True)
    
    fig.clf()
    path_list.clear()   
