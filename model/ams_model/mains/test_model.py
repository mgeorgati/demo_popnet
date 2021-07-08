import tensorflow as tf
import os
from osgeo import gdal
import osr
import sys
import numpy as np

sys.path.append("K:/FUME/popnet/PoPNetV2")

from data_loader.data_generator import DataGenerator, PrepData, PrepTrainTest
from data_loader.data_loader import DataLoader
from models.pop_model import PopModel
from trainers.pop_trainer import PopTrainer
from utils.config import process_config
from utils.dirs import create_dirs
from utils.logger import Logger
from utils.utils import get_args

#base_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(base_dir)
#config_dir = os.path.relpath('..\\configs', base_dir)

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#onlyfiles = [f for f in os.listdir(base_dir) if os.path.isfile(os.path.join(base_dir, f))]
print(base_dir)
#sys.path.append(base_dir)
config_dir = base_dir + '/configs'
print(config_dir)
trialNo ="trial02"
country="Western_Asia"

def main():
    # capture the config path from the run arguments
    # then process the json configration file
    # try:
    args = get_args()
    if args.config != 'None':
        config = process_config(args.config)
    else:
        #config = process_config(os.path.join(config_dir, '/config.json'))
        config = process_config(config_dir + '/example.json')
    #data_dir = os.path.relpath('/data/{}'.format(config.exp_name), base_dir)
    data_dir = base_dir + '/data/{0}/{1}'.format(trialNo,country)
    #print(data_dir)

    data_loader = DataLoader(data_dir,config)
    data_loader.load_directory('.tif')
    data_loader.create_np_arrays()
    #print(data_loader.arrays[0], data_loader.arrays[2])

    preptt = PrepTrainTest(config, data_loader)
    prepd = PrepData(config, data_loader)

    # create the experiments dirs
    create_dirs([config.summary_dir, config.checkpoint_dir])
    # create tensorflow session
    sess = tf.Session()
    # create instance of the model you want
    model = PopModel(config)
    #load model if exist
    model.load(sess)
    # create your data generator
    data = DataGenerator(config, preptt, prepd)

    data.create_traintest_data()
    data.create_data()

    # Create Tensorboard logger
    logger = Logger(sess, config)

    # Create trainer and path all previous components to it
    tester = PopTrainer(sess, model, data, config, logger)

    # Test model
    tester.test()


if __name__ == '__main__':
    tf.reset_default_graph()
    main()