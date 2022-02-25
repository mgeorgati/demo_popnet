import geopandas as gpd

def joinGridToGridPL(ancillary_POPdata_folder_path, year, ancillary_EUROdata_folder_path,country, deliver_path):
    gridL = gpd.read_file(ancillary_EUROdata_folder_path + "/euroGrid/grid_1km_{}.gpkg".format(country))
    gridL = gridL[['geometry', 'GRD_ID']]
    
    gridS = gpd.read_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.geojson".format(year))
    gridS = gridS[[ "totalpop", "children", "students", "mobile_adults", "not_mobile_adults", "elderly", 
                   "births", "deaths","inflow-registration","outflow-unregistration", "immigrants", "EU", "noneu_immigrants" ,"pol", 'geometry']]
    gridS = gridS.rename(columns={'EU':'eu_immigrants'})
    gridS_with_gridL = gridS.sjoin(gridL, how="inner", predicate='within')
    print(gridS_with_gridL.columns.tolist())
    print(gridS.head(2))
    print(gridL.head(2))
    gdf = gridS_with_gridL[['GRD_ID',"totalpop", "children", "students", "mobile_adults", "not_mobile_adults", "elderly", 
                   "births", "deaths","inflow-registration","outflow-unregistration", "immigrants", "eu_immigrants", "noneu_immigrants" ,"pol"]]
    
    columns = ["totalpop", "children", "students", "mobile_adults", "not_mobile_adults", "elderly", 
                   "births", "deaths","inflow-registration","outflow-unregistration", "immigrants", "eu_immigrants", "noneu_immigrants" ,"pol"]
    ndf = gpd.GeoDataFrame()
    for i in columns:
        ndf['{}_1km'.format(i)] = gdf.groupby(by = ["GRD_ID"])['{}'.format(i)].sum()
    print(ndf.head(2))
    ndf = ndf.join(gridL.set_index('GRD_ID'))
    ndf= gpd.GeoDataFrame(ndf, geometry='geometry')
    popMig = ndf[['totalpop_1km','pol_1km', 'immigrants_1km', 'eu_immigrants_1km', 'noneu_immigrants_1km',
               'geometry']]
    
    popAge = ndf[['totalpop_1km',"children_1km", "students_1km", "mobile_adults_1km", "not_mobile_adults_1km", "elderly_1km", 
                   "births_1km", "deaths_1km","inflow-registration_1km","outflow-unregistration_1km",
               'geometry']]
    
    popMig.to_csv(deliver_path + "/{1}/Population/{0}_MigrationStatus.csv".format(year,country), sep=';')
    popMig.to_file(deliver_path + "/{1}/Population/{0}_MigrationStatus.gpkg".format(year,country),driver='GPKG',crs="EPSG:3035")
    
    popAge.to_csv(deliver_path + "/{1}/Population/{0}_DemographicFeatures.csv".format(year,country), sep=';')
    popAge.to_file(deliver_path + "/{1}/Population/{0}_DemographicFeatures.gpkg".format(year,country),driver='GPKG',crs="EPSG:3035")