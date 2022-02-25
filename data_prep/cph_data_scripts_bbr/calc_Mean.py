import numpy as np
import sys, os, rasterio as rs
path= "C:/FUME/DasymetricMapping/SDis_Self-Training"
sys.path.append(path)
import osgeoutils as osgu

ancillary_path = "C:/FUME/PopNetV2/data_prep/cph_ProjectData/temp_tif/"
typeBBR = [ 'housing' ] # 'constryear'
for i in typeBBR:
    ancdataset1, rastergeo = osgu.readRaster(os.path.join(ancillary_path, 'cph_{0}/2002_{0}.tif'.format(i)))
    ancdataset2 = osgu.readRaster(os.path.join(ancillary_path, 'cph_{0}/2004_{0}.tif'.format(i)))[0]
    ancdataset3 = osgu.readRaster(os.path.join(ancillary_path, 'cph_{0}/2006_{0}.tif'.format(i)))[0]

    ancdataset4 = osgu.readRaster(os.path.join(ancillary_path, 'cph_{0}/2008_{0}.tif'.format(i)))[0]

    ancdataset5 = osgu.readRaster(os.path.join(ancillary_path, 'cph_{0}/2010_{0}.tif'.format(i)))[0]
    ancdataset6 = osgu.readRaster(os.path.join(ancillary_path, 'cph_{0}/2012_{0}.tif'.format(i)))[0]

    ancdataset7 = osgu.readRaster(os.path.join(ancillary_path, 'cph_{0}/2014_{0}.tif'.format(i)))[0]

    ancdataset8 = osgu.readRaster(os.path.join(ancillary_path, 'cph_{0}/2016_{0}.tif'.format(i)))[0]

    ancdataset9 = osgu.readRaster(os.path.join(ancillary_path, 'cph_{0}/2018_{0}.tif'.format(i)))[0]
    ancdataset10 = osgu.readRaster(os.path.join(ancillary_path, 'cph_{0}/2020_{0}.tif'.format(i)))[0]

    ancdatasets = np.dstack((ancdataset5,ancdataset6, ancdataset7, ancdataset8,ancdataset9,ancdataset10)) #ancdataset1, ancdataset2, ancdataset3, ancdataset4,  
    #ancdatasets[ancdatasets == 0] = np.nan
    print(ancdatasets.shape)
    meanArray = ancdatasets.mean(axis=2)
    #meanArray= np.nan_to_num(meanArray, nan=0, posinf= 0, neginf= 0)
    print('- Writing raster to disk...')
    osgu.writeRaster(meanArray[:,:], rastergeo, ancillary_path + 'bbr_{0}_mean.tif'.format(i))#