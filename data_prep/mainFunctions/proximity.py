import subprocess
from osgeo import gdal
def shptorasterProximity(raster_file, gdal_rasterize_path, python_scripts_folder_path, vector_file, temp_tif_file, tif_file, xres=100, yres=100):
    '''
    Takes the path of GeoDataframe and converts it to raster
        raster_file         : str
            path to base raster, from which the extent of the new raster is calculated 
        src_file            : str
            path to source file (SHP,GEOJSON, GPKG) 
        gdal_rasterize_path : str
            path to execute gdal_rasterize.exe
        dst_file            : str
            path and name of the destination file
        column_name         : str
            Field to use for rasterizing
    '''
    data = gdal.Open(raster_file)
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None    
    cmd = '{0}/gdal_rasterize.exe -burn 1.0 -tr {5} {6} -a_nodata 0.0 -te {1} {2} {3} {4} -ot Float32 -of GTiff {7} "{8}"'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, vector_file, temp_tif_file)
    subprocess.call(cmd, shell=True)
    
    cmd1 = 'python {0}/gdal_proximity.py -srcband 1 -distunits GEO -nodata 0.0 -ot Float32 -of GTiff {1} "{2}"'\
                .format(python_scripts_folder_path, temp_tif_file, tif_file)
    subprocess.call(cmd1, shell=True)
    