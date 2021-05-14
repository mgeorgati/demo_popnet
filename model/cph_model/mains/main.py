import tensorflow as tf
import os
from osgeo import gdal
import osr
import sys
import numpy as np
import time

sys.path.append("K:/FUME/popnet/PoPNetV2")

from data_loader.data_generator import DataGenerator, PrepData, PrepTrainTest
from data_loader.data_loader import DataLoader
from models.pop_model import PopModel
from trainers.pop_trainer import PopTrainer
from utils.config import process_config
from utils.dirs import create_dirs
from utils.logger import Logger
from utils.utils import get_args
from configs.pop_example import create_updatedjson
from use_model import use_model

def remove_files(trial_dir,country):
    country_proj = '{}_proj'.format(country)
    destination = trial_dir + '/{}'.format(country_proj) 
    # merged_trial01 takes trial01 with 35Bands
    if not os.path.exists(destination):
        print("------------------------------ Creating folder for ------------------------------")
        os.makedirs(destination)
    else: 
        print("------------------------------ Folder already exists------------------------------")     
    proj_years=[2012,2014,2016,2018]
    for proj_year in proj_years:
        old_path = trial_dir + '/{}/{}.tif'.format(country,proj_year)
        new_path = destination + '/{}.tif'.format(proj_year)
        os.rename(old_path, new_path)
    for fileName in os.listdir(trial_dir + '/{}'.format(country)):

        if fileName.endswith('.txt'):
            old_path = trial_dir + '/{0}/{1}'.format(country,fileName)
            new_path = destination + '/{}'.format(fileName)
            os.rename(old_path, new_path)
            #print(fileName)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_dir = base_dir + '/configs'

countries = [ "EurEUNoL","West_Asia","South_Asia"] 
#"Centr_Asia","East_Asia","EurNotEU", "Latin_Amer", "North_Afr"
# "Latin_America_and_the_Caribbean","Northern_Africa", "Northern_America", "Northern_Europe","Oceania","Southern_Asia","Southern_Europe", "Southern-Eastern_Asia", "Sub-Saharan_Africa", "Western_Asia", "Western_Europe"
#"Eastern_Europe", "Latin_America_and_the_Caribbean",
#countries=[] #,''pol','deu','tur' 'irq','pol','deu','tur'
city="cph"
trialNo = "trial02"
trial_dir = base_dir + '/data/{0}/{1}'.format(city,trialNo)

# ------- CAREFUL HERE !!!! -------
"""for country in os.listdir(trial_dir):
    if not country.endswith('_proj'): 
        countries.append(country)
        remove_files(trial_dir,country) """
        
def run_all():
    for country in countries:
        create_updatedjson(base_dir,config_dir + '/example.json', country, trialNo,city)
        args = get_args()
        #print(args)
        if args.config != 'None':
            config = process_config(args.config)
        else:
            config = process_config(config_dir + '/example.json')

        data_dir = base_dir + '/data/{0}/{1}/{2}'.format(city,trialNo,country)
        #data_dir = base_dir + '/data/{}'.format(config.exp_name)
        
        #print('*****Training: {}*****'.format(country))
        #tf.reset_default_graph()
        #train_model(data_dir,config)
        print('*****Producing outcome: {}*****'.format(country))
        tf.reset_default_graph()
        use_model(data_dir,config)        

def train_model(data_dir,config):
    #Start total preparation time timer
    start_total_algorithm_timer = time.time()
    # capture the config path from the run arguments
    # then process the json configration file
    # try:
    data_loader = DataLoader(data_dir, config)
    
    # Load the tif files in data_dir folder, get their names as integers, get them sorted in ascending order based on year 
    data_loader.load_directory('.tif') 
    data_loader.create_np_arrays()
    data_loader.create_data_label_pairs()

    preptt = PrepTrainTest(config, data_loader)

    for i in range(len(data_loader.data_label_pairs)):
        x_data = data_loader.data_label_pairs[i][0][:, :, :]
        y_true = data_loader.data_label_pairs[i][1][:, :, 0]

        preptt.add_data(x_data, y_true)
    #print(preptt)
    # Create the experiments dirs
    create_dirs([config.summary_dir, config.checkpoint_dir, config.input_dir])

    # Create tensorflow session
    sess = tf.compat.v1.Session()

    # Create instance of the model you want
    model = PopModel(config)

    # Load model if exist
    model.load(sess)

    # Create Tensorboard logger
    logger = Logger(sess, config)
    logger.log_config()

    # Create your data generator
    data = DataGenerator(config, preptraintest = preptt)

    data.create_traintest_data()

    #print(data)
    # Create trainer and path all previous components to it
    trainer = PopTrainer(sess, model, data, config, logger)

    # Train model
    trainer.train()

    # Test model
    
    # stop total algorithm time timer ----------------------------------------------------------------------------------
    stop_total_algorithm_timer = time.time()
    # calculate total runtime
    total_time_elapsed = (stop_total_algorithm_timer - start_total_algorithm_timer)/60
    print("Total preparation time for ... is {} minutes".format( total_time_elapsed))

if __name__ == '__main__':
    run_all()
   