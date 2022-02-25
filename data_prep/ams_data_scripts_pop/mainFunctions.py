import os
import pandas as pd
from sqlalchemy import create_engine
import openpyxl

from variables import engine

#Python get unique values from list using numpy.unique
import numpy as np
# function to get unique values
def unique(list1):
    x = np.array(list1)
    print(np.unique(x))

## ## ## ## ## ----- CREATE NEW FOLDER  ----- ## ## ## ## ##
def createFolder(path):
    if not os.path.exists(path):
        print("------------------------------ Creating Folder : {} ------------------------------".format(path))
        os.makedirs(path)
    else: 
        print("------------------------------ Folder already exists------------------------------")

## ## ## ## ## ----- SAVE DATAFRAME TO EXCEL FILE  ----- ## ## ## ## ##
def dfTOxls(dest_path, fileName, frame):
    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(dest_path + "/{}.xlsx".format(fileName),  index = False, header=True)
    # Convert the dataframe to an XlsxWriter Excel object.
    frame.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

## ## ## ## ## ----- CREATE QUERY IN PROSTGRES AND EXPORT TO EXCEL  ----- ## ## ## ## ##
def sqlTOxls(engine,query,fileName):
    #query = 'SELECT * FROM unsd'
    df = pd.read_sql_query(query,con=engine)
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(dest_path + "/{}.xlsx".format(fileName), index = False, header=True)
    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

import random 
## ## ## ## ## ----- A FUNCTION CREATING RANDOM COLORS  ----- ## ## ## ## ## 
def generate_colors(n): 
  rgb_values = [] 
  hex_values = [] 
  r = int(random.random() * 256) 
  g = int(random.random() * 256) 
  b = int(random.random() * 256) 
  step = 256 / n 
  for _ in range(n): 
    r += 25 #originally all += step
    g += 46 
    b += 125 
    r = int(r) % 256 
    g = int(g) % 256 
    b = int(b) % 256 
    r_hex = hex(r)[2:] 
    g_hex = hex(g)[2:] 
    b_hex = hex(b)[2:] 
    hex_number = "#%02x%02x%02x" % ((r,g,b))
    hex_values.append(hex_number) 
    rgb_values.append((r,g,b)) 
  return  hex_values #rgb_values,

import matplotlib.pyplot as plt
## ## ## ## ## ----- CREATE LINE DIAGRAM FROM DATAFRAME ----- ## ## ## ## ##
def lineDiagram(frame, outputName, n, title, dest_path):
    ax = plt.gca()
    # Shink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # generate values and print them 
    hex_values = generate_colors(len(frame.columns)) 
    lines = [] 
    print(frame.head(3))
    for i, country in enumerate(frame):
        #lines = nframe[i].plot(kind='line', x='Year', y='Population',ax=ax, ylabel='Population', title ='Population Change of Migrant Groups (1992-2018)', color='green')  
        axes = frame[country].plot.line(color={ "{}".format(country): "{}".format(hex_values[i])}, title= "{}".format(title))
    plt.xlabel("Year")
    plt.ylabel("Population")    
    plt.legend(bbox_to_anchor=(1.3,0.5), loc='center', borderaxespad=0., fontsize=5)
    plt.savefig(dest_path + '/{}.png'.format(outputName), dpi=300)
    plt.cla()
    plt.close()