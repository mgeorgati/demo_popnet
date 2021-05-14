import os 
import pandas as pd
from osgeo import gdal
import sys
import math
import matplotlib.pyplot as plt

def reclassify(directory,trialNo,country, extTrial, year_list):
    
    for year in year_list:
        driver = gdal.GetDriverByName('GTiff')
        
        file = gdal.Open(directory + '/{0}_{1}/{0}_{1}_{3}/output/AcPerc_{0}_{1}_{2}.tif'.format(trialNo,country,year, extTrial))
        band = file.GetRasterBand(1)
        #print(directory + '/{0}_{1}/{0}_{1}_{3}/output/dif_{0}_{1}_{2}.tif'.format(trialNo,country,year, extTrial))
        lista = band.ReadAsArray()

        # reclassification
        for j in range(file.RasterXSize):
            for i in range(file.RasterYSize):
                if lista[i,j] <= -5:
                    lista[i,j] = 1
                elif -5 < lista[i,j] < -1:
                    lista[i,j] = 2
                elif -1 < lista[i,j] < -0.01:
                    lista[i,j] = 3
                elif -0.01 <= lista[i,j] <= 0.01:
                    lista[i,j] = 4
                elif 0.01 < lista[i,j] < 1:
                    lista[i,j] = 5
                elif 1 < lista[i,j] < 5:
                    lista[i,j] = 6
                elif 5 < lista[i,j] :
                    lista[i,j] = 7
                else:
                    lista[i,j] = 0

        # create new file
        file2 = driver.Create( directory + '/{0}_{1}/{0}_{1}_{3}/output/AcPerc_{0}_{1}_{2}_reclass.tif'.format(trialNo,country,year, extTrial), file.RasterXSize , file.RasterYSize , 1)
        file2.GetRasterBand(1).WriteArray(lista)

        # spatial ref system
        proj = file.GetProjection()
        georef = file.GetGeoTransform()
        file2.SetProjection(proj)
        file2.SetGeoTransform(georef)
        file2.FlushCache()

def count_cells(out_directory,trialNo,country, extTrial, year_list):
    df = pd.DataFrame()
    for year in year_list:

        path = out_directory + '/{0}_{1}/{0}_{1}_{3}/output/AcPerc_{0}_{1}_{2}_reclass.tif'.format(trialNo,country,year, extTrial)

        gdalData = gdal.Open(path)
        if gdalData is None:
            sys.exit( "ERROR: can't open raster" )

        # get width and heights of the raster
        xsize = gdalData.RasterXSize
        ysize = gdalData.RasterYSize

        # get number of bands
        bands = gdalData.RasterCount
        
        # process the raster
        band_i = gdalData.GetRasterBand(1)
        raster = band_i.ReadAsArray()

        # create dictionary for unique values count
        count = {}

        # count unique values for the given band
        for col in range( xsize ):
            for row in range( ysize ):
                cell_value = raster[row, col]
                
                # check if cell_value is NaN
                if math.isnan(cell_value):
                    cell_value = 'Null'

                # add cell_value to dictionary
                try:
                    count[cell_value] += 1
                except:
                    count[cell_value] = 1
        #print(year,count)
    
        count.update({'year':year})
        df = df.append(count,ignore_index=True) 
    
    #print(df.head())
    df.rename({0: 'Other', 1: '<-5', 2: '-5--1', 3: '-1--0.01', 4: '-0.01-0.01',5: '0.01-1', 6: '1-5', 7: '>5'}, axis=1, inplace=True)
    ndf = df.fillna(0)
    #print(ndf.head())

    ndf.set_index('year',inplace=True, drop=True)
    #print(ndf.head())
    #print(df)
    stacked_data = ndf.apply(lambda x: x*100/sum(x), axis=1)
    
    #print(stacked_data.head())
    stacked_data.plot(kind="bar", stacked=True)
    plt.title("Cell Value Error ({0},{1},{2})".format(trialNo,country, extTrial))
    plt.xlabel("Year")
    plt.ylabel("Percentage of Cell Value Error (%)")
    plt.savefig(out_directory + '/{0}_{1}/{0}_{1}_{3}/output/percError_{0}_{1}_{2}.png'.format(trialNo,country,year, extTrial), dpi=300, bbox_inches='tight',) 
    plt.cla()
    plt.close()       
    #plt.show() 
