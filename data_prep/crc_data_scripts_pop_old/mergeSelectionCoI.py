import os
import subprocess
import fnmatch
import rasterio
import rasterio.plot
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

def sumUpTifsByGeographicalRegion(ancillary_data_folder_path,ancillary_POPdata_folder_path,city,year,save_path, country_dict):
    for key in country_dict:
        pop_list=[]
        for value in country_dict[key]:
            for file in os.listdir(ancillary_POPdata_folder_path + '/{}/temp_tif'.format(year)):
                path = Path("{0}/{1}/temp_tif/{2}".format(ancillary_POPdata_folder_path,year,file))
                if file.endswith('{}.tif'.format(value.upper())) and file.startswith('{}_'.format(year)) and path.exists() and not file.startswith('{}_totalPop'.format(year)) and not file.startswith('{}_MigPop'.format(year)):
                    pop_list.append(path)
        #print(key, pop_list)
        total_pop = 0
        for i in range(len(pop_list)): 
            #print(pop_list[i])
            
            src = rasterio.open(pop_list[i]) 
            pop = src.read(1)
            total_pop += pop
        
        with rasterio.open(ancillary_POPdata_folder_path + "/{0}/temp_tif/{0}_totalPop.tif".format(year)) as dd:

            new_dataset = rasterio.open(
                '{0}/{1}_{2}.tif'.format(save_path,year,key),
                'w',
                driver='GTiff',
                height=total_pop.shape[0],
                width=total_pop.shape[1],
                count=1,
                dtype=total_pop.dtype,
                crs=dd.crs,
                transform= dd.transform
            )
        new_dataset.write(total_pop, 1)
        new_dataset.close()               

def sumUpTifsByGeogrRegionCoI(ancillary_data_folder_path,ancillary_POPdata_folder_path,city,year,temp_path, country_dict, CoI):

    pop_list=[]
    for key in country_dict:
        for value in country_dict[key]:
            for file in os.listdir(ancillary_POPdata_folder_path + '/{}/temp_tif'.format(year)):
                path = Path("{0}/{1}/temp_tif/{2}".format(ancillary_POPdata_folder_path,year,file))
                if file.endswith('{}.tif'.format(value.upper())) and file.startswith('{}_L10'.format(year)) and path.exists():
                    pop_list.append(path)
        print(key,CoI, pop_list)
        total_pop = 0
        for i in range(len(pop_list)):             
            src = rasterio.open(pop_list[i]) 
            pop = src.read(1)
            total_pop += pop
        print(total_pop.max())
        #print(total_pop)
        with rasterio.open("{0}/1990/temp_tif/1990_L1_SUM_POP.tif".format(ancillary_POPdata_folder_path,city)) as dd:
            new_dataset = rasterio.open(
                '{0}/{1}_{2}_totalMig_{3}.tif'.format(temp_path,year,CoI,key),
                'w',
                driver='GTiff',
                height=total_pop.shape[0],
                width=total_pop.shape[1],
                count=1,
                dtype=total_pop.dtype,
                crs=dd.crs,
                transform= dd.transform
            )
        new_dataset.write(total_pop, 1)
        new_dataset.close()  
        pop_list.clear()
  
#Merge all files by year of question
def mergeCoI(ancillary_data_folder_path,ancillary_POPdata_folder_path,mergedFinal00,city,year,temp_path,python_scripts_folder_path,CoI):
    #Create list of year with geographical areas, append socio-economic and then infrastructure
    listFiles = []
    path = Path("{0}/{1}/temp_tif/{1}_L10_{2}.tif".format(ancillary_POPdata_folder_path,year, CoI.upper()))
    listFiles.append(path)
    # Get the migration data
    for file in os.listdir(temp_path):
        if file.endswith('.tif') and file.startswith('{}_'.format(year)):
            print(file)
            path = Path("{0}/{1}".format(temp_path,file))
            listFiles.append(path)
                
    # Now get the rest of the sociodemographic data
    # L2-L6 : 5 age groups
    # L11 : Births, L12 : Deaths
    # L13a : Marriages,male 
    # L18 : High Education
    # L19 : Share Rich , L20 : Share Poor
    indicators = ['L2','L3','L4','L5','L6','L11','L12','L13a', 'L18','L19','L20' ]
    for i in indicators:
        for file in os.listdir(ancillary_POPdata_folder_path + '/{}/temp_tif'.format(year)):
            if file.startswith('{0}_{1}_'.format(year,i)) and not file.endswith('NEWINCOME.tif') :#
                path = Path("{0}/{1}/temp_tif/{2}".format(ancillary_POPdata_folder_path, year, file))
                listFiles.append(path)
                    
    #Now add to that list the infrastructure
    for file in os.listdir(ancillary_data_folder_path + '/temp_tif'):
        #Add files for busses and trains
        if file.startswith('{}_'.format(year)):
            path = Path("{0}/temp_tif/{1}".format(ancillary_data_folder_path , file))
            listFiles.append(path)
        if file.startswith('{}_water'.format(city)):
            path = Path("{0}/temp_tif/{1}".format(ancillary_data_folder_path , file))
            listFiles.append(path)
        
    #Get Corine data (2bands included)
    if year <= 2000:
        path = Path("{0}/temp_tif/cph_U2000_CLC1990_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2006 and year > 2000 :
        path = Path("{0}/temp_tif/cph_U2006_CLC2000_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2012 and year > 2006 :
        path = Path("{0}/temp_tif/cph_U2012_CLC2006_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2020 and year > 2012 :
        path = Path("{0}/temp_tif/cph_U2018_CLC2012_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
        
    outfile =  mergedFinal00 + "/{0}.tif".format(year)
        
    #Create txt file with number of band --> Name of File
    f = open(temp_path + "/{0}_{1}_bandList.txt".format(year,CoI), "w+")
    str_files = " ".join(["{}".format(listFiles[i]) for i in range(len(listFiles))])
    for i,each in enumerate(listFiles,start=1):
        f.write("{}.{}".format(i,each))
        #print ("{}.{}".format(i,each))
    f.close()
        
    # Clear the list for the next loop
    listFiles.clear()
        
    #Write the merged tif file 
    cmd_tif_merge = "python {0}/gdal_merge.py -o {1} -separate {2} ".format(python_scripts_folder_path, outfile, str_files)
    #print(cmd_tif_merge)
    subprocess.call(cmd_tif_merge, shell=False)

#Merge all files by year of question
def mergeAoI(ancillary_data_folder_path,ancillary_POPdata_folder_path,folder_path,city,mergedFinal02,python_scripts_folder_path,year,AoI):
    #Create list of year with geographical areas, append socio-economic and then infrastructure 
     
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    #print(listOfFiles)
    listFiles = []
    first_path = folder_path +"\\{0}\\{1}_totalMig_{0}.tif".format(AoI, year)
    listFiles.append(first_path)
    for x in listOfFiles:
        if x==first_path:
            listOfFiles.remove(x)
            
    for k in listOfFiles:   
        fileName=k.split('\\')[-1] 
        if fileName.endswith('.tif') and fileName.startswith('{}_'.format(year)) and not fileName.endswith('Northern Europe.tif'): 
            listFiles.append(k)
    # Now get the rest of the sociodemographic data
    # L2-L6 : 5 age groups
    # L11 : Births, L12 : Deaths
    # L13a : Marriages,male 
    # L18 : High Education
    # L19 : Share Rich , L20 : Share Poor
    indicators = ['L2','L3','L4','L5','L6','L11','L12','L13a', 'L18','L19','L20' ]
    for i in indicators:
        for file in os.listdir(ancillary_POPdata_folder_path + '/{}/temp_tif'.format(year)):
            if file.startswith('{0}_{1}_'.format(year,i)) and not file.endswith('NEWINCOME.tif') :#
                path = Path("{0}/{1}/temp_tif/{2}".format(ancillary_POPdata_folder_path, year, file))
                listFiles.append(path)
                    
    #Now add to that list the infrastructure
    for file in os.listdir(ancillary_data_folder_path + '/temp_tif'):
        #Add files for busses and trains
        if file.startswith('{}_'.format(year)):
            path = Path("{0}/temp_tif/{1}".format(ancillary_data_folder_path , file))
            listFiles.append(path)
        if file.startswith('{}_water'.format(city)):
            path = Path("{0}/temp_tif/{1}".format(ancillary_data_folder_path , file))
            listFiles.append(path)
        
    #Get Corine data (2bands included)
    if year <= 2000:
        path = Path("{0}/temp_tif/cph_U2000_CLC1990_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2006 and year > 2000 :
        path = Path("{0}/temp_tif/cph_U2006_CLC2000_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2012 and year > 2006 :
        path = Path("{0}/temp_tif/cph_U2012_CLC2006_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2020 and year > 2012 :
        path = Path("{0}/temp_tif/cph_U2018_CLC2012_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
        
    outfile =  mergedFinal02 + "/{0}/{1}.tif".format(AoI, year)
        
    #Create txt file with number of band --> Name of File
    f = open(mergedFinal02 + "/{1}/{0}_{1}_bandList.txt".format(year,AoI), "w+")
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

#Merge all files by year of question
def mergeAoI3(ancillary_data_folder_path,ancillary_POPdata_folder_path,folder_path,city,mergedFinal03,python_scripts_folder_path,year,AoI):
    #Create list of year with geographical areas, append socio-economic and then infrastructure 
     
    # Get the list of all files in directory tree at given path
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    #print(listOfFiles)
    listFiles = []
    first_path = folder_path +"\\{0}\\{1}_totalMig_{0}.tif".format(AoI, year)
    listFiles.append(first_path)
    for x in listOfFiles:
        if x==first_path:
            listOfFiles.remove(x)
            
    for k in listOfFiles:   
        fileName=k.split('\\')[-1] 
        if fileName.endswith('.tif') and fileName.startswith('{}_'.format(year)): 
            listFiles.append(k)
    #Now add the DNK
    for file in os.listdir(ancillary_POPdata_folder_path + '/{}/temp_tif'.format(year)):
        if file.endswith('_DNK.tif') and file.startswith('{0}_'.format(year)) :#
            path = Path("{0}/{1}/temp_tif/{2}".format(ancillary_POPdata_folder_path, year, file))
            listFiles.append(path)

    
    # Now get the rest of the sociodemographic data
    # L2-L6 : 5 age groups
    # L11 : Births, L12 : Deaths
    # L13a : Marriages,male 
    # L18 : High Education
    # L19 : Share Rich , L20 : Share Poor
    """indicators = ['L2','L3','L4','L5','L6','L11','L12','L13a', 'L18','L19','L20', 'L21','L22', 'L23','L24','P' ]
    for i in indicators:
        for file in os.listdir(ancillary_POPdata_folder_path + '/{}/temp_tif'.format(year)):
            if file.endswith('.tif') and file.startswith('{0}_{1}_'.format(year,i)) and not file.endswith('NEWINCOME.tif') :#
                path = Path("{0}/{1}/temp_tif/{2}".format(ancillary_POPdata_folder_path, year, file))
                listFiles.append(path)"""
                    
    #Now add to that list the infrastructure
    for file in os.listdir(ancillary_data_folder_path + '/temp_tif'):
        #Add files for busses and trains
        if file.endswith('.tif') and file.startswith('{}_'.format(year)):
            path = Path("{0}/temp_tif/{1}".format(ancillary_data_folder_path , file))
            listFiles.append(path)
        if file.endswith('.tif') and file.startswith('{}_water'.format(city)):
            path = Path("{0}/temp_tif/{1}".format(ancillary_data_folder_path , file))
            listFiles.append(path)
        
    #Get Corine data (2bands included)
    if year <= 2000:
        path = Path("{0}/temp_tif/cph_U2000_CLC1990_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2006 and year > 2000 :
        path = Path("{0}/temp_tif/cph_U2006_CLC2000_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2012 and year > 2006 :
        path = Path("{0}/temp_tif/cph_U2012_CLC2006_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2020 and year > 2012 :
        path = Path("{0}/temp_tif/cph_U2018_CLC2012_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
        
    outfile =  mergedFinal03 + "/{0}/{1}.tif".format(AoI, year)
        
    #Create txt file with number of band --> Name of File
    f = open(mergedFinal03 + "/{1}/{0}_{1}_bandList.txt".format(year,AoI), "w+")
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
    
    

   

"""path = Path(os.path.dirname(ancillary_POPdata_folder_path) + "/GeogrGroups/{1}/{0}_totalMig_{1}.tif".format(year, AoI))
    listFiles.append(path)
    # Get the migration data
    for file in os.listdir(temp_path):
        if file.endswith('.tif') and file.startswith('{}_'.format(year)):
            print(file)
            path = Path("{0}/{1}".format(temp_path,file))
            listFiles.append(path)
                
    # Now get the rest of the sociodemographic data
    # L2-L6 : 5 age groups
    # L11 : Births, L12 : Deaths
    # L13a : Marriages,male 
    # L18 : High Education
    # L19 : Share Rich , L20 : Share Poor
    indicators = ['L2','L3','L4','L5','L6','L11','L12','L13a', 'L18','L19','L20' ]
    for i in indicators:
        for file in os.listdir(ancillary_POPdata_folder_path + '/{}/temp_tif'.format(year)):
            if file.startswith('{0}_{1}_'.format(year,i)) and not file.endswith('NEWINCOME.tif') :#
                path = Path("{0}/{1}/temp_tif/{2}".format(ancillary_POPdata_folder_path, year, file))
                listFiles.append(path)
                    
    #Now add to that list the infrastructure
    for file in os.listdir(ancillary_data_folder_path + '/temp_tif'):
        #Add files for busses and trains
        if file.startswith('{}_'.format(year)):
            path = Path("{0}/temp_tif/{1}".format(ancillary_data_folder_path , file))
            listFiles.append(path)
        if file.startswith('{}_water'.format(city)):
            path = Path("{0}/temp_tif/{1}".format(ancillary_data_folder_path , file))
            listFiles.append(path)
        
    #Get Corine data (2bands included)
    if year <= 2000:
        path = Path("{0}/temp_tif/cph_U2000_CLC1990_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2006 and year > 2000 :
        path = Path("{0}/temp_tif/cph_U2006_CLC2000_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2012 and year > 2006 :
        path = Path("{0}/temp_tif/cph_U2012_CLC2006_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
    elif year <= 2020 and year > 2012 :
        path = Path("{0}/temp_tif/cph_U2018_CLC2012_V2020_20u1.tif".format(ancillary_data_folder_path ))
        listFiles.append(path)
        
    outfile =  mergedFinal00 + "/{0}.tif".format(year)
        
    #Create txt file with number of band --> Name of File
    f = open(temp_path + "/{0}_{1}_bandList.txt".format(year,CoI), "w+")
    str_files = " ".join(["{}".format(listFiles[i]) for i in range(len(listFiles))])
    for i,each in enumerate(listFiles,start=1):
        f.write("{}.{}".format(i,each))
        #print ("{}.{}".format(i,each))
    f.close()
        
    # Clear the list for the next loop
    listFiles.clear()
        
    #Write the merged tif file 
    cmd_tif_merge = "python {0}/gdal_merge.py -o {1} -separate {2} ".format(python_scripts_folder_path, outfile, str_files)
    #print(cmd_tif_merge)
    subprocess.call(cmd_tif_merge, shell=False)"""

    ######################################OLDER
"""def sumUpTifsByGeographicalRegion_old(ancillary_data_folder_path,ancillary_POPdata_folder_path,city,year,save_path, country_dict):
    pop_list=[]
    for key in country_dict:
        for value in country_dict[key]:
            for file in os.listdir(ancillary_POPdata_folder_path + '/{}/temp_tif'.format(year)):
                path = Path("{0}/{1}/temp_tif/{2}".format(ancillary_POPdata_folder_path,year,file))
                
                if file.endswith('{}.tif'.format(value.upper())) and file.startswith('{}_L10'.format(year)) and path.exists():
                    #print(file)
                    with rasterio.open('{0}/{1}/temp_tif/{2}'.format(ancillary_POPdata_folder_path,year, file)) as src:
                        pop = src.read(1)
                        p1 = src.crs
                        height = src.shape[0],
                        width= src.shape[1],
                        bb= src.transform,
                        pop_list.append(pop)

        total_pop=np.add.reduce(pop_list)
        print(key, pop_list, total_pop)

        with rasterio.open('{0}/1990/temp_tif/1990_L1_SUM_POP.tif'.format(ancillary_POPdata_folder_path,city)) as dd:

            new_dataset = rasterio.open(
                '{0}/{2}/{1}_totalMig_{2}.tif'.format(save_path,year,key),
                'w',
                driver='GTiff',
                height=total_pop.shape[0],
                width=total_pop.shape[1],
                count=1,
                dtype=total_pop.dtype,
                crs=p1,
                transform= dd.transform
            )
        new_dataset.write(total_pop, 1)
        new_dataset.close()
"""
