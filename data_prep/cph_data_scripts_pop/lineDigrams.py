# A function creating random colors
import os
import numpy as np
import pandas as pd
import geopandas as gpd
import openpyxl
import matplotlib.pyplot as plt
import random 

city="cph"
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(base_dir)
# Paths for the Population Data --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path = base_dir + "/data_prep/{}_Projectdata/AncillaryData".format(city)
ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_Projectdata/PopData".format(city)
image_path= base_dir + "/data_prep/{}_Projectdata/PopData/images".format(city)
years_list=[1992,1994,1996,1998,2000,2002,2004,2006,2008,2010,2012,2014,2016,2018]

df_Afr = pd.read_excel(base_dir + '/data_prep/{}_Projectdata/Visualizations/EXCEL/EXCEL/PopChangeCountry_Africa.xlsx'.format(city))
# find the index position of maximum
# values in every column
maxValueIndex = df_Afr.idxmax(axis = 1)
print(maxValueIndex)

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

def gen_plot(image_path, name):  
  ax = plt.gca()
  # Shink current axis by 20%
  box = ax.get_position()
  ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
  # generate values and print them 
  hex_values = generate_colors(len(L_select)) 
  lines = [] 
  for i, country in enumerate(lframe):
      #lines = nframe[i].plot(kind='line', x='Year', y='Population',ax=ax, ylabel='Population', title ='Population Change of Migrant Groups (1992-2018)', color='green')  
      axes = nframe[country].plot.line(color={ "{}".format(country): "{}".format(hex_values[i])})
  plt.legend(bbox_to_anchor=(1.3,0.5), loc='center', borderaxespad=0., fontsize=7)
  plt.savefig(image_path + '/{}.png'.format(name), dpi=300)
  plt.show()