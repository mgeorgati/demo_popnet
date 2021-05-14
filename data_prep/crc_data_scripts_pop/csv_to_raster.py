import os
import subprocess
import pandas as pd
import geopandas as gpd
import gdal
import xlrd
from shapely.wkt import loads


def csvtoshp(ancillary_POPdata_folder_path,ancillary_data_folder_path,city):
    #Combine all the csv files in one shp for points and another one for polygons with the vector grid            
    path = ancillary_POPdata_folder_path + "/rawData" # use your path
    li = []
    
    for filename in os.listdir(path):
        print(filename)
        file_path = path + '/' + filename
        year = filename.split("Krakow_")[-1].split(".xlsx")[0]
        print(year)
        df = pd.read_excel(file_path, header=0, skiprows=1 )
        
        #split the Grid column to x,y coordinates and make geometry    
        y=df['GRID'].str.split('N', 1).str[0]
        x=df['GRID'].str.split('N', 1).str[1].str.split('E', 1).str[0]
        df['y'] = y.astype(int)
        df['x'] = x.astype(int)
        print(df.head(5))
        gdf_points = gpd.GeoDataFrame(
                df, geometry=gpd.points_from_xy(df['x'], df['y']), crs='epsg:3035')
        print(gdf_points.crs)
        # spatial join between the vector grid and the points
        polys = gpd.read_file(os.path.dirname(ancillary_data_folder_path) + "/temp_shp/{0}_grid.shp".format(city), crs="EPSG:3035")
        polys = polys.set_crs("EPSG:3035")
        print(polys.crs)
        print(polys.head(5))
        gdf_joined = gpd.sjoin(gdf_points, polys, how='left', op='intersects') # Here I am using intersects with left join
        print(gdf_joined.head(5))
        #remove the point geometry and add the polygon geometry
        gdf = gdf_joined.loc[:, gdf_joined.columns != 'geometry']
        print(gdf.head(5))
        gdf_merged = gdf.merge(polys, how='inner', on='FID')
        
        #Create total population column
        columns_dont_want = ["GRID", "y", "x", "index_right", "FID", "geometry"]
        select = [x for x in gdf_merged.columns if x not in columns_dont_want]
        gdf_merged['totalPop'] = gdf_merged.loc[:, select].sum(axis=1)
        #Create total FOREIGNER population column
        columns_dont_want1 = ["GRID","POL","totalPop", "y", "x", "index_right", "FID", "geometry"]
        select1 = [x for x in gdf_merged.columns if x not in columns_dont_want1]
        gdf_merged['MigPop'] = gdf_merged.loc[:, select1].sum(axis=1)
        gdf_merged['MigPerTotal'] = (gdf_merged['MigPop']/gdf_merged['totalPop'])*100
        print(gdf_merged.head(5))
        #save shapefiles to folder
        print("------------------------------ Creating shapefile:{0} on Vector Grid------------------------------".format(year)) 
        gdf_merged.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.shp".format(year))
        #save shapefiles to folder
        print("------------------------------ Creating shapefile:{0} on Points------------------------------".format(year)) 
        gdf_points.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataPoints.shp".format(year))

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