import json
from bunch import Bunch
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_config_from_json(json_file):
    """
    Get the config from a json file
    :param json_file:
    :return: config(namespace) or config(dictionary)
    """
    # parse the configurations from the config json file provided
    with open(json_file, 'r') as config_file:
        config_dict = json.load(config_file)

    # convert the dictionary to a namespace using bunch lib
    config = Bunch(config_dict)
    
    return config, config_dict


def process_config(jsonfile):
    config, _ = get_config_from_json(jsonfile)

    config.summary_dir = os.path.join(os.path.sep, base_dir, "experiments", config.city,config.trial_name,config.exp_name, config.sub_exp, "summary")
    config.checkpoint_dir = os.path.join(os.path.sep, base_dir, "experiments", config.city, config.trial_name,config.exp_name, config.sub_exp, "checkpoints/")
    config.output_dir = os.path.join(os.path.sep, base_dir, "experiments",  config.city, config.trial_name,config.exp_name, config.sub_exp, "output")
    config.output_pred_dir = os.path.join(os.path.sep, base_dir, "experiments",  config.city, config.trial_name,config.exp_name, config.sub_exp, "outputs", "predictions")
    config.output_dif_dir = os.path.join(os.path.sep, base_dir, "experiments",  config.city, config.trial_name, config.exp_name, config.sub_exp, "outputs", "difference")
    config.output_eval_dir = os.path.join(os.path.sep, base_dir, "experiments",  config.city,config.trial_name,config.exp_name, config.sub_exp, "outputs", "evaluation")
    config.output_bbox_dir = os.path.join(os.path.sep, base_dir, "experiments", config.city, config.trial_name, config.exp_name, config.sub_exp, "outputs", "bbox")
    config.input_dir = os.path.join(os.path.sep, base_dir, "experiments",  config.city, config.trial_name,config.exp_name, config.sub_exp, "inputs")

    return config
    #print(config)