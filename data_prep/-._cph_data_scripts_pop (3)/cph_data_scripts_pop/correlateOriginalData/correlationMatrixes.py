import os 
import pandas as pd
import geopandas as gpd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline

city='cph'
years = [1990,1992, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018] #1990,1992, 1994, 1996, 1998, 2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018
cor_path= "K:/FUME/popnet/PoPNetV2/data_scripts/cph_Projectdata/correlations"
ancillary_POPdata_folder_path = "K:/FUME/popnet/PoPNetV2/data_scripts/{}_Projectdata/PopData".format(city)

#Calculate correlations among regions of origin
def calc_cor(ancillary_POPdata_folder_path, year):
    # Load point data
    js = gpd.read_file(ancillary_POPdata_folder_path + '/{}/temp_shp/L10_PopCOO.shp'.format(year))
    js= js.iloc[:, :-3]
    #print(js)
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
                ks = ks.iloc[:,0: 2]
                dataframe_list.append(ks)
    
    df_merged = pd.concat(dataframe_list)
    print(df_merged.columns)             
    #cor = df_merged.corr(method='pearson')
    correlation_mat = df_merged.corr(method='pearson')
    kot = correlation_mat[correlation_mat>=.3]
    plt.figure(figsize=(100,100))
    sns.heatmap(kot, cmap="twilight")

    plt.title("Correlation matrix of Migrants by Country of origin, {}".format(year),fontsize=100)
    plt.xlabel("Country of Origin", fontsize=60)
    plt.ylabel("Country of Origin", fontsize=60)
    #plt.xticks(fontsize=20, rotation=0)
    plt.yticks(fontsize=40, rotation=0)
    #plt.savefig(cor_path + "/{}_cor_Matrix.png".format(year), dpi=300)
    plt.show()  
    #correlation_mat.to_csv(cor_path + "/{}_cor.csv".format(year))