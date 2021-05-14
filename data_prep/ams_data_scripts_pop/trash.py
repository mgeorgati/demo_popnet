"""def csvtoshp(ancillary_POPdata_folder_path,ancillary_data_folder_path,year):
    #Combine all the csv files in one shp for points and another one for polygons with the vector grid            
    path = ancillary_POPdata_folder_path + "/rawData/nidi" # use your path  
    file_path = path + '/nidi{}.xlsx'.format(year)
    print(file_path)
    df = pd.read_excel(file_path, header=0, skiprows=2 )
    ndf = df.iloc[:,:-1].drop(df.index[0]) #
    print(ndf.head(2))
    gdf = gpd.GeoDataFrame(ndf, geometry=ndf['grid_geometry_epsg3035'].apply(loads), crs='epsg:3035') #
    #print(gdf.head(2)) 
    code_path = ancillary_POPdata_folder_path + "/EXCEL/nld_codes.xlsx"
    codes = pd.read_excel(code_path, header=0)
    print(codes)
    df1 = gdf.rename(columns=codes.set_index('Land_nld')['L10_abbr'])
    print (df1.head(4))
    print("------------------------------ Creating geojson:{0} on Vector Grid------------------------------".format(year))
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(ancillary_POPdata_folder_path + "/{}.xlsx".format(year),  index = False,  header=True)
    # Convert the dataframe to an XlsxWriter Excel object.
    df1.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    df1.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVector_Grid11.geojson".format(year), driver='GeoJSON', crs='epsg:3035')"""    

"""def sumCountries(ancillary_POPdata_folder_path,year,dictionary):
   
    # spatial join between the vector grid and the points
    grid = gpd.read_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.geojson".format(year), crs="EPSG:3035")
    grid.columns= grid.columns.str.lower()
    grid.columns= [col.replace('l10_', '') for col in grid.columns]
    print(grid.columns)
    for key in dictionary:
        selectList = dictionary['{}'.format(key)]
        print(key, selectList)
        
        
        select = [x for x in grid.columns.str.rstrip('l10_') if x in selectList]
        print(select)
        grid['{}'.format(key)] = grid.loc[:, select].sum(axis=1)
    print(grid.iloc[1:3, 25:45])
    #save shapefiles to folder
    print("------------------------------ Creating shapefile:{0} on VectorGrid------------------------------".format(year)) 
    grid.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridSums.geojson".format(year),driver='GeoJSON',crs="EPSG:3035")
    
    # Create EU population column
    EU_EE = ["BGR","CZE","HUN","POL","ROU","SVK"]
    select = [x for x in points.columns if x in EU_EE]
    points['EU_EE'] = points.loc[:, select_EU_EE].sum(axis=1)

    EU_EEnotPol = ["BGR","CZE","HUN","ROU","SVK"]
    select_EU_EEnotPol = [x for x in points.columns if x in EU_EEnotPol]
    points['EU_EEnotPol'] = points.loc[:, select_EU_EEnotPol].sum(axis=1)

    EU_NE = ["DNK","FIN","IRL","LVA","LTU","SWE","GBR","ISL","NOR","GBR"]
    select_EU_NE = [x for x in points.columns if x in EU_NE]
    points['EU_NE'] = points.loc[:, select_EU_NE].sum(axis=1)

    EU_SE = ["HRV","GRC","ITA","MLT","PRT","SVN","ESP","CYP"]
    select_EU_SE = [x for x in points.columns if x in EU_SE]
    points['EU_SE'] = points.loc[:, select_EU_SE].sum(axis=1)

    EU_WE = ["AUT","BEL","FRA","DEU","LUX","MCO","NLD","LIE","CHE"]
    select_EU_WE = [x for x in points.columns if x in EU_WE]
    points['EU_WE'] = points.loc[:, select_EU_WE].sum(axis=1)

    # Create not EU population column
    notEU_EE = ["BLR","MDA","RUS","UKR"]
    select_notEU_EE = [x for x in points.columns if x in notEU_EE]
    points['notEU_EE'] = points.loc[:, select_notEU_EE].sum(axis=1)

    notEU_NE = ["ALA","GGY","JEY","FRO","IMN","SJM"]
    select_notEU_NE = [x for x in points.columns if x in notEU_NE]
    points['notEU_NE'] = points.loc[:, select_notEU_NE].sum(axis=1)

    notEU_SE = ["ALB","AND","BIH","GIB","VAT","MNE","MKD","SMR","SRB"]
    select_notEU_SE = [x for x in points.columns if x in notEU_SE]
    points['notEU_SE'] = points.loc[:, select_notEU_SE].sum(axis=1)
    
    #save shapefiles to folder
    print("------------------------------ Creating shapefile:{0} on Points------------------------------".format(year)) 
    points.to_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataPointsSums.shp".format(year))   
    """

def findCountries(ancillary_POPdata_folder_path,years_list):
    grid = gpd.read_file(ancillary_POPdata_folder_path + "/2018/temp_shp/2018_dataVectorGrid.geojson", crs="EPSG:3035")
    colList = grid.columns.tolist()
    
    for i in range(len(years_list)):
        # spatial join between the vector grid and the points
        df = gpd.read_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.geojson".format(years_list[i]), crs="EPSG:3035")
        unique = [x for x in df.columns if x not in colList and (colList.append(x) or True)]
    print(colList)

    for i in colList:
        if not i.startswith("L10"):
            print(i)
    """#sumI = [grid['{}'.format(i)].sum(axis=1) for i in grid.columns if grid['{}'.format(i)].sum(axis=1) == 0]
    #print
    selectList = ['grid_geometry_epsg3035','geometry', 'grid_id']        
    select = [x for x in grid.columns if not x in selectList]
    
    for i in select:
        sumI = grid['{}'.format(i)].sum()
        if sumI == 0 :
            print(i)
        elif sumI <= 10 :
            print(i)"""