import os
import subprocess
import geopandas as gpd
import gdal
from pathlib import Path
from csv_to_raster import createFolder

def normalize_Numbers(ancillary_POPdata_folder_path, city,year):
    div_srcFile = gpd.read_file(ancillary_POPdata_folder_path + '/1992/temp_shp/1992_dataVectorGrid.geojson')
    df = gpd.read_file(ancillary_POPdata_folder_path + '/{0}/temp_shp/{0}_dataVectorGrid.geojson'.format(year))
    
    disselect =["grid_geometry_epsg3035", "grid_id", "geometry"]
    df_select = [x for x in df if not x in disselect]
    ndf = df.loc[:, df_select]

    selectedColumns = df[['grid_id','geometry','l1_totalpop', 'nld', 'l2_children',	'l3_students',	'l4_mobile_adults',	'l5_not_mobile_adults',	'l6_elderly',
    'l11_births','l12_deaths', 'l21_not_used_dwellings','l22_let_out_dwellings','l23_privately_owned_dwellings','l25_total_area_of_residence',	
    'l26_number_of_dwellings','l27_number_of_rooms', 'Oceania', 'EuropeNotEU', 'EuropeEUnoLocal',  'Central_Asia', 'Eastern_Asia', 'Southern-Eastern_Asia', 'Southern_Asia', 
                'Western_Asia', 'Northern_America', 'Latin_America_and_the_Caribbean', 'Northern_Africa', 'Sub-Saharan_Africa', 'Others', 'Colonies']]
    frame = selectedColumns.copy()
    #Remove the standard columns from the unique Attributes and write file
    select = ['l1_totalpop','nld', 'l2_children', 'l3_students', 'l4_mobile_adults', 'l5_not_mobile_adults', 'l6_elderly',
    'l11_births','l12_deaths', 'l21_not_used_dwellings','l22_let_out_dwellings','l23_privately_owned_dwellings','l25_total_area_of_residence',	
    'l26_number_of_dwellings','l27_number_of_rooms', 'Oceania', 'EuropeNotEU', 'EuropeEUnoLocal',  'Central_Asia', 'Eastern_Asia', 'Southern-Eastern_Asia', 'Southern_Asia', 
                'Western_Asia', 'Northern_America', 'Latin_America_and_the_Caribbean', 'Northern_Africa', 'Sub-Saharan_Africa', 'Others', 'Colonies']

    for i in select:
        max92 =  div_srcFile['{}'.format(i)].max()
        print(i, max92)
        # Calculate percentage of each migrant group per total population
        frame['norm_{}'.format(i)] = df['{}'.format(i)]/max92 #totalPop
        
    frame.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridNorm.geojson".format(year),driver='GeoJSON',crs="EPSG:3035")

def shptorasterNorm(ancillary_POPdata_folder_path,ancillary_data_folder_path, gdal_rasterize_path, city, year, dictionary):
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
    src_file = ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridNorm.geojson".format(year)
    df = gpd.read_file(src_file, crs="EPSG:3035")
    disselect =[ "grid_id", "geometry"]
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

    emptryRasters=list()
    ## ## ## ## ## ----- Rasterize files ----- ## ## ## ## ##
    for column_name in ndf: 
        
        """if ndf["{}".format(column_name)].sum(axis=0) == 0:
            print("----- No Raster created for : {} -----".format(column_name))
            emptryRasters.append(column_name)
        """ 
        if column_name.startswith("norm_"):
            x = column_name.split("norm_")[1] 
            
            dst_path_Regions = os.path.dirname(ancillary_POPdata_folder_path) + "/Normalized/{0}".format(x)
            createFolder(dst_path_Regions)
            print("Rasterizing in GeogrGroups: {} layer".format(column_name))
            dst_file = dst_path_Regions + "/{0}_{1}.tif".format(year, column_name)
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

#Merge all files by year of question
def mergeAoINorm(ancillary_data_folder_path,ancillary_POPdata_folder_path,folder_path,city,mergedFolder,python_scripts_folder_path,year,AoI,
            demo_age,demo_ng,demo_se, buildings, transport, corine, home_prices):
    projectDataFolder = os.path.dirname(ancillary_data_folder_path)
    #Create list of year with geographical areas, append socio-economic and then infrastructure 
     
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    #print(listOfFiles)
    listFiles = []
    first_path = os.path.dirname(ancillary_POPdata_folder_path)  + "/Normalized/00GeogrGroups_sel_Norm\\{0}\\{1}_norm_{0}.tif".format(AoI, year) #totalMig_
    listFiles.append(first_path)
    for x in listOfFiles:
        if x==first_path:
            listOfFiles.remove(x)
            
    for k in listOfFiles:   
        fileName=k.split('\\')[-1] 
        if fileName.endswith('.tif') and fileName.startswith('{}_'.format(year)): 
            listFiles.append(k)
    
    #Now add the DNK
    for file in os.listdir(os.path.dirname(ancillary_POPdata_folder_path) + '/Normalized/nld'):
        if file.endswith('_nld.tif') and file.startswith('{0}_'.format(year)) :#
            path = Path("{0}/Normalized/nld/{2}".format(os.path.dirname(ancillary_POPdata_folder_path), year, file))
            listFiles.append(path)
    
    # Now get the rest of the sociodemographic data
    #indicators = ['l2','l3','l4','l5','l6','l18','l19','l20', 'l21','l22', 'l23','l24' ] #
    indicators = []
    # L2-L6 : 5 age groups
    if demo_age == "yes":
        age_indicators = ['l2','l3','l4','l5','l6']
        indicators.extend(age_indicators)
    
    # L11 : Births, L12 : Deaths
    # L13a : Marriages,male 
    if demo_ng == "yes":
        ng_indicators = ['l11','l12','l13a']
        indicators.extend(ng_indicators)   
    
    # L18 : High Education
    # L19 : Share Rich , L20 : Share Poor
    if demo_se == "yes":
        se_indicators = ['l18','l19_p_rich','l20_p_poor']
        indicators.extend(se_indicators) 
    
    # Buildings :
    # L21 : notused , L22 : rented, L23: Private, L24: public
    if buildings == "yes":
        bl_indicators = ['l21','l22','l23','l24']
        indicators.extend(bl_indicators) 
    
    print(indicators)
    for i in indicators:
        for folder in os.listdir(os.path.dirname(ancillary_POPdata_folder_path) + '/Normalized/01Demo_sel_Norm/'):
            if folder.startswith('{0}'.format(i)):
                for file in os.listdir(os.path.dirname(ancillary_POPdata_folder_path) + '/Normalized/01Demo_sel_Norm/{}'.format(folder)):
                    if file.endswith('.tif') and file.startswith('{0}_norm_{1}_'.format(year,i)) :
                        path = Path("{0}/Normalized/01Demo_sel_Norm/{1}/{2}".format(os.path.dirname(ancillary_POPdata_folder_path),folder,file))
                        listFiles.append(path)
    
    #Now add to that list the infrastructure
    if transport == "yes":                
        for file in os.listdir(projectDataFolder + '/temp_tif'):
            #Add files for busses and trains
            if file.endswith('.tif') and file.startswith('{}_'.format(year)):
                path = Path("{0}/temp_tif/{1}".format(projectDataFolder , file))
                listFiles.append(path)
    
    #Get Corine data     
    if corine == "yes":   
        if year <= 2000:
            pathUF = Path("{0}/temp_tif/corine/urbfabr_{1}_CLC_1990_2000.tif".format(projectDataFolder,city))
            listFiles.append(pathUF)
            pathAG = Path("{0}/temp_tif/corine/agric_{1}_CLC_1990_2000.tif".format(projectDataFolder,city))
            listFiles.append(pathAG)
            pathFOR = Path("{0}/temp_tif/corine/greenSpaces_{1}_CLC_1990_2000.tif".format(projectDataFolder,city))
            listFiles.append(pathFOR)
            pathInd = Path("{0}/temp_tif/corine/industry_{1}_CLC_1990_2000.tif".format(projectDataFolder,city))
            listFiles.append(pathInd)
            pathtransp = Path("{0}/temp_tif/corine/transp_{1}_CLC_1990_2000.tif".format(projectDataFolder,city))
            listFiles.append(pathtransp)
            pathWater = Path("{0}/temp_tif/corine/water_{1}_CLC_1990_2000.tif".format(projectDataFolder,city))
            listFiles.append(pathWater)
        elif year <= 2006 and year > 2000 :
            pathUF = Path("{0}/temp_tif/corine/urbfabr_{1}_CLC_2000_2006.tif".format(projectDataFolder,city))
            listFiles.append(pathUF)
            pathAG = Path("{0}/temp_tif/corine/agric_{1}_CLC_2000_2006.tif".format(projectDataFolder,city))
            listFiles.append(pathAG)
            pathFOR = Path("{0}/temp_tif/corine/greenSpaces_{1}_CLC_2000_2006.tif".format(projectDataFolder,city))
            listFiles.append(pathFOR)
            pathInd = Path("{0}/temp_tif/corine/industry_{1}_CLC_2000_2006.tif".format(projectDataFolder,city))
            listFiles.append(pathInd)
            pathtransp = Path("{0}/temp_tif/corine/transp_{1}_CLC_2000_2006.tif".format(projectDataFolder,city))
            listFiles.append(pathtransp)
            pathWater = Path("{0}/temp_tif/corine/water_{1}_CLC_2000_2006.tif".format(projectDataFolder,city))
            listFiles.append(pathWater)
        elif year <= 2012 and year > 2006 :
            pathUF = Path("{0}/temp_tif/corine/urbfabr_{1}_CLC_2006_2012.tif".format(projectDataFolder,city))
            listFiles.append(pathUF)
            pathAG = Path("{0}/temp_tif/corine/agric_{1}_CLC_2006_2012.tif".format(projectDataFolder,city))
            listFiles.append(pathAG)
            pathFOR = Path("{0}/temp_tif/corine/greenSpaces_{1}_CLC_2006_2012.tif".format(projectDataFolder,city))
            listFiles.append(pathFOR)
            pathInd = Path("{0}/temp_tif/corine/industry_{1}_CLC_2006_2012.tif".format(projectDataFolder,city))
            listFiles.append(pathInd)
            pathtransp = Path("{0}/temp_tif/corine/transp_{1}_CLC_2006_2012.tif".format(projectDataFolder,city))
            listFiles.append(pathtransp)
            pathWater = Path("{0}/temp_tif/corine/water_{1}_CLC_2006_2012.tif".format(projectDataFolder,city))
            listFiles.append(pathWater)
        elif year <= 2020 and year > 2012 :
            pathUF = Path("{0}/temp_tif/corine/urbfabr_{1}_CLC_2012_2018.tif".format(projectDataFolder,city))
            listFiles.append(pathUF)
            pathAG = Path("{0}/temp_tif/corine/agric_{1}_CLC_2012_2018.tif".format(projectDataFolder,city))
            listFiles.append(pathAG)
            pathFOR = Path("{0}/temp_tif/corine/greenSpaces_{1}_CLC_2012_2018.tif".format(projectDataFolder,city))
            listFiles.append(pathFOR)
            pathInd = Path("{0}/temp_tif/corine/industry_{1}_CLC_2012_2018.tif".format(projectDataFolder,city))
            listFiles.append(pathInd)
            pathtransp = Path("{0}/temp_tif/corine/transp_{1}_CLC_2012_2018.tif".format(projectDataFolder,city))
            listFiles.append(pathtransp)
            pathWater = Path("{0}/temp_tif/corine/water_{1}_CLC_2012_2018.tif".format(projectDataFolder,city))
            listFiles.append(pathWater)
    
    #Now add to that list the home prices
    if home_prices == "yes": 
        if year <= 2002:    
            pathHomePrices = Path("{0}/Normalized/02HomePrices_Norm/2002_price_meanNorm.tif".format(projectDataFolder))
            listFiles.append(pathHomePrices)
        else:
            pathHomePrices = Path("{0}/Normalized/02HomePrices_Norm/{}_price_meanNorm.tif".format(projectDataFolder,year))
            listFiles.append(pathHomePrices)               
        

    outfile =  mergedFolder + "/{1}.tif".format(AoI, year)
        
    #Create txt file with number of band --> Name of File
    f = open(mergedFolder + "/{0}_{1}_bandList.txt".format(year,AoI), "w+")
    str_files = " ".join(["{}".format(listFiles[i]) for i in range(len(listFiles))])
    for i,each in enumerate(listFiles,start=1):
        f.write("{}.{}".format(i,each))
        #print ("{}.{}".format(i,each))
    f.close()
        
    # Clear the list for the next loop
    listFiles.clear()
        
    #Write the merged tif file 
    cmd_tif_merge = "python {0}/gdal_merge.py -o {1} -separate {2} ".format(python_scripts_folder_path, outfile, str_files)
    print(cmd_tif_merge)
    subprocess.call(cmd_tif_merge, shell=False)
