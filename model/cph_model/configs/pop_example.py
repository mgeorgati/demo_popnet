import json
import rasterio
import numpy as np
import os
import sys
from pathlib import Path

def calc_pop_proj(path):
    src = rasterio.open(path)
    df= src.read(1)
    pop=np.sum(df)
    return(pop)

def create_updatedjson(base_dir,config_dir, country, trialNo,city):
    proj_years=[2012,2014,2016,2018]
    proj_list=[]
    country_proj = '{}_proj'.format(country)
    
    for year in proj_years:
        
        for file in os.listdir(base_dir + '/data/{0}/{1}/{2}'.format(city,trialNo,country_proj)):
            if file.endswith('{}.tif'.format(year)):
                path = Path(base_dir + '/data/{0}/{1}/{2}/{3}'.format(city, trialNo,country_proj,file))
                print(path)
                proj_list.append(calc_pop_proj(path))
    print(proj_list)

    # python object to be appended 
    y = {"city":"{0}".format(city),
        "trial_name" :"{0}".format(trialNo),
            "exp_name": "{0}_{1}".format(trialNo,country), 
            "exp_name_train": "{0}_{1}".format(trialNo,country), 
            "sub_exp": "{0}_{1}_CV_01".format(trialNo,country),
            "num_epochs": 60, 
            "learning_rate": 0.001, 
            "batch_size": 16, 
            "max_to_keep": 5, 
            "chunk_height": 32, 
            "chunk_width": 32, 
            "feature_list": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1  ,  1, 1, 1, 1, 1, 1, 1, 1  ],  #, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 #, 1, 1, 1, 1, 1, 1, 1, 1 #, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1  #, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0
            "feature_values": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  ,  0, 0, 100, 0, 0, 0, 0, 0 ], #, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0  # , 0, 0, 100, 0, 0, 0, 0, 0 #, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 0 #, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 100, 999, 999
            "num_outputs": 4, 
            "train_size": 0.8, 
            "test_size": 0.2, 
            "cost_cell": 0.5, 
            "cost_chunk": 0.5, 
            "bbox": [4456400, 3608600, 4497100, 3636700],  
            "pop_proj": proj_list
            } 
    
    with open(config_dir, "r+") as f:
    #Update to JSON
        json_data = json.load(f)
        #print (json_data.values()) # View Previous entries
        json_data.update(y)
        print (json_data.values())

    with open(config_dir, 'w') as f:
        f.write(json.dumps(json_data))
    y.clear()