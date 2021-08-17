import os
import subprocess
import pandas as pd
import geopandas as gpd
import gdal
import xlrd
import openpyxl
from shapely.wkt import loads
import numpy as np

## ## ## ## ## ----- CREATE NEW FOLDER  ----- ## ## ## ## ##
def createFolder(path):
    if not os.path.exists(path):
        print("------------------------------ Creating Folder : {} ------------------------------".format(path))
        os.makedirs(path)
    else: 
        print("------------------------------ Folder already exists------------------------------")

def csvtoshp(ancillary_POPdata_folder_path,ancillary_data_folder_path,year, dictionary):
    pathI = ancillary_POPdata_folder_path + "/process02/{}.xlsx".format(year)
    dfI = pd.read_excel(pathI, header=0)
    print(dfI.head())
    ndf = dfI.iloc[: , 1:] #
    ndf.columns= ndf.columns.str.lower()
    ndf.columns= [col.replace('l10_', '') for col in ndf.columns]
    ndf.columns= [x.replace('l40_', '') for x in ndf.columns]
    print(ndf.head(2))
    keyList=[]

    for key in dictionary:
        keyList.append(key)
        selectList = dictionary['{}'.format(key)]
        print(key, selectList)
        select = [x for x in ndf if x in selectList]
        print(select)
        ndf['{}'.format(key)] = ndf.loc[:, select].sum(axis=1)
        ndf['{}'.format(key)].astype(int)
        print(ndf['{}'.format(key)].sum())
    
    extraColumns= ['grid_id','grid_geometry_epsg3035', 'l1_totalpop','l2_children',	'l3_students',	'l4_mobile_adults',	'l5_not_mobile_adults',	'l6_elderly',
    'l7_immigrants', 'l8_eu_immigrants', 'l9_noneu_immigrants','l11_births','l12_deaths','l14a_people_who_moved_out_of_grid',
    'l14b_immigrants_into_netherlands',	'l15a_ people_who_moved_into_grid',	'l15b_immigrants_outof_netherlands','l16_verhuis_in_ams_outof',	
    'l17_verhuis_in_ams_into', 'l21_not_used_dwellings','l22_let_out_dwellings','l23_privately_owned_dwellings','l25_total_area_of_residence',	
    'l26_number_of_dwellings','l27_number_of_rooms']
    keyList.extend(extraColumns)
    
    ndf['totalMig']= ndf['l1_totalpop']-ndf['nld']
    print(keyList)
    print("------------------------------ Creating xlsx:{0} ------------------------------".format(year))
    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(ancillary_POPdata_folder_path + "/{0}/{0}.xlsx".format(year),  index = False, header=True)
    # Convert the dataframe to an XlsxWriter Excel object.
    ndf.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    
    # Create geopandas for large dataframe with all cleaned attributes 
    gdfXXL= gpd.GeoDataFrame(ndf, geometry=ndf['grid_geometry_epsg3035'].apply(loads), crs='epsg:3035')
    print("------------------------------ Creating shapefile:{0} on VectorGrid------------------------------".format(year))
    gdfXXL.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.geojson".format(year),driver='GeoJSON',crs="EPSG:3035")
    
    keyList.append('totalMig')
    # CREATE DATAFRAME WITH SELECTION OF COLUMNS FOR SUM AND GENERAL DATA
    sumByRegionDF= [x for x in ndf if x in keyList]
    ndfL = ndf.loc[:, sumByRegionDF]
    print(ndfL)
    
    # CONVERT IT TO GEODATAFRAME AND SAVE IT IN GEOJSON
    gdfL = gpd.GeoDataFrame(ndfL, geometry=ndfL['grid_geometry_epsg3035'].apply(loads), crs='epsg:3035')
    print("------------------------------ Creating shapefile:{0} on VectorGridSums ------------------------------".format(year)) 
    gdfL.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridSums.geojson".format(year),driver='GeoJSON',crs="EPSG:3035")

def calc_Perc(ancillary_POPdata_folder_path, city,year):

    df = gpd.read_file(ancillary_POPdata_folder_path + '/{0}/temp_shp/{0}_dataVectorGrid.geojson'.format(year))
    selectedColumns = df[['grid_id','geometry','l1_totalpop','totalMig','nld', 'l2_children',	'l3_students',	'l4_mobile_adults',	'l5_not_mobile_adults',	'l6_elderly',
    'l7_immigrants', 'l8_eu_immigrants', 'l9_noneu_immigrants','l11_births','l12_deaths','l14a_people_who_moved_out_of_grid',
    'l14b_immigrants_into_netherlands',	'l15a_ people_who_moved_into_grid',	'l15b_immigrants_outof_netherlands','l16_verhuis_in_ams_outof',	
    'l17_verhuis_in_ams_into', 'l21_not_used_dwellings','l22_let_out_dwellings','l23_privately_owned_dwellings','l25_total_area_of_residence',	
    'l26_number_of_dwellings','l27_number_of_rooms', 'Oceania', 'EuropeNotEU', 'EuropeEUnoLocal',  'Central_Asia', 'Eastern_Asia', 'Southern-Eastern_Asia', 'Southern_Asia', 
                'Western_Asia', 'Northern_America', 'Latin_America_and_the_Caribbean', 'Northern_Africa', 'Sub-Saharan_Africa', 'Others', 'Colonies']]
    frame = selectedColumns.copy()
    #Remove the standard columns from the unique Attributes and write file
    select = ['totalMig', 'Oceania', 'EuropeNotEU', 'EuropeEUnoLocal',  'Central_Asia', 'Eastern_Asia', 'Southern-Eastern_Asia', 'Southern_Asia', 
                'Western_Asia', 'Northern_America', 'Latin_America_and_the_Caribbean', 'Northern_Africa', 'Sub-Saharan_Africa', 'Others', 'Colonies']

    for i in select:
        # Calculate percentage of each migrant group per total population
        frame['Z0_{}'.format(i)] = (df['{}'.format(i)]/df['l1_totalpop'])*100 #totalPop
        
        # Calculate percentage of each migrant group per total migration
        frame['Z1_{}'.format(i)] = (df['{}'.format(i)]/df['totalMig'])*100 #totalMig
    
    frame.drop('Z1_totalMig', axis=1, inplace=True)
    frame.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridDivs.geojson".format(year),driver='GeoJSON',crs="EPSG:3035")

def shptoraster(ancillary_POPdata_folder_path,ancillary_data_folder_path, gdal_rasterize_path, city, year, dictionary):
    ## ## ## ## ## ----- Getting extent of corine raster ----- ## ## ## ## ##  
    data = gdal.Open(os.path.dirname(ancillary_data_folder_path) + "/temp_tif/{0}_CLC_2012_2018.tif".format(city))
    wkt = data.GetProjection()
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None
    xres=100
    yres=100

    ## ## ## ## ## ----- Rasterize files ----- ## ## ## ## ##
    src_file = ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridSums.geojson".format(year)
    df = gpd.read_file(src_file, crs="EPSG:3035")
    disselect =["grid_geometry_epsg3035", "grid_id", "geometry"]
    df_select = [x for x in df if not x in disselect]
    ndf = df.loc[:, df_select]

    countriesList = list()
    for key in dictionary:
        countriesList.extend(list(dictionary[key]))
    #print(countriesList)

    selectList = list()
    for i in dictionary.keys():
        selectList.append(i)
    selectList.append("totalMig")

    ## ## ## ## ## ----- Creating Necessary Folders ----- ## ## ## ## ##
    
    dst_path_Countries = ancillary_POPdata_folder_path + "/{0}/temp_tif/countries".format(year)
    createFolder(dst_path_Countries)
    dst_path_Demographic = ancillary_POPdata_folder_path + "/{0}/temp_tif/demo".format(year)
    createFolder(dst_path_Demographic)

    emptryRasters=list()
    ## ## ## ## ## ----- Rasterize files ----- ## ## ## ## ##
    for column_name in ndf: 
        
        """if ndf["{}".format(column_name)].sum(axis=0) == 0:
            print("----- No Raster created for : {} -----".format(column_name))
            emptryRasters.append(column_name)
        """ 
        if column_name in selectList: 
            dst_path_Regions = os.path.dirname(ancillary_POPdata_folder_path) + "/GeogrGroups/{0}".format(column_name)
            createFolder(dst_path_Regions)
            print("Rasterizing in GeogrGroups: {} layer".format(column_name))
            dst_file = dst_path_Regions + "/{0}_{1}.tif".format(year, column_name)
            cmd = '{0}/gdal_rasterize.exe -a "{9}" -te {1} {2} {3} {4} -tr {5} {6} {7} "{8}"'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
            subprocess.call(cmd, shell=True)
        
        elif column_name == 'nld': 
            print("Rasterizing in Countries: {} layer".format(column_name))
            dst_file = dst_path_Countries + "/{0}_{1}.tif".format(year, column_name)
            cmd = '{0}/gdal_rasterize.exe -a "{9}" -te {1} {2} {3} {4} -tr {5} {6} {7} "{8}"'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
            subprocess.call(cmd, shell=True)

        elif column_name in countriesList: 
            print("Rasterizing in Countries: {} layer".format(column_name))
            dst_file = dst_path_Countries + "/{0}_{1}.tif".format(year, column_name)
            cmd = '{0}/gdal_rasterize.exe -a "{9}" -te {1} {2} {3} {4} -tr {5} {6} {7} "{8}"'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
            #subprocess.call(cmd, shell=True)

        else : 
            print("Rasterizing in Demographic: {} layer".format(column_name))
            dst_file = dst_path_Demographic + "/{0}_{1}.tif".format(year, column_name)
            cmd = '{0}/gdal_rasterize.exe -a "{9}" -te {1} {2} {3} {4} -tr {5} {6} {7} "{8}"'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
            subprocess.call(cmd, shell=True)

    dst_path_Empty = os.path.dirname(ancillary_POPdata_folder_path) + "/emptyRaster"
    createFolder(dst_path_Empty)    
    #Create txt file with number of band --> Name of File
    f = open(dst_path_Empty + "/{}_emptyRasters.txt".format(year), "w+")
    str_files = " ".join(["{}".format(emptryRasters[i]) for i in range(len(emptryRasters))])
    for i,each in enumerate(emptryRasters,start=1):
        f.write("{1}.{2}".format(year, i,each) + "\n")
    f.close()

"""
def shptoraster(ancillary_POPdata_folder_path,ancillary_data_folder_path, gdal_rasterize_path, city,year):
    # Getting extent of ghs pop raster
    data = gdal.Open(os.path.dirname(ancillary_data_folder_path) + "/temp_tif/{0}_CLC_2012_2018.tif".format(city))
    wkt = data.GetProjection()
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None
    xres=100
    yres=100
    # Rasterizing layers
    src_file = ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridDivs.geojson".format(year)
    df = gpd.read_file(src_file)
    
    for column_name in df.columns:
        if column_name.startswith('Z0_') or  column_name.startswith('Z1_'):
            print("Rasterizing {} layer".format(column_name))
            dst_file = ancillary_POPdata_folder_path + "/{0}/temp_tifPercentages/{0}_{1}.tif".format(year, column_name)
            cmd = '{0}/gdal_rasterize.exe -a {9} -te {1} {2} {3} {4} -tr {5} {6} "{7}" "{8}"'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
            print(cmd) #-ot Integer64
            subprocess.call(cmd, shell=True)"""
        

