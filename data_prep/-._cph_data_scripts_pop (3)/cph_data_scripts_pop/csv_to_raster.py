import os
import subprocess
import pandas as pd
import geopandas as gpd
import gdal

import glob

def csvtoshp(ancillary_POPdata_folder_path,ancillary_data_folder_path, year):
 
    #Combine all the csv files in one shp for points and another one for polygons with the vector grid            
    csv_path = ancillary_POPdata_folder_path + "/{}".format(year) # use your path
    all_files = glob.glob(csv_path + "/*.csv")

    li = []

    for filename in all_files:
        #print(filename)
        fileName = filename.split("/")[-1].split(".csv")[0].split("FUME_")[1]
        fileCode = fileName.split("_")[0]
        #print(fileName)
        df = pd.read_csv(filename, index_col='GC100m', header=0)
        if fileName.endswith("_NEWINCOME") :
            df = df.rename(columns={'P_RICH': 'P_RICH_NEW'})
            df = df.rename(columns={'P_POOR': 'P_POOR_NEW'})
            li.append(df)
        else:   
            columns= df.columns.tolist()
            for i in columns:
                df = df.rename(columns={'{0}'.format(i): '{0}_{1}'.format(fileCode,i)})
            li.append(df)    

    data = pd.concat(li, axis=1, ignore_index=False)
    data.index.name = 'GC100m'
    data_new= data.reset_index()
    
    #split the GC100m column to x,y coordinates and make geometry    
    y=data_new['GC100m'].str.split('N', 1).str[0]
    x=data_new['GC100m'].str.split('N', 1).str[1].str.split('E', 1).str[0]
    data_new['y'] = y.astype(int)
    data_new['x'] = x.astype(int)

    gdf_points = gpd.GeoDataFrame(
            data_new, geometry=gpd.points_from_xy(data_new['x'], data_new['y']), crs={'init': 'epsg:3035'})

    # spatial join between the vector grid and the points
    polys = gpd.read_file(ancillary_data_folder_path + "/CaseStudy/cph_vectorgrid.geojson")
    gdf_joined = gpd.sjoin(gdf_points, polys, how='left', op='intersects') # Here I am using intersects with left join
    
    #remove the point geometry and add the polygon geometry
    gdf = gdf_joined.loc[:, gdf_joined.columns != 'geometry']
    gdf_merged= gdf.merge(polys, how='inner', on='gid')
    #print(gdf_merged.head())
    #print(gdf_merged.columns.tolist())
    #save shapefiles to folder
    print("------------------------------ Creating shapefile:{0} on Vector Grid------------------------------".format(year)) 
    gdf_merged.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.shp".format(year))
    #save shapefiles to folder
    print("------------------------------ Creating shapefile:{0} on Points------------------------------".format(year)) 
    gdf_points.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataPoints.shp".format(year))

def shptoraster(ancillary_POPdata_folder_path,ancillary_data_folder_path, gdal_rasterize_path, city,year):
    # Getting extent of ghs pop raster
    data = gdal.Open(ancillary_data_folder_path + "/temp_tif/{0}_U2018_CLC2012_V2020_20u1.tif".format(city))
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
    df= df.iloc[:, 1:-5]
    columns = df.columns.tolist()
    for column_name in columns: 
        print("Rasterizing {} layer".format(column_name))
        dst_file = ancillary_POPdata_folder_path +"/{0}/temp_tif/{0}_{1}.tif".format(year, column_name)
        cmd = '{0}/gdal_rasterize.exe -a {9} -te {1} {2} {3} {4} -tr {5} {6} {7} {8}'\
            .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
        subprocess.call(cmd, shell=True)

"""
############################# Older Version #################################
def csvtoshp(ancillary_POPdata_folder_path, year):
    
    csv_path = ancillary_POPdata_folder_path + "/{}".format(year)
        
    for file in os.listdir(csv_path):
        #filePath = os.path.join(csv_path, file)
            
        if file.endswith(".csv"):
            print(file)
            fileName = file.split(".csv")[0].split("FUME_")[1]
            data = pd.read_csv(ancillary_POPdata_folder_path + "/{0}/{1}".format(year,file), sep=',') 

            #split the GC100m column to x,y coordinates and make geometry    
            y=data['GC100m'].str.split('N', 1).str[0]
            x=data['GC100m'].str.split('N', 1).str[1].str.split('E', 1).str[0]
            data['y'] = y.astype(int)
            data['x'] = x.astype(int)

            gdf = gpd.GeoDataFrame(
                data, geometry=gpd.points_from_xy(data['x'], data['y']), crs={'init': 'epsg:3035'})
                
            #save shapefiles to folder
            print("------------------------------ Creating shapefile:{0} for {1}------------------------------".format(fileName,year))        
            gdf.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{1}.shp".format(year,fileName))
            

def shptoraster(ancillary_POPdata_folder_path,python_scripts_folder_path, year):
    # Define pixel_size and NoData value of new raster
    pixel_size = 100
    NoData_value = 0
    
    shp_path = ancillary_POPdata_folder_path + "/{}/temp_shp".format(year)
    tif_path = ancillary_POPdata_folder_path + "/{}/temp_tif".format(year)
    for file in os.listdir(shp_path):
        #filename = os.fsdecode(file)
        #print(filename)
        if file =='L10_PopCOO.shp': # whatever file types you're using...
            #filenames.append(filename)
            print(file)
                    
            name=os.path.splitext(file)[0]
            daShapefile = "{}/{}".format(shp_path,file)
            driver = ogr.GetDriverByName('ESRI Shapefile')
            dataSource = driver.Open(daShapefile, 0) # 0 means read-only. 1 means writeable.

            # Check to see if shapefile is found.
            if dataSource is None:
                print ('Could not open %s' % (daShapefile))
            else:
                print ('Opened %s' % (daShapefile))
                layer = dataSource.GetLayer()
                featureCount = layer.GetFeatureCount()
                print ("Number of features in %s: %d" % (os.path.basename(daShapefile),featureCount))

                #Open the data source and read in the extent
                source_ds = ogr.Open(file)

                schema = []
                ldefn = layer.GetLayerDefn()
                for n in range(ldefn.GetFieldCount()):
                    fdefn = ldefn.GetFieldDefn(n)
                    schema.append(fdefn.name)
                    
                schema.remove('GC100m' )
                schema.remove('x')
                schema.remove('y')
                for field in schema:
                    # Filename of the raster Tiff that will be created
                    raster_fn = "{0}/{1}_{2}_{3}.tif".format(tif_path,year,name,field)
                    #print(raster_fn)
                    
                    source_layer = dataSource.GetLayer()
                    srs= source_layer.GetSpatialRef()
                    #x_min, x_max, y_min, y_max = source_layer.GetExtent()
                    
                    x_min= 4456350.0
                    x_max= 4497100.0
                    y_min= 3608600.0
                    y_max= 3636650.0
                    
                    # Create the destination data source
                    x_res = int((x_max - x_min + pixel_size) / pixel_size)
                    y_res = int((y_max - y_min + pixel_size) / pixel_size)
                    target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Float32)
                    x= x_min-(pixel_size/2)
                    y= y_max+(pixel_size/2)

                    target_ds.SetGeoTransform((x, pixel_size, 0, y, 0, -pixel_size))

                    target_wkt=srs.ExportToWkt()
                    target_ds.SetProjection(target_wkt)

                    band = target_ds.GetRasterBand(1)
                    band.SetNoDataValue(NoData_value)

                    # Rasterize
                    gdal.RasterizeLayer(target_ds, [1], source_layer, options=["ATTRIBUTE={}".format(field), "ALL_TOUCHED=FALSE"], burn_values=[1])
                    target_ds = None
            
        if file.endswith('.shp') and file !='L10_PopCOO.shp':
            name=os.path.splitext(file)[0]
            daShapefile = "{}/{}".format(shp_path,file)
            driver = ogr.GetDriverByName('ESRI Shapefile')
            dataSource = driver.Open(daShapefile, 0) # 0 means read-only. 1 means writeable.

            # Check to see if shapefile is found.
            if dataSource is None:
                print ('Could not open %s' % (daShapefile))
            else:
                print ('Opened %s' % (daShapefile))
                layer = dataSource.GetLayer()
                featureCount = layer.GetFeatureCount()
                print ("Number of features in %s: %d" % (os.path.basename(daShapefile),featureCount))

                #Open the data source and read in the extent
                source_ds = ogr.Open(file)

                schema = []
                ldefn = layer.GetLayerDefn()
                for n in range(ldefn.GetFieldCount()):
                    fdefn = ldefn.GetFieldDefn(n)
                    schema.append(fdefn.name)
                field= schema[1]
                        
                # Filename of the raster Tiff that will be created
                raster_fn = "{0}/{1}_{2}.tif".format(tif_path,year,name)

                source_layer = dataSource.GetLayer()
                srs= source_layer.GetSpatialRef()
                #x_min, x_max, y_min, y_max = source_layer.GetExtent()
                
                x_min= 4456350.0
                x_max= 4497100.0
                y_min= 3608600.0
                y_max= 3636650.0
                # Create the destination data source
                x_res = int((x_max - x_min + pixel_size) / pixel_size)
                y_res = int((y_max - y_min + pixel_size) / pixel_size)
                target_ds = gdal.GetDriverByName('GTiff').Create(raster_fn, x_res, y_res, 1, gdal.GDT_Float32)
                x= x_min-(pixel_size/2)
                y= y_max+(pixel_size/2)

                target_ds.SetGeoTransform((x, pixel_size, 0, y, 0, -pixel_size))

                target_wkt=srs.ExportToWkt()
                target_ds.SetProjection(target_wkt)

                band = target_ds.GetRasterBand(1)
                band.SetNoDataValue(NoData_value)

                # Rasterize
                gdal.RasterizeLayer(target_ds, [1], source_layer, options=["ATTRIBUTE={}".format(field), "ALL_TOUCHED=FALSE"], burn_values=[1])
                target_ds = None
"""           
           