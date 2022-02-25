import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches
import rasterio 
import rasterio.plot
import numpy as np
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(base_dir)
sys.path.append(base_dir)
from plot_map import plot_map

#Set filepath
cph = base_dir + "/cph_ProjectData/AncillaryData/CaseStudy/GreaterCopenhagen.gpkg"
regions = base_dir + "/cph_ProjectData/AncillaryData/CaseStudy/regioner.gpkg"
waterPath= base_dir + "/cph_ProjectData/AncillaryData/temp_tif/cph_water_cover.tif"

categories= {'pop':['L1','L11','L12','L13a','L18','L19','L20','P'],
                'age': ['L2','L3','L4','L5', 'L6'],
                'mig': ['L7','L8','L9'],
                'migCountry': ['L10'],
                'migInOut': ['L14', 'L15', 'L16', 'L17'],
                'dwelling': ['L21','L22','L23', 'L24']
}

def createMaps(importPath, exportPath, year, categories ):
    for key in categories.values():
        for category in key:
            for file in os.listdir(importPath):
                if file.endswith('.tif') and file.startswith('{0}_{1}'.format(year, category)) : #and not file.startswith('{}_L10'.format(year))
                    fileName= file.split('.tif')[0].split('{}_'.format(year))[1]
                    #print(fileName)
                    with rasterio.open('{0}/{1}'.format(importPath, file)) as src: 
                        pop = src.read(1)
                        #print(np.min(pop),np.max(pop)) 
                        hist=np.asarray(np.histogram(pop, bins=5, density=True))
                
                        valMax = np.round(np.max(pop), 2)
                        valMin = np.round(np.min(pop), 2)
                        total = np.sum(pop)
                        if valMax == 1 and not file.startswith('{0}_L10'.format(year)):                             
                            val=0.10   
                            valmid1 = 0.30
                            valmid2 = 0.50
                            valmid3 = 0.70
                            valmid4 = 0.90
                            valmid5 = 1.00
                            plot_map(cph,regions,waterPath, src,exportPath, year, valMin, val, valmid1, valmid2, valmid3, valmid4,valmid5, valMax, fileName)
                        
                        if total>2000 and valMax > 1 and valMax<300:                             
                            val=5   
                            valmid1 = 20
                            valmid2 = 50
                            valmid3 = 100
                            valmid4 = 150
                            if valMax > 220:
                                valmid5 = valMax
                            else:
                                valmid5 = 220
                            plot_map(cph,regions,waterPath, src,exportPath, year, valMin, val, valmid1, valmid2, valmid3, valmid4,valmid5, valMax, fileName)
                        
                        if total>2000 and valMax > 1 and valMax>300 and valMax<30000:                             
                            val= 20   
                            valmid1 = 100
                            valmid2 = 400
                            valmid3 = 800
                            valmid4 = 1200
                            if valMax> 1500:
                                valmid5 = valMax
                            else:
                                valmid5 = 1500
                            plot_map(cph,regions,waterPath, src,exportPath, year, valMin, val, valmid1, valmid2, valmid3, valmid4,valmid5, valMax, fileName)
           
                        if valMax>30000:                            
                            val=50   
                            valmid1 = 5000
                            valmid2 = 10000
                            valmid3 = 15000
                            valmid4 = 20000
                            if valMax > 30000:
                                valmid5 = valMax
                            else:
                                valmid5 = 30000
                            plot_map(cph,regions,waterPath, src,exportPath, year, valMin, val, valmid1, valmid2, valmid3, valmid4,valmid5, valMax, fileName)          
           
years = [1998]#1992, 1994, 1996, 1998,2000, 2002,2004,2006, 2008,2010,2012, 2014,2016, 2018
for year in years:
    #importPath="K:/FUME/popnet/PoPNetV2/data_scripts/cph_ProjectData/MigGeogrGroups"
    #exportPath = 'K:/FUME/popnet/PoPNetV2/data_scripts/cph_ProjectData/MigGeogrGroups/temp_png'

    importPath="K:/FUME/popnet/PoPNetV2/data_scripts/cph_ProjectData/PopData/{}/temp_tif".format(year)
    exportPath = "K:/FUME/popnet/PoPNetV2/data_scripts/cph_ProjectData/PopData/{}/temp_png".format(year)
    createMaps(importPath, exportPath, year, categories)
    