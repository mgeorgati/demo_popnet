import os
import subprocess
import fnmatch
import rasterio
import rasterio.plot
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

#Merge all files by year of question
def mergeAoI(ancillary_data_folder_path,ancillary_POPdata_folder_path,folder_path,city,mergedFolder,python_scripts_folder_path,year,AoI,
                demo_age,demo_ng,demo_se, buildings, transport, corine, home_prices):
    #Create list of year with geographical areas, append socio-economic and then infrastructure 
     
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    #print(listOfFiles)
    listFiles = []
    first_path = os.path.dirname(ancillary_POPdata_folder_path)  + "/GeogrGroups_sel\\{0}\\{1}_{0}.tif".format(AoI, year) #totalMig_
    listFiles.append(first_path)
    for x in listOfFiles:
        if x==first_path:
            listOfFiles.remove(x)
            
    for k in listOfFiles:   
        fileName=k.split('\\')[-1] 
        if fileName.endswith('.tif') and fileName.startswith('{}_'.format(year)): 
            listFiles.append(k)
    
    #Now add the DNK
    for file in os.listdir(ancillary_POPdata_folder_path + '/{}/temp_tif/countries'.format(year)):
        if file.endswith('_dnk.tif') and file.startswith('{0}_'.format(year)) :#
            path = Path("{0}/{1}/temp_tif/countries/{2}".format(ancillary_POPdata_folder_path, year, file))
            listFiles.append(path)
    
    # Now get the rest of the sociodemographic data
    #indicators = ['l2','l3','l4','l5','l6','l18','l19','l20', 'l21','l22', 'l23','l24' ] #
    indicators = []
    # L2-L6 : 5 age groups
    if demo_age == "yes":
        age_indicators = ['l2','l3','l4','l5','l6']
        indicators.extend(age_indicators)
    
    # L11 : Births, L12 : Deaths
    # L13a : Marriages,male 
    if demo_ng == "yes":
        ng_indicators = ['l11','l12','l13a']
        indicators.extend(ng_indicators)   
    
    # L18 : High Education
    # L19 : Share Rich , L20 : Share Poor
    if demo_se == "yes":
        se_indicators = ['l18','l19_p_rich','l20_p_poor']
        indicators.extend(se_indicators) 
    
    # Buildings :
    # L21 : notused , L22 : rented, L23: Private, L24: public
    if buildings == "yes":
        bl_indicators = ['l21','l22','l23','l24']
        indicators.extend(bl_indicators) 
    
    print(indicators)
    for i in indicators:
        for file in os.listdir(ancillary_POPdata_folder_path + '/{}/temp_tif/demo'.format(year)):
            if file.endswith('.tif') and file.startswith('{0}_{1}_'.format(year,i)) :
                path = Path("{0}/{1}/temp_tif/demo/{2}".format(ancillary_POPdata_folder_path, year, file))
                listFiles.append(path)
    
    #Now add to that list the infrastructure
    if transport == "yes":                
        for file in os.listdir(ancillary_data_folder_path + '/temp_tif'):
            #Add files for busses and trains
            if file.endswith('.tif') and file.startswith('{}_'.format(year)):
                path = Path("{0}/temp_tif/{1}".format(ancillary_data_folder_path , file))
                listFiles.append(path)
    
    #Get Corine data     
    if corine == "yes":   
        if year <= 2000:
            pathUF = Path("{0}/temp_tif/corine/urbfabr_{1}_CLC_1990_2000.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathUF)
            pathAG = Path("{0}/temp_tif/corine/agric_{1}_CLC_1990_2000.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathAG)
            pathFOR = Path("{0}/temp_tif/corine/greenSpaces_{1}_CLC_1990_2000.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathFOR)
            pathInd = Path("{0}/temp_tif/corine/industry_{1}_CLC_1990_2000.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathInd)
            pathtransp = Path("{0}/temp_tif/corine/transp_{1}_CLC_1990_2000.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathtransp)
            pathWater = Path("{0}/temp_tif/corine/waterComb_{1}_CLC_1990_2000.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathWater)
        elif year <= 2006 and year > 2000 :
            pathUF = Path("{0}/temp_tif/corine/urbfabr_{1}_CLC_2000_2006.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathUF)
            pathAG = Path("{0}/temp_tif/corine/agric_{1}_CLC_2000_2006.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathAG)
            pathFOR = Path("{0}/temp_tif/corine/greenSpaces_{1}_CLC_2000_2006.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathFOR)
            pathInd = Path("{0}/temp_tif/corine/industry_{1}_CLC_2000_2006.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathInd)
            pathtransp = Path("{0}/temp_tif/corine/transp_{1}_CLC_2000_2006.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathtransp)
            pathWater = Path("{0}/temp_tif/corine/waterComb_{1}_CLC_2000_2006.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathWater)
        elif year <= 2012 and year > 2006 :
            pathUF = Path("{0}/temp_tif/corine/urbfabr_{1}_CLC_2006_2012.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathUF)
            pathAG = Path("{0}/temp_tif/corine/agric_{1}_CLC_2006_2012.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathAG)
            pathFOR = Path("{0}/temp_tif/corine/greenSpaces_{1}_CLC_2006_2012.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathFOR)
            pathInd = Path("{0}/temp_tif/corine/industry_{1}_CLC_2006_2012.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathInd)
            pathtransp = Path("{0}/temp_tif/corine/transp_{1}_CLC_2006_2012.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathtransp)
            pathWater = Path("{0}/temp_tif/corine/waterComb_{1}_CLC_2006_2012.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathWater)
        elif year <= 2020 and year > 2012 :
            pathUF = Path("{0}/temp_tif/corine/urbfabr_{1}_CLC_2012_2018.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathUF)
            pathAG = Path("{0}/temp_tif/corine/agric_{1}_CLC_2012_2018.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathAG)
            pathFOR = Path("{0}/temp_tif/corine/greenSpaces_{1}_CLC_2012_2018.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathFOR)
            pathInd = Path("{0}/temp_tif/corine/industry_{1}_CLC_2012_2018.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathInd)
            pathtransp = Path("{0}/temp_tif/corine/transp_{1}_CLC_2012_2018.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathtransp)
            pathWater = Path("{0}/temp_tif/corine/waterComb_{1}_CLC_2012_2018.tif".format(ancillary_data_folder_path,city))
            listFiles.append(pathWater)

    #Now add to that list the infrastructure
    if home_prices == "yes":                
        for file in os.listdir(ancillary_data_folder_path + '/temp_tif'):
            #Add files for busses and trains
            if file.endswith('.tif') and file.startswith('{}_'.format(year)):
                path = Path("{0}/temp_tif/{1}".format(ancillary_data_folder_path , file))
                listFiles.append(path)
    
    outfile =  mergedFolder + "/{1}.tif".format(AoI, year)
        
    #Create txt file with number of band --> Name of File
    f = open(mergedFolder + "/{0}_{1}_bandList.txt".format(year,AoI), "w+")
    str_files = " ".join(["{}".format(listFiles[i]) for i in range(len(listFiles))])
    for i,each in enumerate(listFiles,start=1):
        f.write("{}.{}".format(i,each))
        #print ("{}.{}".format(i,each))
    f.close()
        
    # Clear the list for the next loop
    listFiles.clear()
        
    #Write the merged tif file 
    cmd_tif_merge = "python {0}/gdal_merge.py -o {1} -separate {2} ".format(python_scripts_folder_path, outfile, str_files)
    print(cmd_tif_merge)
    subprocess.call(cmd_tif_merge, shell=False)
    
    
