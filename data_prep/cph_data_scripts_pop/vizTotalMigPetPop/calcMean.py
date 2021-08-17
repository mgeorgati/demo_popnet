import os
import sys
import numpy as np
import geopandas as gpd
from geopandas.tools import sjoin
import json
from rasterstats import zonal_stats


base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
print(base_dir)
city="cph"
# Paths
ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_ProjectData/PopData".format(city)
districtsPath = base_dir + "/data_prep/cph_ProjectData/AncillaryData/CaseStudy/sogns.geojson"

def createSognMean(year):
    pointsPath = ancillary_POPdata_folder_path + "/{0}/temp_shp/{0}_dataVectorGridDivs.geojson".format(year)

    # Read Files
    districts = gpd.read_file(districtsPath)
    gdf_points = gpd.read_file(pointsPath)
    zs= zonal_stats(districts, "K:/FUME/popnet/PoPNetV2/experiments/cph/trial03/trial03_South_Asia/trial03_South_Asia_CV_01/outputs/predictions/pred_{}.tif".format(year),
                stats="mean", geojson_out=True)
    result = {"type": "FeatureCollection", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::3035" } }, "features": zs}
    
    with open(base_dir + "/data_prep/cph_data_scripts_pop/sognStatistics/sognMean/pred_{}.geojson".format(year), 'w') as outfile:
        json.dump(result, outfile)

years_list= [ 2012,2014,2016,2018 ]
#years_list= [ 1990, 1992, 1994, 1996, 1998,2000, 2002,2004,2006, 2008,2010,2012, 2014,2016,2018 ] 
for year in years_list:
    createSognMean(year)

"""
# Convert the grid to points
gdf_points= gdf_points.drop(columns=["geometry", "index_right"])
points = gpd.GeoDataFrame(
            gdf_points, geometry=gpd.points_from_xy(gdf_points['x'], gdf_points['y']), crs="EPSG:3035")


pointInPolys = sjoin(points, districts, how='inner', op='intersects')

grouped = pointInPolys.groupby('SOGNENAVN')
# Get the Mean Values
df = grouped.mean()

merged_df = df.merge(districts, how="outer")

merged_df.to_file(base_dir + "/data_prep/cph_data_scripts_pop/sognStatistics/{}_sognsMean.geojson".format(year),driver='GeoJSON',crs="EPSG:3035")"""
