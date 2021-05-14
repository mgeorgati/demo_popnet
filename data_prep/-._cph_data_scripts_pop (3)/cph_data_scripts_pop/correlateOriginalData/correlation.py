import os 
import pandas as pd
import geopandas as gpd
import numpy as np

import seaborn as sn
import matplotlib.pyplot as plt

city='cph'
ancillary_POPdata_folder_path = "K:/FUME/popnet/PoPNetV2/data_scripts/{}_Projectdata/PopData".format(city)
#js_path= "K:/FUME/popnet/PoPNetV2/data_scripts/cph_Projectdata/PopData/1990/temp_shp/"
# Load point data
#js = gpd.read_file(js_path+'L10_PopCOO.shp')
#js1 = gpd.read_file(js_path+'L13a_Marriages_Male.shp')
#df  = js.merge(js1.iloc[:,0: 2], on='GC100m', how='left')

cor_path= "K:/FUME/popnet/PoPNetV2/data_scripts/cph_Projectdata/PopData/correlations"
def calc_cor(ancillary_POPdata_folder_path, year):
    
    # Load point data
    js = gpd.read_file(ancillary_POPdata_folder_path + '/{}/temp_shp/L10_PopCOO.shp'.format(year))
    js= js.iloc[:, :-3]
    dataframe_list=[js]
    # Now get the rest of the sociodemographic data
    for file in os.listdir(ancillary_POPdata_folder_path + '/{}/temp_shp'.format(year)):
        # L2-L6 : 5 age groups
        # L11 : Births, L12 : Deaths
        # L13a : Marriages,male 
        # L18 : High Education
        # L19 : Share Rich , L20 : Share Poor
        indicators = ['L2','L3','L4','L5','L6','L11','L12','L13a', 'L18','L19','L20' ]
        for i in indicators:
            if file.endswith('.shp') and file.startswith('{0}_'.format(i)) and not file.endswith('NEWINCOME.shp'):
                #print(file)
                ks = gpd.read_file(ancillary_POPdata_folder_path + '/{0}/temp_shp/{1}'.format(year, file))
                dataframe_list.append(ks)
    
    df_merged = pd.concat(dataframe_list)
                 
    cor = df_merged.corr(method='pearson')
    cor = cor.replace(np.nan, 0)
    print(cor)
    sn.heatmap(cor, annot=True)
    plt.show()  
    #cor.to_csv(cor_path + "/{}_cor.csv".format(year))

      
    
years = [1990, 1992]
for year in years:
    print()
    calc_cor(ancillary_POPdata_folder_path, year)

def find_cor(cor_path):
    df= pd.read_csv(cor_path + '/1990_cor.csv')
    
    df= df.iloc[:, 1:]
    print(df)
    df[df>0.1]
#find_cor(cor_path)