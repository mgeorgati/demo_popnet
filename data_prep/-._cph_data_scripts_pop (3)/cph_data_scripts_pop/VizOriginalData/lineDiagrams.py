import os
import numpy as np
import pandas as pd
import rasterio 
import matplotlib.pyplot as plt
import seaborn as sns
import mapclassify as mc

city='cph'
ancillary_POPdata_folder_path = "K:/FUME/popnet/PoPNetV2/data_scripts/{}_Projectdata/PopData".format(city)
image_path= "K:/FUME/popnet/PoPNetV2/data_scripts/cph_Projectdata/images"

path= "K:/FUME/popnet/PoPNetV2/data_scripts/cph_ProjectData/GeogrGroupsRevised"
AoIs=[]
years =[]
for AoI in os.listdir(path):
    #print(AoI)
    AoIs.append(AoI)
df = pd.DataFrame(columns=AoIs)

for AoI in AoIs:
    AoI_path = path + "/{}".format(AoI) 
    for file in os.listdir(AoI_path):
        if file.endswith('.tif') :
            #print(file)
            year = file.split('_')[0]
            years.append(year)
            src = rasterio.open(AoI_path + '/' + file)
            array = src.read(1)
            pop = np.sum(array)
            df.at[year, '{}'.format(AoI)] = pop
            #print(year,AoI, pop)
df.index.name = "year"
exclude = ['Denmark']
df.loc[:, df.columns.difference(exclude)].plot(kind="line", title= "Change of Migrant Populations")
plt.xlabel("Year")
plt.ylabel("Population")
#plt.savefig(image_path + '/PopChangeMigrantGroups.png', dpi=300, bbox_inches='tight', transparent=True) #{0}_{1}/{0}_{1}_{2}/output
plt.show()
plt.cla()
plt.close()   

for year in years:
    df.loc['{}'.format(year), df.columns.difference(exclude)].plot(kind="bar", title= "Population of Migrant Groups ({})".format(year))
    plt.xlabel("Region of origin")
    plt.ylabel("Population")
    plt.savefig(image_path + '/revisedGroups/migrantgroups_{}.png'.format(year), dpi=300, bbox_inches='tight', transparent=True) #{0}_{1}/{0}_{1}_{2}/output
    #plt.show()
    plt.cla()
    plt.close()            