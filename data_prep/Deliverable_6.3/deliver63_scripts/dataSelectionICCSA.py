import pandas as pd
import geopandas as gpd

def joinGridToGridDKICCSA(ancillary_POPdata_folder_path,year ,ancillary_EUROdata_folder_path,country, deliver_path):
    gridL = gpd.read_file(ancillary_EUROdata_folder_path + "/euroGrid/grid_1km_{}.gpkg".format(country))
    gridL = gridL[['geometry', 'GRD_ID']]
    
    gridS = gpd.read_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.geojson".format(year))
    
    print(gridS.head(2))
    selectCOO= []
    for col in gridS.columns:
        if col.startswith("L10_"):
            
            coo = col.split("L10_")[1]
            gridS=gridS.rename(columns={col:col.replace("L10_","")})
            selectCOO.append(coo)
    
    selectCOO.append('geometry')
    selectCOO.append('L1_SUM_POPULATION')
    print(selectCOO)
    ldf = gridS[selectCOO]
    codes = pd.read_csv('K:/FUME/demo_popnet-Commit01/data_prep/Deliverable/UNSD_methodology.csv', delimiter=",", encoding = "ISO-8859-1", engine='python')
    print(codes.head(2))
    a = codes['ISO-alpha3 Code'].to_list()
    b = ldf.columns.to_list()
    #print(non_match_elements(b, a))
    
    gridL = gpd.read_file(ancillary_EUROdata_folder_path + "/euroGrid/grid_1km_{}.gpkg".format(country))
    gridL = gridL[['geometry', 'GRD_ID']]
    
    regions = codes['Sub-region Name'].unique().tolist()
    #print(codes.head(3))
    #print(regions)
    for key in regions:
        print(key)
        keyFrame = codes.loc[codes['Sub-region Name'] =='{}'.format(key)]
        select = keyFrame['ISO-alpha3 Code'].tolist()
        print(select)
        print(ldf.head(2))
        #ldf['{}'.format(key)] = ldf.loc[:, select].sum(axis=1)
        ldf['{}'.format(key)] = ldf[ldf.columns.intersection(select)].sum(axis=1)
        ldf['{}'.format(key)].astype(int)
        print(ldf['{}'.format(key)].sum())
    
    subregions = codes['Intermediate Region Name'].unique().tolist()
    for key in subregions:
        print(key)
        keyFrame = codes.loc[codes['Intermediate Region Name'] =='{}'.format(key)]
        select1 = keyFrame['ISO-alpha3 Code'].tolist()
        print(select1)
        ldf['{}'.format(key)] = ldf[ldf.columns.intersection(select1)].sum(axis=1)
        ldf['{}'.format(key)].astype(int)
        print(ldf['{}'.format(key)].sum())

    print(ldf.head(2))
    
    finalSelection = regions + subregions
    finalSelection.append('geometry')
    finalSelection.append('L1_SUM_POPULATION')
    print(len(finalSelection), finalSelection)
    cleanedList = [x for x in finalSelection if str(x) != 'nan']
    ndf = ldf[cleanedList] 
    #ndf.drop(columns=['Sub-Saharan Africa', 'Latin America and the Caribbean'])

    gridS_with_gridL = ndf.sjoin(gridL, how="inner", predicate='within')
    
    gdf = gridS_with_gridL.copy()
    print(gdf.head(2))
    gdf.drop(columns=['geometry','index_right'])
    print(gdf.head(2))
    cols=['Northern Africa', 'Sub-Saharan Africa', 'Latin America and the Caribbean', 'Northern America', 'Central Asia', 'Eastern Asia', 
    'South-eastern Asia', 'Southern Asia', 'Western Asia', 'Eastern Europe', 'Northern Europe', 'Southern Europe', 
    'Western Europe', 'Australia and New Zealand', 'Melanesia', 'Micronesia', 'Polynesia', 'Eastern Africa', 'Middle Africa', 
    'Southern Africa', 'Western Africa', 'Caribbean', 'Central America', 'South America', 'Channel Islands', 'Denmark', 'L1_SUM_POPULATION']
    ndf = gpd.GeoDataFrame()
    for i in cols:
        ndf['{}_1km'.format(i)] = gdf.groupby(by = ["GRD_ID"])['{}'.format(i)].sum()
    
    print(ndf.head(2))
    frame = ndf.join(gridL.set_index('GRD_ID'))
    print(frame.head(1))
    frame = gpd.GeoDataFrame(frame, geometry='geometry')
    print(frame.head(2))
    frame.to_csv(deliver_path + "/ICCSA_popData/{0}_1km.csv".format(year,country), sep=';')
    frame.to_file(deliver_path + "/ICCSA_popData/{0}_1km.gpkg".format(year,country),driver='GPKG',crs="EPSG:3035")
