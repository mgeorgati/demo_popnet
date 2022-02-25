import geopandas as gpd
import numpy as np

def selectEuroGrid(ancillary_EUROdata_folder_path, country, nutsArea):
    df = gpd.read_file(ancillary_EUROdata_folder_path + '/euroGrid/grid_1km_surf.gpkg')
    if isinstance(nutsArea,list):
        df[df['Credit-Rating'].str.contains('Fair')]
        gdf =df.loc[np.logical_or(df["NUTS2021_3" ].str.contains(nutsArea[0]),df["NUTS2021_3"].str.contains(nutsArea[1]))]
    else: 
        gdf =df.loc[df["NUTS2021_3"].str.contains(nutsArea)]
    print(gdf.head(2))
    gdf.to_file(ancillary_EUROdata_folder_path + "/euroGrid/grid_1km_{}.gpkg".format(country),driver='GPKG',crs="EPSG:3035")
    

    

    
   
    

    
    
    
    