import os 
from multiprocessing import Process


def startTensorboard(tf_log_dir):
  os.system('o:/projekter/PY000014_D/popnet_env/Scripts/tensorboard.exe --logdir="'+ tf_log_dir + '" --host localhost --port 6006')


def print_tensorboard(directory,trialNo, base_dir, countries):
    for country in countries:
        path = directory + "/{0}_{1}".format(trialNo,country)
        #extTrials=[] #'CV_00','CV_01'
        extTrials=['CV_00','CV_01'] #'CV_00','CV_01'
        for k in os.listdir(path):
            extTrial= k.split("{0}_{1}_".format(trialNo,country))[1]
            print(extTrial)
            extTrials.append(extTrial)
            
        for extTrial in extTrials:
             
            logdir="K:/FUME/popnet/PoPNetV2/experiments/{0}_{1}/{0}_{1}_{2}/summary/".format(trialNo,country,  extTrial)
            print(logdir)
            #startTensorboard(logdir)

tf_log_dir = "K:/FUME/popnet/PoPNetV2/experiments/trial03_Northern_Africa/trial03_Northern_Africa_CV_00/summary/"
