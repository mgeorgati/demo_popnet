import os
import subprocess
import pandas as pd
import geopandas as gpd

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
    
    # Calculate percentage of each migrant group per total population
    frame['Z0_nld'] = (df['nld']/df['l1_totalpop'])*100 #totalPop
    frame.drop('Z1_totalMig', axis=1, inplace=True)
    frame.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridDivs.geojson".format(year),driver='GeoJSON',crs="EPSG:3035")

def shptorasterPercentages(ancillary_POPdata_folder_path,ancillary_data_folder_path, gdal_rasterize_path, city,year):
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
        if column_name.startswith('Z0_'):
            print("Rasterizing {} layer".format(column_name))
            dst_Path = ancillary_POPdata_folder_path + "/{0}/temp_tif_Z0".format(year)
            createFolder(dst_Path)
            dst_file = dst_Path + "/{0}_{1}.tif".format(year, column_name)
            cmd = '{0}/gdal_rasterize.exe -a {9} -te {1} {2} {3} {4} -tr {5} {6} "{7}" "{8}"'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
            print(cmd) #-ot Integer64
            subprocess.call(cmd, shell=True)
        elif  column_name.startswith('Z1_'):
            print("Rasterizing {} layer".format(column_name))
            dst_Path = ancillary_POPdata_folder_path + "/{0}/temp_tif_Z1".format(year)
            createFolder(dst_Path)
            dst_file = dst_Path + "/{0}_{1}.tif".format(year, column_name)
            cmd = '{0}/gdal_rasterize.exe -a {9} -te {1} {2} {3} {4} -tr {5} {6} "{7}" "{8}"'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
            print(cmd) #-ot Integer64
            subprocess.call(cmd, shell=True)