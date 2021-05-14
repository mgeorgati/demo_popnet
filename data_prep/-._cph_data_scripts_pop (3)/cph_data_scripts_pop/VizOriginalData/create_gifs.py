import os
import imageio
base_dir =  'K:/FUME/popnet/PoPNetV2/data_scripts/cph_ProjectData/PopData'
years = [1990,1992, 1994, 1996, 1998,2000, 2002,2004,2006, 2008,2010,2012, 2014,2016, 2018] #1992, 1994, 1996, 1998,2000, 2002,2004,2006, 2008,2010,2012, 2014,2016, 2018
png_dir = base_dir + "/2018/temp_png/"

fileNames=[]
for year in years:
    for file in os.listdir(png_dir):
        if file.endswith('.png'):
            fileName = file.split('{}_'.format(year))[-1]
            fileNames.append(fileName)
#print(fileNames)

for i in fileNames:
    iName=i.split('{}_'.format(year))[-1].split('.png')[0]
    #print(iName)
    images = []
    try:
        for year in years:
            #iName=i.split('.png')[0].split('{}_'.format(year))[-1]        
            image = base_dir + "/{0}/temp_png/{0}_{1}.png".format(year,iName)
            images.append(imageio.imread(image))
            print(images)
    except OSError:
        continue
    imageio.mimsave(os.path.dirname(base_dir) + '/gifsRawData/gif_{}.gif'.format(iName), images, fps=24, duration=1)


