To start you need:
    1. A database city_data  

    2. The following folders/files:
        2.1. folder city_ProjectData with: 
            2.1.1 AncillaryData: For Infrastructure
                ams_ProjectData/AncillaryData/
                ams_ProjectData/AncillaryData/adm/districts
                ams_ProjectData/AncillaryData/adm/neighborhoods
                ams_ProjectData/AncillaryData/railways/trammetro2018 (tram lines)
                ams_ProjectData/AncillaryData/railways/trammetrost2018 (tram stops)


            2.1.2 PopData: For Population
                ams_ProjectData/PopData/rawData

        2.2. A folder for European data:
            euroData
                /ref-nuts-2021-01m/NUTS_RG_01M_2021_3035_LEVL_3/NUTS_RG_01M_2021_3035_LEVL_3.shp
                /corine/CLC_1990_2000.tif 
                /corine/CLC_2000_2006.tif 
                /corine/CLC_2006_2012.tif 
                /corine/CLC_2012_2018.tif        

    3. Scripts
        3.1. city_data_scripts_infra: scripts for loading data in database, process it and export to tif 
            (see more in folderDescription.txt: main -> process -> others)

        3.2. city_data_scripts_pop: scripts for converting excel to shp and tif, aggregate countries to region 
            (see more in folderDescription.txt: main -> process -> others)

________________________
Directories Automatically generated
    ams_ProjectData/temp_shp, which contains necessary shp files of case study
    ams_ProjectData/temp_tif, which contains necessary tif files of case study 
    ams_ProjectData/GeogrGroups, which contains tif files of populations summed by regions

    ams_ProjectData/PopData/year/temp_shp
    ams_ProjectData/PopData/year/temp_tif

Other folders/files
    