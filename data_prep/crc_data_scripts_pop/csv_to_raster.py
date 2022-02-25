import os
import subprocess
import pandas as pd
import geopandas as gpd
from osgeo import gdal
import xlrd
from shapely.wkt import loads
import glob
from pathlib import Path

def non_match_elements(list_a, list_b):
    non_match = []
    for i in list_a:
        if i not in list_b:
            non_match.append(i)
    return non_match

def csvtoshp(ancillary_POPdata_folder_path,ancillary_data_folder_path,city, year, dictionary):
    path = ancillary_POPdata_folder_path + "/rawData" # use your path
    """a=[]
    for i in dictionary.keys():
        values = dictionary[i]
        for x in values:
            a.append(x)
    
    print(a)
    frame = pd.read_csv(path + "/Population by citizenship/FUME_KRAKOW_POP_{}.csv".format(year))
    b = [i.lower() for i in frame.columns.to_list()]
    print(b)
    print('unmatch', non_match_elements(b, a))
    #Combine all the csv files in one shp for points and another one for polygons with the vector grid            
    """
    
    listOfFiles = glob.glob(path + "/*/*_{}.csv".format(year))
    
    polys = gpd.read_file(os.path.dirname(ancillary_data_folder_path) + "/temp_shp/{0}_grid.shp".format(city), crs="EPSG:3035")
    polys = polys.set_crs("EPSG:3035")
    
    frame = pd.read_csv(path + "/Age structure/FUME_KRAKOW_Age_{}.csv".format(year))
    frame = frame.set_index('Eurogrid')
    for i in listOfFiles:
        file = Path(i)
        filename = file.stem 
        name = filename.split('FUME_KRAKOW_')[1].split('_{}'.format(year))[0]
        if name!= 'POP' and name!='Age':
            df = pd.read_csv(i)
            nameColumn = df.columns[1]
            df = df.rename(columns={'{}'.format(nameColumn):'{}'.format(name)})
            frame = frame.join(df.set_index('Eurogrid'), on='Eurogrid', lsuffix='_l')
        elif name =='Age':
            df = pd.read_csv(i)
            df = df.rename(columns={'X0.19':'children', 'X20.29':'yadults', 'X30.44':'mobadults', 'X45.64':'nmobadults', 'X65.':'elderly', 'Total':'totalpop'})
            frame = frame.join(df.set_index('Eurogrid'), on='Eurogrid', lsuffix='_l')
        elif name == 'POP':
            df = pd.read_csv(i)
            frame = frame.join(df.set_index('Eurogrid'), on='Eurogrid', lsuffix='_l')
    print(frame.head(2))  
    frame.reset_index(inplace=True)
    frame = frame.rename(columns = {'index':'Eurogrid'})
    #split the Grid column to x,y coordinates and make geometry    
    y=frame['Eurogrid'].str.split('N', 1).str[0]
    x=frame['Eurogrid'].str.split('N', 1).str[1].str.split('E', 1).str[0]
    frame['y'] = y.astype(int)
    frame['x'] = x.astype(int)
    print(frame.head(5))
    gdf_points = gpd.GeoDataFrame(
            frame, geometry=gpd.points_from_xy(frame['x'], frame['y']), crs='epsg:3035')
    gdf_points.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorPoints.geojson".format(year), driver='GeoJSON', crs='EPSG:3035')
    
    polys = gpd.read_file(os.path.dirname(ancillary_data_folder_path) + "/temp_shp/{0}_grid.shp".format(city), crs="EPSG:3035")
    #gdf_points=  gpd.read_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorPoints.geojson".format(year), crs="EPSG:3035")
    
    gdf_joined = gpd.sjoin(gdf_points, polys, how='left', op='within') # Here I am using intersects with left join
    print(gdf_joined.head(5))
    #remove the point geometry and add the polygon geometry
    gdf = gdf_joined.loc[:, gdf_joined.columns != 'geometry']
    print(gdf.head(5))
    gdf_merged = gdf.merge(polys, how='inner', on='FID')
    
    for col in gdf_merged.columns:
        gdf_merged = gdf_merged.rename(columns={'{}'.format(col):'{}'.format(col.lower())})
    keyList=[]
    for key in dictionary:
        keyList.append(key)
        selectList = dictionary['{}'.format(key)]
        print(key, selectList) 
        select = [x for x in gdf_merged if x in selectList]
        print(select)
        gdf_merged['{}'.format(key)] = gdf_merged.loc[:, select].sum(axis=1)
        gdf_merged['{}'.format(key)].astype(int)
        print(gdf_merged['{}'.format(key)].sum())
    
    gdf_merged['immigrants'] = gdf_merged['totalpop'] - gdf_merged['pol']
    gdf_merged['immigrants'].astype(int)
    gdf_merged['noneu_immigrants']= gdf_merged['immigrants'] - gdf_merged['EU']
    

    #save shapefiles to folder
    print("------------------------------ Creating shapefile:{0} on Vector Grid------------------------------".format(year)) 
    gdf_merged.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.geojson".format(year), driver='GeoJSON', crs='EPSG:3035')
    #save shapefiles to folder
    #print("------------------------------ Creating shapefile:{0} on Points------------------------------".format(year)) 
    #gdf_points.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataPoints.shp".format(year))

def csvtoshpMUW(ancillary_POPdata_folder_path,ancillary_data_folder_path,city, year, dictionary):
    path = ancillary_POPdata_folder_path + "/rawData" # use your path
    
    frame = pd.read_csv(path + "/MUW_Immigrants/FUME_MUW_KRAKOW_{}.csv".format(year))
    frame = frame.set_index('Eurogrid')
   
    print(frame.head(2))  
    frame.reset_index(inplace=True)
    frame = frame.rename(columns = {'index':'Eurogrid'})
    #split the Grid column to x,y coordinates and make geometry    
    y=frame['Eurogrid'].str.split('N', 1).str[0]
    x=frame['Eurogrid'].str.split('N', 1).str[1].str.split('E', 1).str[0]
    frame['y'] = y.astype(int)
    frame['x'] = x.astype(int)
    print(frame.head(5))
    gdf_points = gpd.GeoDataFrame(
            frame, geometry=gpd.points_from_xy(frame['x'], frame['y']), crs='epsg:3035')
    gdf_points.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorPoints_MUW.geojson".format(year), driver='GeoJSON', crs='EPSG:3035')
    
    polys = gpd.read_file(os.path.dirname(ancillary_data_folder_path) + "/temp_shp/{0}_grid.shp".format(city), crs="EPSG:3035")
    #gdf_points=  gpd.read_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorPoints.geojson".format(year), crs="EPSG:3035")
    
    gdf_joined = gpd.sjoin(gdf_points, polys, how='left', op='within') # Here I am using intersects with left join
    print(gdf_joined.head(5))
    #remove the point geometry and add the polygon geometry
    gdf = gdf_joined.loc[:, gdf_joined.columns != 'geometry']
    print(gdf.head(5))
    gdf_merged = gdf.merge(polys, how='inner', on='FID')
    
    for col in gdf_merged.columns:
        gdf_merged = gdf_merged.rename(columns={'{}'.format(col):'{}'.format(col.lower())})
    keyList=[]
    for key in dictionary:
        keyList.append(key)
        selectList = dictionary['{}'.format(key)]
        print(key, selectList) 
        select = [x for x in gdf_merged if x in selectList]
        print(select)
        gdf_merged['{}'.format(key)] = gdf_merged.loc[:, select].sum(axis=1)
        gdf_merged['{}'.format(key)].astype(int)
        print(gdf_merged['{}'.format(key)].sum())
    
    gdf_merged['immigrants'] = gdf_merged['totalpop'] - gdf_merged['pol']
    gdf_merged['immigrants'].astype(int)
    gdf_merged['noneu_immigrants']= gdf_merged['immigrants'] - gdf_merged['EU']
    

    #save shapefiles to folder
    print("------------------------------ Creating shapefile:{0} on Vector Grid------------------------------".format(year)) 
    gdf_merged.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.geojson".format(year), driver='GeoJSON', crs='EPSG:3035')
    #save shapefiles to folder
    #print("------------------------------ Creating shapefile:{0} on Points------------------------------".format(year)) 
    #gdf_points.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataPoints.shp".format(year))

def sumGroups(ancillary_POPdata_folder_path,year, dictionary):
    ndf = gpd.read_file(ancillary_POPdata_folder_path + '/{0}/temp_shp/{0}_dataVectorGrid.shp'.format(year))
    for col in ndf.columns:
        ndf= ndf.rename(columns={'{}'.format(col):'{}'.format(col.lower())})
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
    
    non_match = non_match_elements(ndf.columns.to_list(), list(dictionary.values()))
    print(non_match)
    l2 = [ "grid" ,  "y" , "x" , "index_righ",  "fid",  "totalpop",  "migpop",  "migpertota",  "EU", "pol"]
    l3 = [x for x in non_match if x not in l2]
    ndf['notEU'] = ndf.loc[:, l3].sum(axis=1)
    ndf['notEU'].astype(int)
    print(ndf['notEU'].sum())
    # Create geopandas for large dataframe with all cleaned attributes 
    print("------------------------------ Creating shapefile:{0} on VectorGrid------------------------------".format(year))
    ndf.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid1.geojson".format(year),driver='GeoJSON',crs="EPSG:3035")


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
    src_file = ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.shp".format(year)
    df = gpd.read_file(src_file)
    columns_dont_want = ["GRID", "y", "x", "index_righ", "FID", "geometry"]
    select = [x for x in df.columns if x not in columns_dont_want]
    df_selection= df.loc[:, select]
    print(df_selection)
    columns = df_selection.columns.tolist()
    for column_name in columns: 
        print("Rasterizing {} layer".format(column_name))
        dst_file = ancillary_POPdata_folder_path +"/{0}/temp_tif/{0}_{1}.tif".format(year, column_name)
        cmd = '{0}/gdal_rasterize.exe -a {9} -te {1} {2} {3} {4} -tr {5} {6} "{7}" "{8}"'\
            .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
        print(cmd)
        subprocess.call(cmd, shell=True)