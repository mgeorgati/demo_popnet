import os
import sys
import geopandas as gpd
import rasterio
#import pdfkit 

sys.path.append(os.path.abspath(__file__))
from viz_Input import vizInput

from calc_AcPercentage import calc_dif, calc_AcPerc, viz_AcPerc, makeLineDiagrams
from stats import reclassify, count_cells
from vizResultsMatrix import viz4x3Matrix
from make_diary import makeDiary, makeDiaryByCountry

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(base_dir)
#Set filepath
cph = base_dir + "/data_scripts/cph_ProjectData/AncillaryData/CaseStudy/GreaterCopenhagen.gpkg"
regions = base_dir + "/data_scripts/cph_ProjectData/AncillaryData/CaseStudy/regioner.gpkg"
waterPath= base_dir + "/data_scripts/cph_ProjectData/AncillaryData/temp_tif/cph_water_cover.tif"
#parkPath= base_dir + "/data_scripts/cph_ProjectData/AncillaryData/temp_tif/cph_water_cover.tif"

cph_area = gpd.read_file(cph)
regioner = gpd.read_file(regions) 
waterTif = rasterio.open(waterPath) 

# 1. Create matrixes of input Layers for trial number
city="cph"
trialNo="trial03"
area="Eastern_Europe"
year=2010
input_directory= base_dir + "/data/{0}/{1}/{2}.tif".format(trialNo, area, year)
txt_path= base_dir + "/summarizeResults/bandLists/{0}_{1}_{2}_bandList.txt".format(trialNo,year, area)

#vizInput(input_directory, txt_path, trialNo, base_dir, cph_area,regioner, waterPath)

# 2. Create matrixes of output of model
out_directory = base_dir + "/experiments/{0}/{1}".format(city,trialNo)
countries=[]

for i in os.listdir(out_directory):
    #print(i)
    if i.startswith('{}'.format(trialNo)):
        country=i.split("{}_".format(trialNo))[1]
        countries.append(country)

#vizOutput(out_directory, trialNo, base_dir, cph_area,regioner, waterPath, countries)
#vizOutput_Proj(out_directory, trialNo, base_dir, cph_area,regioner, waterPath,countries)

year_list=[2012,2014,2016,2018]
def main(countries, year_list):
    for country in countries:
        #country=countries[i]
        path = out_directory + "/{0}_{1}".format(trialNo,country)
        extTrials=[]
        for k in os.listdir(path):
            extTrial= k.split("{0}_{1}_".format(trialNo,country))[1]
            extTrials.append(extTrial)

        for extTrial in extTrials:
            Ac_Perc_paths=[]
            """for year in year_list:
                
                #1 Calculate the difference real-projection
                print('----- Calculating the difference real-projection {0},{1},{2}-----'.format(year,country,extTrials))
                calc_dif(out_directory,trialNo,country,year,extTrial,city, base_dir)
                
                #2 Calculate the signicance level of error (e= Di*(Di-Fi)/SDi)
                print('----- Calculating the signicance level of error {0},{1},{2}-----'.format(year,country,extTrials))
                calc_AcPerc(out_directory,trialNo,country,year, extTrial,city, base_dir)
                
                Ac_Perc_path= out_directory + '/{0}_{1}/{0}_{1}_{3}/output/AcPerc_{0}_{1}_{2}.tif'.format(trialNo,country,year, extTrial)
                Ac_Perc_paths.append(Ac_Perc_path)
            
            print('----- {0},{1} -----'.format(country,extTrials))
            #3 Make 2x2 plot showing the error by cell %
            print('----- Making 2x2 plot showing the error by cell % -----')
            viz_AcPerc(trialNo, base_dir, cph_area, regioner, waterTif, country, Ac_Perc_paths, extTrial,city)
            
            #4 Make line diagram of historical values,ground truth and projections
            print('----- Making line diagram of historical values,ground truth and projections -----')
            makeLineDiagrams(trialNo, base_dir, country, extTrial,city)
            
            # 5. Count Cells by error
            print('----- Reclassifying the signicance level of error -----')
            reclassify(out_directory,trialNo,country, extTrial, year_list)
            print('----- Counting cells by signicance of error -----')
            count_cells(out_directory,trialNo,country, extTrial, year_list)
            """
            # 6. Create matrix plot for real data, prediction and their difference
            print('----- Create matrix plot for real data, prediction and their difference -----')
            viz4x3Matrix(out_directory,year_list, trialNo, extTrial, base_dir, cph_area,regioner, waterPath,country,city)

#main(countries, year_list)

# 3. Create Summary table (html file) 
print('----- Making Summary table/diary -----')
makeDiary(out_directory, trialNo, base_dir,countries,city) 

#makeDiaryByCountry(out_directory, trialNo, base_dir, countries)