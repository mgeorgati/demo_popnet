def create_Maps(importPath, exportPath, year):
    for file in os.listdir(importPath):
        if file.endswith('.tif') and file.startswith('{}_L10'.format(year)) and not file.startswith('{}_L27'.format(year)): #and not file.startswith('{}_L10'.format(year))
            fileName= file.split('.tif')[0].split('{}_'.format(year))[1]
            print(fileName)
            with rasterio.open('{}/{}'.format(importPath, file)) as src: 
            
                pop = src.read(1)
                print(np.min(pop),np.max(pop)) 
                hist=np.asarray(np.histogram(pop, bins=5, density=True))
                values = hist[1]
                a= np.round(values, decimals=2)
                print(a)
                
                valMax = np.round(np.max(pop), 2)
                valMin = np.round(np.min(pop), 2)
                total = np.sum(pop)
                if total>2000:
                    if valMax>20 and valMax < 30 :
                        val=5
                        valmid1= 10 
                        valmid2= 15 
                        valmid3= 20 
                        valmid4= np.round(valMax-((valMax-30)/2), 2)
                        plot_map(src,exportPath, year,valMin,val, valmid1, valmid2, valmid3, valmid4, valMax, fileName)
                    
                    if valMax >= 30 and valMax < 100:
                        val=5
                        valmid1= 10 
                        valmid2= 20 
                        valmid3= 30 
                        valmid4= np.round(valMax-((valMax-30)/2), 2) 
                        plot_mapB(src,exportPath, year,valMin,val, valmid1, valmid2, valmid3, valmid4, valMax, fileName)

                    if valMax >= 100 and valMax < 350 :
                        valmid1 = 20
                        valmid2 = 40
                        valmid3 = 60
                        valmid4 = 80
                        plot_mapB(src,exportPath, year,valMin, valmid1, valmid2, valmid3, valmid4, valMax, fileName)
                    
                    if valMax >= 350 :
                        valmid1 = 50
                        valmid2 = 100
                        valmid3 = 200
                        valmid4 = np.round(valMax-((valMax-200)/2), 2)
                        plot_mapB(src,exportPath, year,valMin, valmid1, valmid2, valmid3, valmid4, valMax, fileName)

def create_MapsMig(importPath, exportPath, year):
    for file in os.listdir(importPath):
        if file.endswith('.tif') and file.startswith('{}_'.format(year)) and not file.startswith('{}_L27'.format(year)): #and not file.startswith('{}_L10'.format(year))
            fileName= file.split('.tif')[0].split('{}_'.format(year))[1]
            print(fileName)
            with rasterio.open('{}/{}'.format(importPath, file)) as src: 
            
                pop = src.read(1)
                print(np.min(pop),np.max(pop)) 
                hist=np.asarray(np.histogram(pop, bins=5, density=True))
                values = hist[1]
                a= np.round(values, decimals=2)
                print(a)
                
                valMax = np.round(np.max(pop), 2)
                valMin = np.round(np.min(pop), 2)
                total = np.sum(pop)
                if valMax == 1.00  :
                        val = valMin
                        valmid1= 0.20
                        valmid2= 0.40
                        valmid3= 0.60
                        valmid4= 0.80
                        plot_map(src,exportPath, year,valMin,val, valmid1, valmid2, valmid3, valmid4, valMax, fileName)

                if total>2000 :
                    valmid1 = 20
                    valmid2 = 40
                    valmid3 = 60
                    valmid4 = 80
                    if valMax > 100:
                        valmid5 =valMax
                        plot_mapB(src,exportPath, year,valMin, valmid1, valmid2, valmid3, valmid4, valmid5, valMax, fileName)
                    else:
                        valmid5 = 100
                        plot_mapB(src,exportPath, year,valMin, valmid1, valmid2, valmid3, valmid4, valmid5, valMax, fileName)
