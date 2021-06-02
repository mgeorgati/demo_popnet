from qgis.analysis import QgsZonalStatistics
#specify polygon shapefile vector
polygonLayer = QgsVectorLayer('C:/Users/NM12LQ/OneDrive - Aalborg Universitet/PopNetV2/data_prep/ams_ProjectData/AncillaryData/adm/neighborhood.geojson', 'neighborhood', "ogr") 
#Remove the standard columns from the unique Attributes and write file
select = ['Oceania', 'EuropeNotEU', 'EuropeEUnoLocal',  'Central_Asia', 'Eastern_Asia', 'Southern-Eastern_Asia', 'Southern_Asia', 
'Western_Asia', 'Northern_America', 'Latin_America_and_the_Caribbean', 'Northern_Africa', 'Sub-Saharan_Africa', 'Others', 'Colonies'] #'l1_totalpop', 'totalMig',
for i in select:
    # specify raster filename
    rasterFilePath =  QgsRasterLayer('C:/Users/NM12LQ/OneDrive - Aalborg Universitet/PopNetV2/data_prep/ams_ProjectData/PopData/2018/temp_tif/2018_Z0_{}.tif'.format(i), 'mylayer')
    polygonLayer.startEditing() 
    # usage - QgsZonalStatistics (QgsVectorLayer *polygonLayer, const QString &rasterFile, const QString &attributePrefix="", int rasterBand=1)
    zoneStat = QgsZonalStatistics (polygonLayer, rasterFilePath, 'Z0_{}'.format(i), 1, QgsZonalStatistics.Mean)
    print(zoneStat)
    zoneStat.calculateStatistics(None)
    polygonLayer.commitChanges()
