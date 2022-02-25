import geopandas as gpd

def joinGridToGridNL(ancillary_POPdata_folder_path,year ,ancillary_EUROdata_folder_path,country, deliver_path):
    gridL = gpd.read_file(ancillary_EUROdata_folder_path + "/euroGrid/grid_1km_{}.gpkg".format(country))
    gridL = gridL[['geometry', 'GRD_ID']]
    
    gridS = gpd.read_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.geojson".format(year))
    
    gridS_with_gridL = gridS.sjoin(gridL, how="inner", predicate='within')
    print(gridS_with_gridL.columns.tolist())
    
    gdf = gridS_with_gridL[['GRD_ID','l1_totalpop', 'l2_children', 'l3_students', 'l4_mobile_adults', 'l5_not_mobile_adults', 'l6_elderly','nld', 'l7_immigrants', 'l8_eu_immigrants', 'l9_noneu_immigrants', 'l11_births', 'l12_deaths', 'l14a_people_who_moved_out_of_grid', 'l14b_immigrants_into_netherlands', 'l15a_ people_who_moved_into_grid', 'l15b_immigrants_outof_netherlands', 'l16_verhuis_in_ams_outof', 'l17_verhuis_in_ams_into', 'l21_not_used_dwellings', 'l22_let_out_dwellings', 'l23_privately_owned_dwellings', 'l25_total_area_of_residence', 'l26_number_of_dwellings', 'l27_number_of_rooms']]
    gdf = gdf.rename(columns={'l1_totalpop':'totalpop', 'l2_children':'children', 'l3_students':'students', 'l4_mobile_adults':'mobile_adults', 'l5_not_mobile_adults':'not_mobile_adults', 'l6_elderly':'elderly', 
                              'l7_immigrants':'immigrants', 'l8_eu_immigrants':'eu_immigrants', 'l9_noneu_immigrants':'noneu_immigrants', 'l11_births':'births', 'l12_deaths':'deaths', 
                              'l14a_people_who_moved_out_of_grid':'people_who_moved_out_of_grid', 'l14b_immigrants_into_netherlands':'immigrants_into_netherlands', 'l15a_ people_who_moved_into_grid':'people_who_moved_into_grid', 'l15b_immigrants_outof_netherlands':'immigrants_outof_netherlands', 
                              'l16_verhuis_in_ams_outof':'verhuis_in_ams_outof', 'l17_verhuis_in_ams_into':'verhuis_in_ams_into', 
                              'l21_not_used_dwellings':'not_used_dwellings', 'l22_let_out_dwellings':'let_out_dwellings', 'l23_privately_owned_dwellings':'privately_owned_dwellings', 
                              'l25_total_area_of_residence':'total_area_of_residence', 'l26_number_of_dwellings':'number_of_dwellings', 'l27_number_of_rooms':'number_of_rooms'})
    
    columns = ['totalpop', 'children', 'students', 'mobile_adults', 'not_mobile_adults', 'elderly','nld', 'immigrants', 'eu_immigrants', 'noneu_immigrants', 'births', 'deaths', 
               'people_who_moved_out_of_grid', 'immigrants_into_netherlands', 'people_who_moved_into_grid', 'immigrants_outof_netherlands', 'verhuis_in_ams_outof', 'verhuis_in_ams_into', 
               'not_used_dwellings', 'let_out_dwellings', 'privately_owned_dwellings', 'total_area_of_residence', 'number_of_dwellings', 'number_of_rooms']
    ndf = gpd.GeoDataFrame()
    for i in columns:
        ndf['{}_1km'.format(i)] = gdf.groupby(by = ["GRD_ID"])['{}'.format(i)].sum()
    print(ndf.head(2))
    ndf = ndf.join(gridL.set_index('GRD_ID'))
    ndf= gpd.GeoDataFrame(ndf, geometry='geometry')
    popMig = ndf[['totalpop_1km','nld_1km', 'immigrants_1km', 'eu_immigrants_1km', 'noneu_immigrants_1km', 'geometry']]
    
    popAge = ndf[['totalpop_1km', 'children_1km', 'students_1km', 'mobile_adults_1km', 'not_mobile_adults_1km', 'elderly_1km',
               'births_1km', 'deaths_1km', 
               'people_who_moved_out_of_grid_1km', 'immigrants_into_netherlands_1km', 'people_who_moved_into_grid_1km', 'immigrants_outof_netherlands_1km', 'verhuis_in_ams_outof_1km', 
               'verhuis_in_ams_into_1km',
               'geometry']]
    
    popMig.to_csv(deliver_path + "/{1}/Population/{0}_MigrationStatus.csv".format(year,country), sep=';')
    popMig.to_file(deliver_path + "/{1}/Population/{0}_MigrationStatus.gpkg".format(year,country),driver='GPKG',crs="EPSG:3035")
    
    popAge.to_csv(deliver_path + "/{1}/Population/{0}_DemographicFeatures.csv".format(year,country), sep=';')
    popAge.to_file(deliver_path + "/{1}/Population/{0}_DemographicFeatures.gpkg".format(year,country),driver='GPKG',crs="EPSG:3035")
    
    buildings = ndf[['not_used_dwellings_1km', 'let_out_dwellings_1km', 'privately_owned_dwellings_1km', 'total_area_of_residence_1km', 'number_of_dwellings_1km', 'number_of_rooms_1km', 'geometry']]
    buildings.to_csv(deliver_path + "/{1}/Buildings/{0}_Buildings.csv".format(year,country), sep=';')
    buildings.to_file(deliver_path + "/{1}/Buildings/{0}_Buildings.gpkg".format(year,country),driver='GPKG',crs="EPSG:3035")