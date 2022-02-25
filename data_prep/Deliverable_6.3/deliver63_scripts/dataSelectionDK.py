import geopandas as gpd

def joinGridToGridDK(ancillary_POPdata_folder_path,year ,ancillary_EUROdata_folder_path,country, deliver_path):
    gridL = gpd.read_file(ancillary_EUROdata_folder_path + "/euroGrid/grid_1km_{}.gpkg".format(country))
    gridL = gridL[['geometry', 'GRD_ID']]
    
    gridS = gpd.read_file(ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGrid.geojson".format(year))
    #gridS = gridS.explode()
    print(gridS.columns.tolist())
    gridS = gridS[['L1_SUM_POPULATION', 'L2_P00_19', 'L3_P20_29', 'L4_P30_44', 'L5_P45_64', 'L6_P65', 'L7_P_IMMIG', 'L8_P_EUMIG', 'L9_P_NOEUMIG', 'L10_DNK',
                'L11_SUM_Births', 'L12_SUM_Deaths', 'L13a_SUM_Marriages', 'L13b_SUM_Marriages', 
                 "L14a_P_OUTMIGR",  "L14b_P_OUTMIGR_NoDK",  "L15a_P_INMIGR",  "L15b_P_INMIGR_NoDK",  "L16_P_OUTMIGR_InCPH",  "L17_P_INMIGR_InCPH" ,
                 'L18_P_TEDUC', 'L19_P_RICH', 'L19_P_RICH_NEW', 'L20_P_POOR', 'L20_P_POOR_NEW', 
                 'L21_P_NOTUSED', 'L22_P_RENTED', 'L23_P_PRIVATE', 'L24_P_PUBLIC', 'L25_P_AREA', 'L26_P_HOME', 'L27_P_NROOMS',  'geometry']]
    
    gridS['L2_00_19'] = round(gridS['L2_P00_19'] * gridS['L1_SUM_POPULATION'], 0)
    gridS['L3_20_29'] = round(gridS['L3_P20_29'] * gridS['L1_SUM_POPULATION'], 0)
    gridS['L4_30_44'] = round(gridS['L4_P30_44'] * gridS['L1_SUM_POPULATION'], 0)
    gridS['L5_45_64'] = round(gridS['L5_P45_64'] * gridS['L1_SUM_POPULATION'], 0)
    gridS['L6_65'] = round(gridS['L6_P65'] * gridS['L1_SUM_POPULATION'], 0)
    
    gridS['L18_TEDUC'] = round(gridS['L18_P_TEDUC'] * gridS['L1_SUM_POPULATION'], 0)
    gridS['L19_RICH'] = round(gridS['L19_P_RICH'] * gridS['L1_SUM_POPULATION'], 0)
    gridS['L19_RICH_NEW'] = round(gridS['L19_P_RICH_NEW'] * gridS['L1_SUM_POPULATION'], 0)
    gridS['L20_POOR'] = round(gridS['L20_P_POOR'] * gridS['L1_SUM_POPULATION'], 0)
    gridS['L20_POOR_NEW'] = round(gridS['L20_P_POOR_NEW'] * gridS['L1_SUM_POPULATION'], 0)
    
    gridS['L7_IMMIG'] = round(gridS['L7_P_IMMIG'] * gridS['L1_SUM_POPULATION'], 0)          
    gridS['L8_EUMIG'] = round(gridS['L8_P_EUMIG'] * gridS['L1_SUM_POPULATION'],0) 
    gridS['L9_NOEUMIG'] = round(gridS['L9_P_NOEUMIG'] * gridS['L1_SUM_POPULATION'],0)
    
    gridS['L21_NOTUSED'] = round(gridS['L21_P_NOTUSED'] * gridS['L26_P_HOME'], 0)          
    gridS['L22_RENTED'] = round(gridS['L22_P_RENTED'] *gridS['L26_P_HOME'],0) 
    gridS['L23_PRIVATE'] = round(gridS['L23_P_PRIVATE'] * gridS['L26_P_HOME'],0)
    gridS['L24_PUBLIC'] = round(gridS['L24_P_PUBLIC'] * gridS['L26_P_HOME'],0)
    print(gridS.head(2))
    print(gridL.head(2))
    gridS_with_gridL = gridS.sjoin(gridL, how="inner", predicate='within')
    print(gridS_with_gridL.columns.tolist())
    gdf = gridS_with_gridL.copy()

    columns = ['L1_SUM_POPULATION',  'L10_DNK', 'L7_IMMIG', 'L8_EUMIG', 'L9_NOEUMIG',
                'L2_00_19', 'L3_20_29', 'L4_30_44', 'L5_45_64', 'L6_65', 
                'L11_SUM_Births', 'L12_SUM_Deaths', 'L13a_SUM_Marriages', 'L13b_SUM_Marriages', 
                'L18_TEDUC', 'L19_RICH', 'L19_RICH_NEW', 'L20_POOR', 'L20_POOR_NEW',
                "L14a_P_OUTMIGR",  "L14b_P_OUTMIGR_NoDK",  "L15a_P_INMIGR",  "L15b_P_INMIGR_NoDK",  "L16_P_OUTMIGR_InCPH",  "L17_P_INMIGR_InCPH" ,
                'L21_NOTUSED', 'L22_RENTED', 'L23_PRIVATE', 'L24_PUBLIC',
                'L25_P_AREA', 'L26_P_HOME', 'L27_P_NROOMS']
    
    ndf = gpd.GeoDataFrame()
    for i in columns:
        ndf['{}_1km'.format(i)] = gdf.groupby(by = ["GRD_ID"])['{}'.format(i)].sum()
    print(ndf.head(2))

    ndf = ndf.join(gridL.set_index('GRD_ID'))
    ndf= gpd.GeoDataFrame(ndf, geometry='geometry')
   

    ndf = ndf.rename(columns={'L1_SUM_POPULATION_1km': 'totalpop_1km' ,'L10_DNK_1km': 'dnk_1km', 'L7_IMMIG_1km':'immigrants_1km', 'L8_EUMIG_1km':'eu_immigrants_1km', 
                'L9_NOEUMIG_1km':'noneu_immigrants_1km',
                
                'L2_00_19_1km':'children_1km', 'L3_20_29_1km':'students_1km','L4_30_44_1km': 'mobile_adults_1km', 'L5_45_64_1km':'not_mobile_adults_1km', 'L6_65_1km':'elderly_1km', 
                'L11_SUM_Births_1km':'births_1km', 'L12_SUM_Deaths_1km': 'deaths_1km', 'L13a_SUM_Marriages_1km':'marriagesM_1km', 'L13b_SUM_Marriages_1km':'marriagesF_1km', 
                'L18_TEDUC_1km':'tert_education_1km', 'L19_RICH_1km':'rich_1km', 'L19_RICH_NEW_1km':'rich_new_1km', 'L20_POOR_1km':'poor_1km', 'L20_POOR_NEW_1km':'poor_new_1km',
                'L14a_P_OUTMIGR_1km': 'people_who_moved_out_of_grid_1km',  'L14b_P_OUTMIGR_NoDK_1km': 'immigrants_out_outof_denmark_1km',  'L15a_P_INMIGR_1km': 'people_who_moved_in_grid_1km',  
                'L15b_P_INMIGR_NoDK_1km': 'immigrants_in_outof_denmark_1km',  'L16_P_OUTMIGR_InCPH_1km': 'people_who_moved_out_of_grid_incph_1km',  
                'L17_P_INMIGR_InCPH_1km': 'people_who_moved_in_grid_fromcph_1km',
                'L21_NOTUSED_1km':'not_used_dwellings_1km', 'L22_RENTED_1km':'rented_dwellings_1km', 'L23_PRIVATE_1km':'privately_owned_dwellings_1km', 
                'L24_PUBLIC_1km':'public_dwellings_1km', 'L25_P_AREA_1km': 'total_area_of_residence_1km', 
                'L26_P_HOME_1km':'number_of_dwellings_1km', 'L27_P_NROOMS_1km':'number_of_rooms_1km' })
    print(ndf.columns.tolist())
    popMig = ndf[['totalpop_1km','dnk_1km', 'immigrants_1km', 'eu_immigrants_1km', 'noneu_immigrants_1km',
               'geometry']]
    
    popMig.to_csv(deliver_path + "/{1}/Population/{0}_MigrationStatus.csv".format(year,country), sep=';')
    popMig.to_file(deliver_path + "/{1}/Population/{0}_MigrationStatus.gpkg".format(year,country),driver='GPKG',crs="EPSG:3035")

    popAge = ndf[['totalpop_1km','children_1km', 'students_1km', 'mobile_adults_1km', 'not_mobile_adults_1km', 'elderly_1km',
               'births_1km', 'deaths_1km', 'marriagesM_1km', 'marriagesF_1km', 
                'tert_education_1km', 'rich_1km', 'rich_new_1km','poor_1km', 'poor_new_1km',
                'people_who_moved_out_of_grid_1km',  'immigrants_out_outof_denmark_1km',  'people_who_moved_in_grid_1km',  
                'immigrants_in_outof_denmark_1km',  'people_who_moved_out_of_grid_incph_1km',  'people_who_moved_in_grid_fromcph_1km',
                'geometry']]
    
    popAge.to_csv(deliver_path + "/{1}/Population/{0}_DemographicFeatures.csv".format(year,country), sep=';')
    popAge.to_file(deliver_path + "/{1}/Population/{0}_DemographicFeatures.gpkg".format(year,country),driver='GPKG',crs="EPSG:3035")

    buildings = ndf[['not_used_dwellings_1km', 'rented_dwellings_1km', 
                'privately_owned_dwellings_1km', 'public_dwellings_1km', 
                'total_area_of_residence_1km', 'number_of_dwellings_1km', 'number_of_rooms_1km' , 'geometry']]
    
    buildings.to_csv(deliver_path + "/{1}/Buildings/{0}_Buildings.csv".format(year,country), sep=';')
    buildings.to_file(deliver_path + "/{1}/Buildings/{0}_Buildings.gpkg".format(year,country),driver='GPKG',crs="EPSG:3035")

import json
from rasterstats import zonal_stats
# Calculate zonal statistics from tiffs
def zonalStat(src_file, dst_file, polyPath, statistics):  
    # Read Files
    districts = gpd.read_file(polyPath)
    districts = districts.to_crs("EPSG:3035")
    
    zs = zonal_stats(districts, src_file,
                stats='{}'.format(statistics), all_touched = False, percent_cover_selection=None, percent_cover_weighting=False, #0.5-->dubled the population
                percent_cover_scale=None,geojson_out=True)
    
    for row in zs:
        newDict = row['properties']
        for i in newDict.keys():
            if i == '{}'.format(statistics):
                newDict['{}_'.format(statistics)] = newDict.pop(i)
        
    result = {"type": "FeatureCollection", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::3035" } }, "features": zs}
    #dst_file = dstPath + "{0}".format(dstFile) #
    with open(dst_file , 'w') as outfile:
        json.dump(result, outfile)

    
