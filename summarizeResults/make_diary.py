import pandas as pd
import os
import rasterio
import numpy as np
from IPython.core.display import display,HTML

def path_to_image_html(path):
    return '<img src="'+ path + '" height="500" />'
def path_to_diagram_html(path):
    return '<object data="'+ path + '" width="500" height="500"> </object> '

def makeDiary(directory, trialNo, base_dir, countries,city): 
    # your images
    images = [] 
    error_images=[]
    diagrams=[]
    comp_diagrams =[]
    accDiag=[]
    config_data=[]
    for country in countries:
        path = directory + "/{0}_{1}".format(trialNo,country)
        extTrials=[]
        for k in os.listdir(path):
            extTrial= k.split("{0}_{1}_".format(trialNo,country))[1]
            extTrials.append(extTrial)
        
        for extTrial in extTrials:
                    
            image_path = directory + '/{0}_{1}/{0}_{1}_{2}/output/comp_{0}_{1}.png'.format(trialNo,country, extTrial)
            images.append(image_path)
            error_image_path = directory + '/{0}_{1}/{0}_{1}_{2}/output/ErrorPerc_{0}_{1}.png'.format(trialNo,country, extTrial)
            error_images.append(error_image_path)
            diagram_path = directory +'/{0}_{1}/{0}_{1}_{2}/output/abs_loss_1.svg'.format(trialNo,country, extTrial)
            diagrams.append(diagram_path)
            comp_diagram_path = directory +'/{0}_{1}/{0}_{1}_{2}/output/pred_gtruth_comparison.png'.format(trialNo,country, extTrial)
            comp_diagrams.append(comp_diagram_path)
            accDiag_path = directory + '/{0}_{1}/{0}_{1}_{2}/output/percError_{0}_{1}_2018.png'.format(trialNo,country, extTrial)
            accDiag.append(accDiag_path)
            #print(image_path)
            config = open(directory + '/{0}_{1}/{0}_{1}_{2}/config.txt'.format(trialNo,country, extTrial)).read()
            lines_of_config = config.splitlines()
            id = lines_of_config[0].split(":")[-1]
            sub = lines_of_config[1].split(":")[-1]
            epochs = lines_of_config[2].split(":")[-1]
            lrate = lines_of_config[3].split(":")[-1]
            batch = lines_of_config[4].split(":")[-1]
            chunk = lines_of_config[6].split(":")[-1]

            data = open(directory + '/{0}_{1}/{0}_{1}_{2}/output/log.txt'.format(trialNo,country, extTrial)).read()
            
            lines_of_data = data.splitlines()
            min12 = lines_of_data[1].split(":")[-1]
            max12 = lines_of_data[2].split(":")[-1]
            sum12 = lines_of_data[3].split(":")[-1]
            min14 = lines_of_data[6].split(":")[-1]
            max14 = lines_of_data[7].split(":")[-1]
            sum14 = lines_of_data[8].split(":")[-1]
            min16 = lines_of_data[11].split(":")[-1]
            max16 = lines_of_data[12].split(":")[-1]
            sum16 = lines_of_data[13].split(":")[-1]
            min18 = lines_of_data[16].split(":")[-1]
            max18 = lines_of_data[17].split(":")[-1]
            sum18 = lines_of_data[18].split(":")[-1]
            src12 = rasterio.open(base_dir + '/data/{0}/{1}/{2}_proj/2012.tif'.format(city,trialNo,country))
            src14 = rasterio.open(base_dir + '/data/{0}/{1}/{2}_proj/2014.tif'.format(city,trialNo,country))
            src16 = rasterio.open(base_dir + '/data/{0}/{1}/{2}_proj/2016.tif'.format(city,trialNo,country))
            src18 = rasterio.open(base_dir + '/data/{0}/{1}/{2}_proj/2018.tif'.format(city,trialNo,country))
            array12 = src12.read(1)
            array14 = src14.read(1)
            array16 = src16.read(1)
            array18 = src18.read(1)
            sum_pop12= np.sum(array12)
            sum_pop14= np.sum(array14)
            sum_pop16= np.sum(array16)
            sum_pop18= np.sum(array18)

            config_data.append([id,sub,epochs,lrate,batch,chunk]) #,min12,max12,sum12,sum_pop12,min14,max14,sum14,sum_pop14,min16,max16,sum16,sum_pop16, min18,max18,sum18,sum_pop18

    df = pd.DataFrame(config_data, columns= ['id','sub','epochs','l_rate','batch','chunk']) #, 'min12', 'max12','sum12','realSum12','min14','max14','sum14','realSum14','min16','max16','sum16','realSum16','min18','max18','sum18','realSum18'
    
    html_images=[]
    html_error_images=[]
    html_diagrams=[]
    html_comp_diagrams=[]
    html_accDiag=[]
    def iteration(list, html_list):
        for i in list:
            src= path_to_image_html(i)
            html_list.append(src)
        return html_list
    print(diagrams)
    iteration(images, html_images)
    iteration(error_images, html_error_images)
    iteration(comp_diagrams, html_comp_diagrams)
    iteration(accDiag, html_accDiag)
    
    for k in diagrams:
        srcK= path_to_diagram_html(k)
        html_diagrams.append(srcK)
        
    df['error'] = html_error_images
    df['Loss_diagram'] = html_diagrams
    df['Comparison'] = html_comp_diagrams
    df['Cell Error'] = html_accDiag
    #df['image'] = html_images
    # convert your links to html tags 
    pd.set_option('display.max_colwidth', None)
    #print(dict(image=path_to_image_html))
    #display(HTML(df.to_html(escape=False ,formatters=dict(image=path_to_image_html))))
    #data_df.to_csv('K:/FUME/popnet/PoPNetV2/experiments/test.csv')
    df.to_html(base_dir + '/summarizeResults/summaryTables/{}.html'.format(trialNo), escape=False)

def iteration(list, html_list):
    for i in list:
        src= path_to_image_html(i)
        html_list.append(src)
    return html_list

from itertools import groupby

def makeDiaryByCountry(directory, trialNo, base_dir, countries): 
    path =os.path.dirname(directory)
    folder_names = []
    for entry_name in os.listdir(path):
        entry_path = os.path.join(path, entry_name)
        for i in os.listdir(entry_path):
            country= i.split('_',1)[1]
            entry_pathI = os.path.join(entry_path, i)
            #print(entry_pathI,country)
            if os.path.isdir(entry_pathI):
                folder_names.append(country)
    names_list = ['Northern_Africa', 'Northern_Europe']#list(set(folder_names))
    #print() 
    my_dirs =[]
    
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(path):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
  
    for k in names_list:
        error_images=[]
        diagrams=[]
        comp_diagrams =[]
        for i in listOfFiles:
            if ("{}".format(k) in i) and ("output" in i)  and ("ErrorPerc" in i) and i.endswith('.png'):
                error_images.append(i)  
            elif ("{}".format(k) in i) and ("output" in i) and i.endswith('abs_loss_1.svg'):
                diagrams.append(i)
        print(diagrams, error_images)
            


    """

        if ("{}".format(k) in mydir) and not("outputs" in mydir):
                my_dirs.append(mydir) 
    
    for file in os.listdir(mydir):
                        #print(file)
                        if file.endswith('.png') and ("ErrorPerc" in file) :
                            error_image_path = mydir + '/{}'.format(file)
                            print(error_image_path)
                            error_images.append(error_image_path)
                        elif file.endswith('abs_loss_1.svg') :
                            diagram_path = mydir + '/{}'.format(file)
                            diagrams.append(diagram_path)
            print(error_images)
        for i in files:
            mypath = os.path.join(root,file)
        print(dirs,files)
        
        for k in names_list:
            for a_dir in dirs:
                if ("{}".format(k) in a_dir) and ("_CV" in a_dir):
                    mydir = os.path.join(root,a_dir)
                    #print (mydir)
                    
                    
                    print(error_images)
                    print(diagrams)
                    df = pd.DataFrame()  
                
                    html_error_images=[]
                    html_diagrams=[]

                    iteration(error_images, html_error_images)

                    for l in diagrams:
                        srcK= path_to_diagram_html(l)
                        html_diagrams.append(srcK)
                        
                    df['error'] = html_error_images
                    df['Loss_diagram'] = html_diagrams
                    
                    # convert your links to html tags 
                    pd.set_option('display.max_colwidth', None)
                    df.to_html(base_dir + '/summarizeResults/summaryTables/{}.html'.format(k), escape=False) 
    
        # your images
    images = [] 
    error_images=[]
    diagrams=[]
    comp_diagrams =[]
    accDiag=[]
    config_data=[]
    for country in countries:
        path = directory + "/{0}_{1}".format(trialNo,country)
        extTrials=[]
        for k in os.listdir(path):
            extTrial= k.split("{0}_{1}_".format(trialNo,country))[1]
            extTrials.append(extTrial)
        
        for extTrial in extTrials:
                    
            image_path = directory + '/{0}_{1}/{0}_{1}_{2}/output/comp_{0}_{1}.png'.format(trialNo,country, extTrial)
            images.append(image_path)
            error_image_path = directory + '/{0}_{1}/{0}_{1}_{2}/output/ErrorPerc_{0}_{1}.png'.format(trialNo,country, extTrial)
            error_images.append(error_image_path)
            diagram_path = directory +'/{0}_{1}/{0}_{1}_{2}/output/abs_loss_1.svg'.format(trialNo,country, extTrial)
            diagrams.append(diagram_path)
            comp_diagram_path = directory +'/{0}_{1}/{0}_{1}_{2}/output/pred_gtruth_comparison.png'.format(trialNo,country, extTrial)
            comp_diagrams.append(comp_diagram_path)
            accDiag_path = directory + '/{0}_{1}/{0}_{1}_{2}/output/percError_{0}_{1}_2018.png'.format(trialNo,country, extTrial)
            accDiag.append(accDiag_path)
            #print(image_path)
            config = open(directory + '/{0}_{1}/{0}_{1}_{2}/config.txt'.format(trialNo,country, extTrial)).read()
            lines_of_config = config.splitlines()
            id = lines_of_config[0].split(":")[-1]
            sub = lines_of_config[1].split(":")[-1]
            epochs = lines_of_config[2].split(":")[-1]
            lrate = lines_of_config[3].split(":")[-1]
            batch = lines_of_config[4].split(":")[-1]
            chunk = lines_of_config[6].split(":")[-1]

            data = open(directory + '/{0}_{1}/{0}_{1}_{2}/output/log.txt'.format(trialNo,country, extTrial)).read()
            
            lines_of_data = data.splitlines()
            min12 = lines_of_data[1].split(":")[-1]
            max12 = lines_of_data[2].split(":")[-1]
            sum12 = lines_of_data[3].split(":")[-1]
            min14 = lines_of_data[6].split(":")[-1]
            max14 = lines_of_data[7].split(":")[-1]
            sum14 = lines_of_data[8].split(":")[-1]
            min16 = lines_of_data[11].split(":")[-1]
            max16 = lines_of_data[12].split(":")[-1]
            sum16 = lines_of_data[13].split(":")[-1]
            min18 = lines_of_data[16].split(":")[-1]
            max18 = lines_of_data[17].split(":")[-1]
            sum18 = lines_of_data[18].split(":")[-1]
            src12 = rasterio.open(base_dir + '/data/{0}/{1}_proj/2012.tif'.format(trialNo,country))
            src14 = rasterio.open(base_dir + '/data/{0}/{1}_proj/2014.tif'.format(trialNo,country))
            src16 = rasterio.open(base_dir + '/data/{0}/{1}_proj/2016.tif'.format(trialNo,country))
            src18 = rasterio.open(base_dir + '/data/{0}/{1}_proj/2018.tif'.format(trialNo,country))
            array12 = src12.read(1)
            array14 = src14.read(1)
            array16 = src16.read(1)
            array18 = src18.read(1)
            sum_pop12= np.sum(array12)
            sum_pop14= np.sum(array14)
            sum_pop16= np.sum(array16)
            sum_pop18= np.sum(array18)

            config_data.append([id,sub,epochs,lrate,batch,chunk]) #,min12,max12,sum12,sum_pop12,min14,max14,sum14,sum_pop14,min16,max16,sum16,sum_pop16, min18,max18,sum18,sum_pop18

    df = pd.DataFrame(config_data, columns= ['id','sub','epochs','l_rate','batch','chunk']) #, 'min12', 'max12','sum12','realSum12','min14','max14','sum14','realSum14','min16','max16','sum16','realSum16','min18','max18','sum18','realSum18'
    
    html_images=[]
    html_error_images=[]
    html_diagrams=[]
    html_comp_diagrams=[]
    html_accDiag=[]
    def iteration(list, html_list):
        for i in list:
            src= path_to_image_html(i)
            html_list.append(src)
        return html_list
    print(diagrams)
    iteration(images, html_images)
    iteration(error_images, html_error_images)
    iteration(comp_diagrams, html_comp_diagrams)
    iteration(accDiag, html_accDiag)
    
    for k in diagrams:
        srcK= path_to_diagram_html(k)
        html_diagrams.append(srcK)
        
    df['error'] = html_error_images
    df['Loss_diagram'] = html_diagrams
    df['Comparison'] = html_comp_diagrams
    df['Cell Error'] = html_accDiag
    df['image'] = html_images
    # convert your links to html tags 
    pd.set_option('display.max_colwidth', None)
    #print(dict(image=path_to_image_html))
    #display(HTML(df.to_html(escape=False ,formatters=dict(image=path_to_image_html))))
    #data_df.to_csv('K:/FUME/popnet/PoPNetV2/experiments/test.csv')
    df.to_html(base_dir + '/summarizeResults/summaryTables/{}.html'.format(trialNo), escape=False)"""